import logging
from functools import lru_cache

import b2sdk.v2 as b2

from ecommerceapi.config import config

logger = logging.getLogger(__name__)


@lru_cache()
def b2_api():
    """Initialize and return a Backblaze B2 API instance."""
    logger.debug("Creating and authorizing B2 API instance.")
    info = b2.InMemoryAccountInfo()
    b2_api = b2.B2Api(info)
    b2_api.authorize_account("production", config.B2_KEY_ID, config.B2_APPLICATION_KEY)
    return b2_api


@lru_cache()
def b2_get_bucket(api: b2.B2Api):
    """Retrieve and return the specified B2 bucket."""
    bucket = api.get_bucket_by_name(config.B2_BUCKET_NAME)
    logger.debug(f"Retrieving bucket: {config.B2_BUCKET_NAME}")
    if not bucket:
        logger.error(f"Bucket {config.B2_BUCKET_NAME} not found.")
        raise ValueError(f"Bucket {config.B2_BUCKET_NAME} not found.")
    return bucket


def b2_upload_file(local_file_path: str, b2_file_name: str) -> str:
    """Upload a file to Backblaze B2."""
    api = b2_api()
    uploaded_file = b2_get_bucket(api).upload_local_file(
        local_file=local_file_path,
        file_name=b2_file_name,
    )
    download_url = api.get_download_url_for_fileid(uploaded_file.id_)

    logger.debug(
        f"Uploaded file {local_file_path} to B2 as {b2_file_name}. Download URL: {download_url}"
    )
    return download_url
