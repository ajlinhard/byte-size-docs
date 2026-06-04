import os
import tempfile
import requests
import urllib3
import sys
from datetime import datetime, timezone
from env_config import set_env_variables
from jwt_handler import JwtHandler # JWR-setup.py
import json
import boto3
from typing import Optional

# Suppress SSL warnings for testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ApiClient:
    """
    VA API Client for making authenticated requests to VA endpoints
    Supports both real API calls and mock responses for testing
    """

    def __init__(self, context=None, db_handler=None):
        """
        Initialize the VA API client

        Args:
            context: Lambda context object (optional, for environment detection)
            db_handler: DatabaseHandler instance (optional, for API metrics logging)
        """
        self.context = context
        self.db_handler = db_handler
        self.secrets = set_env_variables(context)

        # Endpoint configurations
        self.endpoint_configs = {
            "claims": {
                "url": self.secrets["secrets"].get("HOST_URL_CLAIMS"),
                "jwt_secret": "JWT_SECRET_CLAIMS",
                "issuer": self.secrets["secrets"].get("ISSUER"),
            },
            "claims_evidence": {
                "url": self.secrets["secrets"].get("HOST_URL_CLAIMS_EVIDENCE"),
                "jwt_secret": "JWT_SECRET_CLAIMS_EVIDENCE",
                "issuer": "AICES",
            },
            "military_history": {
                "url": self.secrets["secrets"].get("HOST_URL_MILITARY_HISTORY"),
                "jwt_secret": "JWT_SECRET_MILITARY_HISTORY",
                "issuer": self.secrets["secrets"].get("ISSUER"),
            },
        }

    def _parse_json_response(self, response_data, content_type=None):
        """
        Parse response data as JSON if it's a string and content type is JSON

        Args:
            response_data: Response data (string or dict)
            content_type: Content type header (optional)

        Returns:
            dict or str: Parsed JSON object or original string if parsing fails
        """
        if isinstance(response_data, str):
            # If content type is provided, check if it's JSON
            if content_type and "application/json" in content_type.lower():
                try:
                    return json.loads(response_data)
                except json.JSONDecodeError:
                    return response_data
            # If no content type provided, try to parse as JSON anyway
            elif not content_type:
                try:
                    return json.loads(response_data)
                except json.JSONDecodeError:
                    return response_data
        return response_data

    def _log_api_metrics(self, api_metrics_data):
        """
        Log API metrics to the database using DatabaseHandler

        Args:
            api_metrics_data (dict): API metrics data to log

        Returns:
            bool: True if logging successful, False otherwise
        """
        if not self.db_handler:
            return False

        try:
            from claims_models import ApiMetrics

            with self.db_handler.get_session() as session:
                api_metric = ApiMetrics(**api_metrics_data)
                session.add(api_metric)
                session.flush()

            return True
        except Exception as e:
            print(f"Error logging API metrics: {str(e)}", file=sys.stderr)
            return False

    def make_request(
        self,
        va_api,
        endpoint,
        body=None,
        method="GET",
        claim_id=None,
        batch_id=None,
        batch_type=None,
        ex_headers=None,
    ):
        """
        Make an authenticated request to a VA API endpoint

        Args:
            va_api (str): API type - "claims", "claims_evidence", or "military_history"
            endpoint (str): API endpoint path (e.g., "api/v1/rest/documenttypes")
            body (dict, optional): Request body for POST/PUT requests
            method (str): HTTP method (GET, POST, PUT, etc.)
            claim_id (int, optional): Claim ID for metrics logging
            batch_id (str, optional): Batch ID for metrics logging
            batch_type (str, optional): Batch type for metrics logging
            ex_headers (dict, optional): Extra headers to include in the request

        Returns:
            dict: Response with status_code, data_length, error_response_body, etc.
        """
        # Track request start time for metrics
        requested_at = datetime.now(timezone.utc)

        # Get lambda request ID if available
        lambda_request_id = getattr(self.context, "aws_request_id", None) if self.context else None

        # Mock mode: invoke L-Mock-API lambda instead of real HTTP calls
        if os.environ.get("USE_VA_MOCK") in ("1", "true"):
            return self._invoke_mock_lambda(
                va_api, endpoint, method, body, ex_headers,
                claim_id, batch_id, lambda_request_id, requested_at,
            )

        # Validate VA API type
        if va_api not in self.endpoint_configs:
            return {
                "statusCode": 400,
                "body": {
                    "error": f"Invalid VA_API: {va_api}. Must be one of: {list(self.endpoint_configs.keys())}"
                },
            }

        # Get configuration for the selected API
        config = self.endpoint_configs[va_api]
        API_BASE_URL = config["url"]
        JWT_SECRET_KEY = self.secrets["secrets"].get(config["jwt_secret"])
        ISSUER = config["issuer"]

        USER_ID = self.secrets["secrets"].get("USER_ID")
        STATION_ID = self.secrets["secrets"].get("STATION_ID")

        # Construct full URL
        FULL_URL = f"https://{API_BASE_URL}/{endpoint}"

        # Create JWT token
        jwt_handler = JwtHandler(
            secret_key=JWT_SECRET_KEY,
            issuer=ISSUER,
            user_id=USER_ID,
            station_id=STATION_ID,
            expiration_seconds=3600,
        )

        token = jwt_handler.create_jwt()

        # Prepare certificates
        cert_data = None
        VA_CERT = self.secrets["credentials"].get("cert")
        VA_KEY = self.secrets["credentials"].get("key")

        if VA_CERT and VA_KEY:
            cert_file = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".crt")
            key_file = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".key")

            cert_file.write(VA_CERT.replace("\r\n", "\n"))
            key_file.write(VA_KEY.replace("\r\n", "\n"))
            cert_file.close()
            key_file.close()

            cert_data = (cert_file.name, key_file.name)

            ca_bundle_path = None
            ca_bundle_pem = self.secrets["credentials"].get("ca_bundle_pem")

            if ca_bundle_pem:
                ca_file = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".pem")
                ca_file.write(ca_bundle_pem.replace("\r\n", "\n"))
                ca_file.close()
                ca_bundle_path = ca_file.name

        # Prepare headers
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        if ex_headers:
            headers.update(ex_headers)

        # Make API request with SSL fallback
        # Make API request with SSL fallback (prefer VA CA bundle)
        last_error = None
        response = None
        error_response_body = None

        print(f"[VA API CLIENT] Calling {va_api} {method.upper()} {FULL_URL}")
        safe_headers = {k: v for k, v in headers.items() if k.lower() != "authorization"}
        print(f"[VA API CLIENT] Headers (no auth): {json.dumps(safe_headers)}")

        # Build verify options: 1) VA CA bundle (if present) 2) system CAs 3) no verify
        verify_options = []
        if ca_bundle_path:
            verify_options.append(ca_bundle_path)  # use VA internal CA bundle
        verify_options.append(True)  # fallback to system trust store
        verify_options.append(False)  # last-resort: disable verification

        for verify in verify_options:
            try:
                if method.upper() == "GET":
                    response = requests.get(
                        FULL_URL, headers=headers, timeout=10, verify=verify, cert=cert_data
                    )
                    # Check if this is a multipart file upload for tuple format
                elif method.upper() == "POST":
                    if body and "file" in body and isinstance(body["file"], tuple):
                        # Multipart file upload
                        headers.pop("Content-Type", None)
                        response = requests.post(
                            FULL_URL,
                            headers=headers,
                            files={"file": body["file"]},
                            data={"payload": body.get("payload", "")},
                            timeout=30,
                            verify=verify,
                            cert=cert_data,
                        )
                    else:
                        response = requests.post(
                            FULL_URL,
                            headers=headers,
                            json=body,
                            timeout=10,
                            verify=verify,
                            cert=cert_data,
                        )
                elif method.upper() == "PUT":
                    response = requests.put(
                        FULL_URL,
                        headers=headers,
                        json=body,
                        timeout=10,
                        verify=verify,
                        cert=cert_data,
                    )
                else:
                    return {
                        "statusCode": 400,
                        "body": {"error": f"Unsupported HTTP method: {method}"},
                    }

                # Capture response body for non-200 status codes safely
                if response.status_code != 200:
                    try:
                        error_response_body = response.text
                    except UnicodeDecodeError:
                        # fall back to raw bytes, truncated so logs don't explode
                        error_response_body = response.content[:1024]
                else:
                    response.raise_for_status()

                # Check if response is binary
                content_type = response.headers.get("content-type", "").lower()
                if (
                    "application/pdf" in content_type
                    or "image/" in content_type
                    or "application/octet-stream" in content_type
                ):
                    data = response.content
                    is_binary = True
                else:
                    data = response.text
                    is_binary = False

                # If we got here, this verify setting worked → stop trying others
                break

            except requests.exceptions.SSLError as e:
                # Specifically capture SSL errors so we know it's trust-chain related
                last_error = f"SSL error with verify={verify}: {e}"
                continue
            except Exception as e:
                last_error = str(e)
                continue

        # Clean up temporary certificate files (cert + key)
        if cert_data:
            for file_path in cert_data:
                if os.path.exists(file_path):
                    os.unlink(file_path)

        # Clean up temporary CA bundle file (VAInternal_CAs.pem)
        if ca_bundle_path and os.path.exists(ca_bundle_path):
            os.unlink(ca_bundle_path)

        # Handle response
        if response:
            response_at = datetime.now(timezone.utc)
            file_metadata = self._process_file_metadata(response, is_binary)
            parsed_response_data = self._parse_json_response(
                data, response.headers.get("content-type", "")
            )
            parsed_error_response = self._parse_json_response(error_response_body)

            request_size_mb = len(str(body).encode("utf-8")) / (1024 * 1024) if body else 0
            response_size_mb = len(data) / (1024 * 1024) if data else 0

            # Determine response status
            if response.status_code == 200:
                response_status = "success"
            elif response.status_code >= 400 and response.status_code < 500:
                response_status = "client_error"
            elif response.status_code >= 500:
                response_status = "server_error"
            else:
                response_status = "other"

            # Log API metrics
            if self.db_handler:
                api_metrics_data = {
                    "claim_id": claim_id,
                    "batch_id": lambda_request_id,
                    "batch_type": "lambda_event",
                    "api_endpoint": endpoint,
                    "api_name": va_api,
                    "http_method": method.upper(),
                    "requested_at": requested_at,
                    "response_at": response_at,
                    "request_size_mb": round(request_size_mb, 3),
                    "response_size_mb": round(response_size_mb, 3),
                    "response_status": response_status,
                    "http_status_code": str(response.status_code),
                    "retry_count": 0,
                    "max_retries": 2,
                    "error_message": error_response_body if response.status_code != 200 else None,
                    "is_resolved": response.status_code == 200,
                    "response_metadata": {
                        "content_type": response.headers.get("content-type", ""),
                        "is_binary": is_binary,
                        "file_metadata": file_metadata,
                    },
                    "inserted_by": "ApiClient",
                }
                self._log_api_metrics(api_metrics_data)

            return {
                "statusCode": 200,
                "body": {
                    "message": "Success",
                    "api": va_api,
                    "endpoint": endpoint,
                    "url": FULL_URL,
                    "method": method.upper(),
                    "status_code": response.status_code,
                    "data_length": len(data),
                    "response_data": parsed_response_data,
                    "is_binary": is_binary,
                    "content_type": response.headers.get("content-type", ""),
                    "file_metadata": file_metadata,
                    "error_response_body": parsed_error_response,
                },
            }
        else:
            response_at = datetime.now(timezone.utc)
            parsed_error_response = self._parse_json_response(error_response_body)
            request_size_mb = len(str(body).encode("utf-8")) / (1024 * 1024) if body else 0

            # Log API metrics for failed requests
            if self.db_handler:
                api_metrics_data = {
                    "claim_id": claim_id,
                    "batch_id": lambda_request_id,
                    "batch_type": "lambda_event",
                    "api_endpoint": endpoint,
                    "api_name": va_api,
                    "http_method": method.upper(),
                    "requested_at": requested_at,
                    "response_at": response_at,
                    "request_size_mb": round(request_size_mb, 3),
                    "response_size_mb": 0,
                    "response_status": "failure",
                    "http_status_code": "502",
                    "retry_count": 2,
                    "max_retries": 2,
                    "error_message": last_error,
                    "is_resolved": False,
                    "response_metadata": {"error_response": parsed_error_response},
                    "inserted_by": "ApiClient",
                }
                self._log_api_metrics(api_metrics_data)

            return {
                "statusCode": 502,
                "body": {
                    "error": "API request failed",
                    "api": va_api,
                    "endpoint": endpoint,
                    "url": FULL_URL,
                    "method": method.upper(),
                    "last_error": last_error,
                    "error_response_body": parsed_error_response,
                },
            }

    def _invoke_mock_lambda(self, va_api, endpoint, method, body, ex_headers,
                            claim_id, batch_id, lambda_request_id, requested_at):
        """Invoke L-Mock-API synchronously and return the response."""
        import base64

        mock_fn = os.environ.get("VA_MOCK_LAMBDA_NAME", "va-api-mock-api")
        print(f"[VA API CLIENT] [MOCK] {method} {va_api}/{endpoint}")

        try:
            if not hasattr(self, "_mock_lambda_client"):
                self._mock_lambda_client = boto3.client("lambda")

            resp = self._mock_lambda_client.invoke(
                FunctionName=mock_fn,
                InvocationType="RequestResponse",
                Payload=json.dumps({
                    "va_api": va_api, "endpoint": endpoint, "method": method,
                    "body": body, "headers": ex_headers or {}, "claim_id": claim_id,
                }, default=str),
            )
            result = json.loads(resp["Payload"].read())

            # Decode base64 binary (mock lambda encodes file_content as b64)
            body_dict = result.get("body", {})
            if body_dict.get("is_binary") and isinstance(body_dict.get("response_data"), str):
                result["body"]["response_data"] = base64.b64decode(body_dict["response_data"])

            # Log to api_metrics
            if self.db_handler:
                self._log_api_metrics({
                    "claim_id": claim_id,
                    "batch_id": lambda_request_id,
                    "batch_type": "lambda_event",
                    "api_endpoint": endpoint,
                    "api_name": va_api,
                    "http_method": method.upper(),
                    "requested_at": requested_at,
                    "response_at": datetime.now(timezone.utc),
                    "request_size_mb": 0, "response_size_mb": 0,
                    "response_status": "mock",
                    "http_status_code": str(body_dict.get("status_code", 200)),
                    "retry_count": 0, "max_retries": 0,
                    "error_message": None,
                    "is_resolved": body_dict.get("status_code", 200) == 200,
                    "response_metadata": {"source": "L-Mock-API"},
                    "inserted_by": "ApiClient_MOCK",
                })

            return result

        except Exception as e:
            print(f"[VA API CLIENT] [MOCK] invoke failed: {e}")
            return {"statusCode": 502, "body": {"error": str(e), "api": va_api, "endpoint": endpoint}}

    def _process_file_metadata(self, response, is_binary):
        """
        Process file metadata for S3 upload

        Args:
            response: HTTP response object
            is_binary: Boolean indicating if response is binary

        Returns:
            dict: File metadata including extension, content type, etc.
        """
        content_type = response.headers.get("content-type", "").lower()

        if is_binary:
            if "application/pdf" in content_type:
                return {
                    "file_extension": ".pdf",
                    "s3_content_type": "application/pdf",
                    "file_type": "pdf",
                }
            elif "image/jpeg" in content_type or "image/jpg" in content_type:
                return {
                    "file_extension": ".jpg",
                    "s3_content_type": "image/jpeg",
                    "file_type": "image",
                }
            elif "image/png" in content_type:
                return {
                    "file_extension": ".png",
                    "s3_content_type": "image/png",
                    "file_type": "image",
                }
            elif "image/" in content_type:
                return {
                    "file_extension": ".img",
                    "s3_content_type": content_type,
                    "file_type": "image",
                }
            else:
                return {
                    "file_extension": ".bin",
                    "s3_content_type": "application/octet-stream",
                    "file_type": "binary",
                }
        else:
            return {
                "file_extension": ".json",
                "s3_content_type": "application/json",
                "file_type": "text",
            }

    def upload_to_s3(
        self,
        s3_client,
        bucket,
        key_prefix,
        response_data,
        file_metadata,
        endpoint,
        va_api,
        add_timestamp=False,
    ):
        """
        Upload response data to S3 with proper content type and file extension

        Args:
            s3_client: Boto3 S3 client
            bucket: S3 bucket name
            key_prefix: S3 key prefix
            response_data: Response data (binary or text)
            file_metadata: File metadata from _process_file_metadata
            endpoint: API endpoint (for filename generation)
            va_api: API type (for path structure)
            add_timestamp: Boolean flag to add timestamp to filename

        Returns:
            dict: Upload result with success status and S3 key
        """
        try:
            endpoint_name = endpoint.replace("/", "-")

            if add_timestamp:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                s3_key = f"{key_prefix}/{va_api}/{endpoint_name}_{timestamp}{file_metadata['file_extension']}"
            else:
                s3_key = f"{key_prefix}/{va_api}/{endpoint_name}{file_metadata['file_extension']}"

            s3_client.put_object(
                Bucket=bucket,
                Key=s3_key,
                Body=response_data,
                ContentType=file_metadata["s3_content_type"],
            )

            return {
                "success": True,
                "s3_key": s3_key,
                "file_size": len(response_data),
                "content_type": file_metadata["s3_content_type"],
                "file_type": file_metadata["file_type"],
            }

        except Exception as e:
            return {"success": False, "error": str(e)}
