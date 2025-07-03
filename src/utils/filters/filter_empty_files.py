from fastapi import UploadFile
from typing import Optional, List


def filter_empty_files(
    files: Optional[List[UploadFile]] = None,
) -> list[UploadFile]:
    """
    Filter out empty or invalid files from the given list.

    Args:
        files (Optional[List[UploadFile]]): List of uploaded files, can be None.

    Returns:
        list[UploadFile]: List containing only valid files with filename and content_type.
    """
    valid_files = [
        file for file in (files or []) if file and file.filename and file.content_type
    ]

    return valid_files
