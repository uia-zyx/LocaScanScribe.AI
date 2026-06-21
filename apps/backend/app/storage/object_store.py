from uuid import UUID

import boto3
from botocore.client import BaseClient
from botocore.exceptions import ClientError

from app.core.settings import get_settings


class ObjectStore:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client: BaseClient = boto3.client(
            "s3",
            endpoint_url=self.settings.s3_endpoint,
            aws_access_key_id=self.settings.s3_access_key,
            aws_secret_access_key=self.settings.s3_secret_key,
        )
        self._ensure_bucket()

    def put_document(
        self,
        document_id: UUID,
        filename: str,
        content: bytes,
        mime_type: str,
    ) -> str:
        key = f"documents/{document_id}/{filename}"
        self.client.put_object(
            Bucket=self.settings.s3_bucket_documents,
            Key=key,
            Body=content,
            ContentType=mime_type,
        )
        return key

    def get_document(self, storage_key: str) -> bytes:
        response = self.client.get_object(
            Bucket=self.settings.s3_bucket_documents,
            Key=storage_key,
        )
        return response["Body"].read()

    def delete_document(self, storage_key: str | None) -> None:
        if not storage_key:
            return

        self.client.delete_object(
            Bucket=self.settings.s3_bucket_documents,
            Key=storage_key,
        )

    def _ensure_bucket(self) -> None:
        bucket = self.settings.s3_bucket_documents
        try:
            self.client.head_bucket(Bucket=bucket)
        except ClientError:
            self.client.create_bucket(Bucket=bucket)
