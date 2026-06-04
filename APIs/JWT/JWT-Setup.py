import jwt
import uuid
from datetime import datetime, timedelta


class JwtHandler:
    """JWT token handler for VA API authentication."""

    def __init__(
        self,
        secret_key: str,
        issuer: str,
        user_id: str,
        station_id: str,
        expiration_seconds: int = 3600,
    ):
        self.SECRET_KEY = secret_key
        self.ISSUER = issuer
        self.USER_ID = user_id
        self.STATION_ID = station_id
        self.EXPIRATION_SECONDS = expiration_seconds

    def create_jwt(self) -> str:
        """Create a signed JWT token with user and station information."""
        claims = self._build_claims(self.USER_ID, self.STATION_ID)

        return jwt.encode(claims, self.SECRET_KEY, algorithm="HS256")

    def decode_jwt(self, jwt_token: str):
        """Decode and verify a JWT token."""
        return jwt.decode(jwt_token, self.SECRET_KEY, algorithms=["HS256"])

    def _build_claims(self, user_id: str, station_id: str):
        """Build JWT claims dictionary with standard fields."""
        now = datetime.utcnow()
        return {
            "jti": str(uuid.uuid4()),  # JWT ID for uniqueness
            "iat": now,  # Issued at timestamp
            "exp": now + timedelta(seconds=self.EXPIRATION_SECONDS),  # Expiration
            "iss": self.ISSUER,  # Issuer
            "applicationID": self.ISSUER,  # Application ID (same as issuer)
            "userID": user_id,  # User identifier
            "stationID": station_id,  # Station identifier
        }
