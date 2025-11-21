import polars as pl
import boto3
from io import BytesIO

s3_bucket = 'api-datalake'
s3_client = boto3.client(
                's3',
                # endpoint_url='https://bucket.vpce-09b610ba89639ac28-2k64itq9-us-gov-east-1a.s3.us-gov-east-1.vpce.amazonaws.com'
)

def get_feed_details(api_source_name):
    feed_details = {
        "claims_contentions": {
            "endpoint": "claims_contentions/",
            "method": "POST",
            "payload": {
            },
            "s3_bucket_path": "api-datalake",
        },
    }
    feed = feed_details.get(api_source_name, None)
    if feed is None:
        raise ValueError(f"API Source Name {api_source_name} not found in feed_details")
    return feed

def read_feed_json_from_s3(s3_prefix):
    # get all json files in the s3 prefix
    print(f"Starting to Load from {s3_prefix}")
    response = s3_client.list_objects_v2(Bucket=s3_bucket, Prefix=s3_prefix)
    json_files = [obj['Key'] for obj in response['Contents'] if obj['Key'].endswith('.json')]

    print(f"Found File to Load from {s3_prefix}")
    dataframes = []
    for file_key in json_files:
        response = s3_client.get_object(Bucket=s3_bucket, Key=file_key)
        json_data = response['Body'].read()
        df = pl.read_json(BytesIO(json_data))
        df = df.with_columns([pl.lit(file_key).alias("source_file"), pl.lit(s3_bucket).alias("source_bucket")])
        dataframes.append(df)

    if not dataframes:
        raise ValueError(f"No JSON files found in s3://{s3_bucket}/{s3_prefix}")
    df_feed = pl.concat(dataframes, how="vertical_relaxed")
    # May need to parse the file_key for the claim_id, if a claim_id is not found, raise an error
    if 'claim_id' not in df_feed.columns:
        raise ValueError(f"Claim ID not found in feed data")
    return df_feed

def read_feed(s3_prefix):
    # get all json files in the s3 prefix
    print(f"Starting to Load V2 from {s3_prefix}")
    # df_feed = pl.scan_ndjson(s3_prefix).collect()
    df_feed = pl.read_ndjson(s3_prefix)
    # df_feed = pl.read_json(s3_prefix)
    print(f"Found File to Load from {s3_prefix}")
    # May need to parse the file_key for the claim_id, if a claim_id is not found, raise an error
    if 'claim_id' not in df_feed.columns:
        raise ValueError(f"Claim ID not found in feed data")
    return df_feed

def get_feed_data(api_source_name, claim_id):
    print('==> Start:')
    feed_details = get_feed_details(api_source_name)
    # build_full_s3_full_prefix = f"s3://{s3_bucket}/api-va-contention-lambda/api-endpoint/{api_source_name}/*.json"
    # df_feed = read_feed(build_full_s3_full_prefix)

    build_full_s3_full_prefix = f"api-va-contention-lambda/api-endpoint/{api_source_name}/"
    df_feed = read_feed_json_from_s3(build_full_s3_full_prefix)
    df_feed = df_feed.filter(pl.col('claim_id') == claim_id)
    return df_feed


def get_feed_data_response(api_source_name, claim_id):
    """
    Get the feed data for a given API source name and claim id
    and return the response data as the columns in the dataframe
    Args:
        api_source_name: The name of the API source
        claim_id: The claim id
    Returns:
        The response data
    """
    df_feed = get_feed_data(api_source_name, claim_id)
    df_feed_response = df_feed.select(pl.col('response_data'))
    # unnest the response_data column
    df_feed_response = df_feed_response.unnest(pl.col('response_data'))
    return df_feed_response.explode(pl.col('contentions')).unnest(pl.col('contentions'))
