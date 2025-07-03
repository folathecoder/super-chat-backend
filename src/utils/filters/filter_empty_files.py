from fastapi import UploadFile
from typing import Optional, List


def filter_empty_files(
    files: Optional[List[UploadFile]] = None,
) -> list[UploadFile]:

    valid_files = [
        file for file in (files or []) if file and file.filename and file.content_type
    ]

    return valid_files
