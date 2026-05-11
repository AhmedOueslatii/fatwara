import io
import uuid
from typing import Literal

from minio import Minio
from minio.error import S3Error

from app.core.config import settings


CertFormat = Literal["pkcs12", "pem"]


class StorageError(RuntimeError):
    pass


def _client() -> Minio:
    return Minio(
        settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=settings.MINIO_SECURE,
    )


def ensure_bucket() -> None:
    client = _client()
    bucket = settings.MINIO_BUCKET_CERTS
    try:
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)
    except S3Error as exc:
        raise StorageError(f"Failed to ensure bucket {bucket}: {exc}") from exc


def _object_name(user_id: uuid.UUID, fmt: CertFormat) -> str:
    ext = "p12" if fmt == "pkcs12" else "pem"
    return f"users/{user_id}/cert.{ext}"


def upload_cert(user_id: uuid.UUID, data: bytes, fmt: CertFormat) -> str:
    client = _client()
    bucket = settings.MINIO_BUCKET_CERTS
    object_name = _object_name(user_id, fmt)
    content_type = (
        "application/x-pkcs12" if fmt == "pkcs12" else "application/x-pem-file"
    )
    try:
        client.put_object(
            bucket,
            object_name,
            io.BytesIO(data),
            length=len(data),
            content_type=content_type,
        )
    except S3Error as exc:
        raise StorageError(f"Failed to upload cert: {exc}") from exc
    return object_name


def download_cert(storage_path: str) -> bytes:
    client = _client()
    bucket = settings.MINIO_BUCKET_CERTS
    try:
        response = client.get_object(bucket, storage_path)
        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()
    except S3Error as exc:
        raise StorageError(f"Failed to download cert at {storage_path}: {exc}") from exc


def delete_cert(storage_path: str) -> None:
    client = _client()
    bucket = settings.MINIO_BUCKET_CERTS
    try:
        client.remove_object(bucket, storage_path)
    except S3Error as exc:
        raise StorageError(f"Failed to delete cert at {storage_path}: {exc}") from exc
