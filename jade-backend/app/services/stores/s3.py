# services/storage/s3.py

from pathlib import Path

import aioboto3
from botocore.exceptions import ClientError
from config.settings import s3_config, settings
from logger import logger

# Use a single session for the application lifecycle for efficiency
session = aioboto3.Session(region_name=settings.AWS_REGION)


async def upload_file_to_s3(file_path: Path, object_key: str) -> str:
    """
    Asynchronously uploads a file to the configured S3 bucket.

    Args:
        file_path (Path): The local path of the file to upload.
        object_key (str): The destination key (path) in the S3 bucket.

    Returns:
        str: The S3 URI of the uploaded object.

    Raises:
        Exception: If the upload fails.
    """
    bucket_name = s3_config.BUCKET_NAME
    logger.info(
        "Uploading '%s' to S3 bucket '%s' with key '%s'.",
        file_path.name,
        bucket_name,
        object_key,
    )

    try:
        async with session.client("s3") as s3_client:
            await s3_client.upload_file(str(file_path), bucket_name, object_key)

        s3_uri = f"s3://{bucket_name}/{object_key}"
        logger.info("Successfully uploaded file to %s", s3_uri)
        return s3_uri
    except ClientError as e:
        logger.error("S3 upload failed for key '%s': %s", object_key, e, exc_info=True)
        raise e
    except Exception as e:
        logger.error(
            "An unexpected error occurred during S3 upload: %s", e, exc_info=True
        )
        raise e
