"""
S3 Bucket File Transfer Script
Transfers files from one S3 bucket to another while preserving the key structure.
"""

import boto3
from botocore.exceptions import ClientError
import logging
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class S3BucketTransfer:
    def __init__(self, aws_access_key_id: Optional[str] = None, 
                 aws_secret_access_key: Optional[str] = None,
                 region_name: str = 'us-gov-east-1'):
        """
        Initialize S3 client.
        
        Args:
            aws_access_key_id: AWS access key (optional if using IAM role or env vars)
            aws_secret_access_key: AWS secret key (optional if using IAM role or env vars)
            region_name: AWS region name
        """
        if aws_access_key_id and aws_secret_access_key:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=region_name
            )
        else:
            # Use default credentials (from ~/.aws/credentials or IAM role)
            self.s3_client = boto3.client('s3', region_name=region_name)
    
    def transfer_files(self, source_bucket: str, destination_bucket: str, 
                      prefix: str = '', delete_source: bool = False) -> dict:
        """
        Transfer files from source bucket to destination bucket.
        
        Args:
            source_bucket: Name of the source S3 bucket
            destination_bucket: Name of the destination S3 bucket
            prefix: Optional prefix to filter objects (e.g., 'folder1/')
            delete_source: Whether to delete files from source after copying
            
        Returns:
            dict: Summary of transfer operation
        """
        transferred = 0
        failed = 0
        skipped = 0
        
        try:
            # List all objects in source bucket
            paginator = self.s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=source_bucket, Prefix=prefix)
            
            for page in pages:
                if 'Contents' not in page:
                    logger.warning(f"No objects found in {source_bucket} with prefix '{prefix}'")
                    continue
                
                for obj in page['Contents']:
                    key = obj['Key']
                    
                    # Skip if it's just a folder marker
                    if key.endswith('/'):
                        skipped += 1
                        continue
                    
                    try:
                        # Copy object to destination bucket
                        copy_source = {'Bucket': source_bucket, 'Key': key}
                        self.s3_client.copy_object(
                            CopySource=copy_source,
                            Bucket=destination_bucket,
                            Key=key
                        )
                        
                        logger.info(f"Transferred: {key}")
                        transferred += 1
                        
                        # Optionally delete from source
                        if delete_source:
                            self.s3_client.delete_object(Bucket=source_bucket, Key=key)
                            logger.info(f"Deleted from source: {key}")
                        
                    except ClientError as e:
                        logger.error(f"Failed to transfer {key}: {str(e)}")
                        failed += 1
            
            summary = {
                'transferred': transferred,
                'failed': failed,
                'skipped': skipped,
                'total': transferred + failed + skipped
            }
            
            logger.info(f"\nTransfer Summary:")
            logger.info(f"  Successfully transferred: {transferred}")
            logger.info(f"  Failed: {failed}")
            logger.info(f"  Skipped: {skipped}")
            
            return summary
            
        except ClientError as e:
            logger.error(f"Error accessing buckets: {str(e)}")
            raise
    
    def transfer_single_file(self, source_bucket: str, destination_bucket: str, 
                            key: str, new_key: Optional[str] = None) -> bool:
        """
        Transfer a single file between buckets.
        
        Args:
            source_bucket: Name of the source S3 bucket
            destination_bucket: Name of the destination S3 bucket
            key: Object key in source bucket
            new_key: Optional different key for destination (defaults to same key)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            copy_source = {'Bucket': source_bucket, 'Key': key}
            destination_key = new_key if new_key else key
            
            self.s3_client.copy_object(
                CopySource=copy_source,
                Bucket=destination_bucket,
                Key=destination_key
            )
            
            logger.info(f"Successfully transferred {key} to {destination_key}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to transfer {key}: {str(e)}")
            return False


def main():
    """
    Example usage of the S3BucketTransfer class
    """
    # Configuration
    SOURCE_BUCKET = 'api-datalake'
    DESTINATION_BUCKET = 'dbq-templates'
    PREFIX = 'prodtest/level-0/20251120/'  # Optional: filter by prefix (e.g., 'folder1/')
    
    # Initialize transfer object
    # Option 1: Use default AWS credentials
    transfer = S3BucketTransfer()
    
    # Option 2: Provide explicit credentials
    # transfer = S3BucketTransfer(
    #     aws_access_key_id='YOUR_ACCESS_KEY',
    #     aws_secret_access_key='YOUR_SECRET_KEY',
    #     region_name='us-east-1'
    # )
    
    # Transfer all files
    logger.info(f"Starting transfer from {SOURCE_BUCKET} to {DESTINATION_BUCKET}")
    summary = transfer.transfer_files(
        source_bucket=SOURCE_BUCKET,
        destination_bucket=DESTINATION_BUCKET,
        prefix=PREFIX,
        delete_source=False  # Set to True to move instead of copy
    )
    
    # Transfer a single file example
    # transfer.transfer_single_file(
    #     source_bucket=SOURCE_BUCKET,
    #     destination_bucket=DESTINATION_BUCKET,
    #     key='path/to/file.txt'
    # )


if __name__ == '__main__':
    main()
