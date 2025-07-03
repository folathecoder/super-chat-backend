from typing import List
from fastapi import UploadFile, HTTPException, status
from src.utils.constants.file_type import ALLOWED_FILE_TYPES
from src.models.file import FileData
from src.core.logger import logger
from src.utils.filters.filter_empty_files import filter_empty_files


async def read_files_into_memory(files: List[UploadFile]) -> List[FileData]:
    """
    Validate and read uploaded files into memory as FileData objects.

    Args:
        files (List[UploadFile]): List of uploaded files.

    Raises:
        HTTPException: If any file has an unsupported content type.

    Returns:
        List[FileData]: List of file data with filename, content bytes, and content type.
    """
    file_data_list: List[FileData] = []
    valid_files = filter_empty_files(files)

    for file in valid_files:
        if file.content_type not in ALLOWED_FILE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail=f"File type {file.content_type} not allowed for {file.filename}",
            )

        # Read file content asynchronously into bytes
        content_bytes = await file.read()

        file_data = FileData(
            filename=file.filename,
            content=content_bytes,
            content_type=file.content_type,
        )
        file_data_list.append(file_data)

    logger.info(f"Read {len(file_data_list)} files into memory")

    return file_data_list
