"""
S3 Service for file uploads and management
"""
import boto3
import os
import logging
import asyncio
from typing import Optional
from botocore.exceptions import ClientError, NoCredentialsError

logger = logging.getLogger(__name__)

class S3Service:
    def __init__(self):
        self.bucket_name = os.getenv('S3_BUCKET_NAME', 'ai-messaging-tool-production-uploads')
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        
        try:
            self.s3_client = boto3.client(
                's3',
                region_name=self.region
            )
            logger.info(f"S3 service initialized with bucket: {self.bucket_name}")
        except NoCredentialsError:
            logger.error("AWS credentials not found")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize S3 service: {e}")
            raise

    def upload_file(self, file_content: bytes, file_key: str, content_type: str = 'application/octet-stream') -> Optional[str]:
        """
        Upload file content to S3 (synchronous version)
        
        Args:
            file_content: File content as bytes
            file_key: S3 object key (path in bucket)
            content_type: MIME type of the file
            
        Returns:
            S3 URL if successful, None if failed
        """
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=file_content,
                ContentType=content_type
            )
            
            s3_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{file_key}"
            logger.info(f"File uploaded to S3: {s3_url}")
            return s3_url
            
        except ClientError as e:
            logger.error(f"Failed to upload file to S3: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error uploading to S3: {e}")
            return None

    async def upload_file_async(self, file_content: bytes, file_key: str, content_type: str = 'application/octet-stream') -> Optional[str]:
        """
        Upload file content to S3 asynchronously
        
        Args:
            file_content: File content as bytes
            file_key: S3 object key (path in bucket)
            content_type: MIME type of the file
            
        Returns:
            S3 URL if successful, None if failed
        """
        try:
            # Run the synchronous S3 operation in a thread pool
            loop = asyncio.get_event_loop()
            s3_url = await loop.run_in_executor(
                None,
                self._upload_file_sync,
                file_content,
                file_key,
                content_type
            )
            return s3_url
            
        except Exception as e:
            logger.error(f"Unexpected error in async upload to S3: {e}")
            return None

    def _upload_file_sync(self, file_content: bytes, file_key: str, content_type: str) -> Optional[str]:
        """
        Synchronous helper method for S3 upload
        """
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=file_content,
                ContentType=content_type
            )
            
            s3_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{file_key}"
            logger.info(f"File uploaded to S3: {s3_url}")
            return s3_url
            
        except ClientError as e:
            logger.error(f"Failed to upload file to S3: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error uploading to S3: {e}")
            return None

    def download_file(self, file_key: str) -> Optional[bytes]:
        """
        Download file content from S3
        
        Args:
            file_key: S3 object key (path in bucket)
            
        Returns:
            File content as bytes if successful, None if failed
        """
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            return response['Body'].read()
            
        except ClientError as e:
            logger.error(f"Failed to download file from S3: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error downloading from S3: {e}")
            return None

    def delete_file(self, file_key: str) -> bool:
        """
        Delete file from S3
        
        Args:
            file_key: S3 object key (path in bucket)
            
        Returns:
            True if successful, False if failed
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            logger.info(f"File deleted from S3: {file_key}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to delete file from S3: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting from S3: {e}")
            return False

    def file_exists(self, file_key: str) -> bool:
        """
        Check if file exists in S3
        
        Args:
            file_key: S3 object key (path in bucket)
            
        Returns:
            True if file exists, False otherwise
        """
        try:
            self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            logger.error(f"Error checking file existence in S3: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error checking file in S3: {e}")
            return False

    def get_file_url(self, file_key: str) -> str:
        """
        Get public URL for a file in S3
        
        Args:
            file_key: S3 object key (path in bucket)
            
        Returns:
            Public S3 URL
        """
        return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{file_key}"

    def list_files(self, prefix: str = "") -> list:
        """
        List files in S3 bucket with optional prefix
        
        Args:
            prefix: Prefix to filter files
            
        Returns:
            List of file keys
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            if 'Contents' in response:
                return [obj['Key'] for obj in response['Contents']]
            return []
            
        except ClientError as e:
            logger.error(f"Failed to list files in S3: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error listing files in S3: {e}")
            return []
