import aioboto3
from botocore.exceptions import ClientError
from src.core.logger import logger


async def delete_objects_by_metadata(
    bucket_name: str, metadata_key: str, metadata_value: str
):
    keys_to_delete = []
    session = aioboto3.Session()

    async with session.client("s3") as s3_client:
        paginator = s3_client.get_paginator("list_objects_v2")

        async for page in paginator.paginate(Bucket=bucket_name):
            for obj in page.get("Contents", []):
                key = obj["Key"]

                try:
                    head = await s3_client.head_object(Bucket=bucket_name, Key=key)
                    meta = head.get("Metadata", {})

                    if meta.get(metadata_key) == metadata_value:
                        keys_to_delete.append(key)

                except ClientError as e:
                    logger.info(f"Failed to get metadata for {key}: {e}")

        if not keys_to_delete:
            logger.info("No objects found matching metadata criteria.")
            return

        logger.info(
            f"Deleting {len(keys_to_delete)} objects matching metadata {metadata_key}={metadata_value}..."
        )

        batch_size = 1000

        for i in range(0, len(keys_to_delete), batch_size):
            batch = keys_to_delete[i : i + batch_size]
            objects = [{"Key": k} for k in batch]

            try:
                response = await s3_client.delete_objects(
                    Bucket=bucket_name,
                    Delete={"Objects": objects, "Quiet": True},
                )

                deleted_count = len(response.get("Deleted", []))
                logger.info(
                    f"Deleted batch {i // batch_size + 1}, deleted count: {deleted_count}"
                )

            except ClientError as e:
                logger.error(f"Failed to delete batch {i // batch_size + 1}: {e}")
