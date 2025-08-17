from fastapi import APIRouter, status, File, UploadFile, HTTPException
from typing import List, Optional
from src.services.loader_service import LoaderService

file_router = APIRouter()


@file_router.post("/upload", status_code=status.HTTP_201_CREATED, response_model=str)
async def upload_file(file: Optional[UploadFile] = File(default=None)):

    if file is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No file uploaded"
        )

    try:
        loader_service = LoaderService()

        print("file_content", file)

        file_key = await loader_service.upload_file_to_s3(file_data=file)

        print("file_key", file_key)

        return file_key
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to upload file: {str(e)}",
        )
