import logging
import tempfile

import aiofiles
from fastapi import APIRouter, File, HTTPException, UploadFile, status

from ecommerceapi.libs.b2 import b2_upload_file

logger = logging.getLogger(__name__)

router = APIRouter()

CHUNK_SIZE = 1024 * 1024  # 1MB


@router.post("/upload", status_code=201)
async def upload_file(file: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name
            logger.debug(f"Created temporary file at {temp_file_path}")
            async with aiofiles.open(temp_file_path, "wb") as out_file:
                while chunk := await file.read(CHUNK_SIZE):
                    await out_file.write(chunk)

            file_url = b2_upload_file(temp_file_path, file.filename)

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File upload failed",
        )

    return {
        "details": f"Successfully uploaded {file.filename}",
        "file_url": file_url,
    }
