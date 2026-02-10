import logging
import uuid
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from django.conf import settings

logger = logging.getLogger(__name__)


class MinIOStorage:
    """Lazy-initialised S3/MinIO client with automatic bucket creation."""

    def __init__(self):
        self._client = None
        self._bucket_ensured = False

    @property
    def client(self):
        if self._client is None:
            self._client = boto3.client(
                's3',
                endpoint_url=settings.S3_ENDPOINT_URL,
                aws_access_key_id=settings.S3_ACCESS_KEY,
                aws_secret_access_key=settings.S3_SECRET_KEY,
                config=Config(signature_version='s3v4'),
                region_name='us-east-1',
            )
        return self._client

    @property
    def bucket(self):
        return settings.S3_BUCKET_NAME

    def _ensure_bucket(self):
        if self._bucket_ensured:
            return
        try:
            self.client.head_bucket(Bucket=self.bucket)
        except ClientError:
            self.client.create_bucket(Bucket=self.bucket)
            logger.info("Created bucket %s", self.bucket)
        self._bucket_ensured = True


    # Public API
    def upload_file(self, file, folder: str = "uploads") -> dict:
        """Upload a Django UploadedFile to MinIO. Returns storage metadata."""
        self._ensure_bucket()

        ext = file.name.rsplit('.', 1)[-1] if '.' in file.name else ''
        object_key = f"{folder}/{uuid.uuid4()}.{ext}" if ext else f"{folder}/{uuid.uuid4()}"

        self.client.upload_fileobj(
            file, self.bucket, object_key,
            ExtraArgs={'ContentType': file.content_type},
        )

        return {
            'bucket_name': self.bucket,
            's3_object_key': object_key,
            'mime_type': file.content_type,
            'file_size': file.size,
        }

    def delete_file(self, object_key: str) -> bool:
        try:
            self.client.delete_object(Bucket=self.bucket, Key=object_key)
            return True
        except ClientError as exc:
            logger.warning("Failed to delete %s: %s", object_key, exc)
            return False

    def get_presigned_url(self, object_key: str, expiration: int = 3600) -> str | None:
        try:
            return self.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': object_key},
                ExpiresIn=expiration,
            )
        except ClientError as exc:
            logger.warning("Presigned URL failed for %s: %s", object_key, exc)
            return None


storage = MinIOStorage()  # lazy – nothing happens until first use
