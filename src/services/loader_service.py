import aiofiles
import os
import inspect
from langchain_community.document_loaders import PyPDFLoader, CSVLoader
from langchain_community.document_loaders.image import UnstructuredImageLoader
from fastapi import UploadFile, HTTPException, status
from typing import List, Optional
from src.utils.constants.file_type import ALLOWED_FILE_TYPES, FILE_TYPE
from src.core.logger import logger
from src.services.chunking_service import chunking_service


class LoaderService:
    async def run(self, files: Optional[List[UploadFile]]):
        if not files:
            logger.info("No files provided and the loader run is terminated early.")
            return

        for file in files:
            if file.content_type not in ALLOWED_FILE_TYPES:
                raise HTTPException(
                    status_code=status.HTTP_406_NOT_ACCEPTABLE,
                    detail=f"Document with file name: {file.filename} and file type: {file.content_type} is not allowed",
                )

            await self._upload_file_to_local_directory(file)
            await self._load_file_by_type(file)

    async def _upload_file_to_local_directory(self, file: UploadFile):
        os.makedirs("uploads", exist_ok=True)
        file_location = f"uploads/{file.filename}"

        async with aiofiles.open(file_location, "wb") as buffer:
            while chunk := await file.read(1024):
                await buffer.write(chunk)

        logger.info(f"Uploaded {file.filename} in the local directory")

    def _get_local_file_path(self, file: UploadFile) -> str:
        return f"uploads/{file.filename}"

    async def _load_file_by_type(self, file: UploadFile):
        handlers = {
            FILE_TYPE["PDF"]: self._load_pdf,
            FILE_TYPE["JPEG"]: self._load_image,
            FILE_TYPE["PNG"]: self._load_image,
            FILE_TYPE["CSV"]: self._load_csv,
        }

        handler = handlers.get(file.content_type)

        if handler:
            if inspect.iscoroutinefunction(handler):
                return await handler(file)
            return handler(file)
        else:
            logger(f"Unsupported file type: {file.content_type}")

    async def _load_pdf(self, file: UploadFile):
        logger.info(f"Loading PDF file: {file.filename}")

        file_path = self._get_local_file_path(file)
        loader = PyPDFLoader(file_path)
        pages = []

        async for page in loader.alazy_load():
            pages.append(page)

        chunks = chunking_service.recursive_text_splitter(documents=pages)

    def _load_csv(self, file: UploadFile):
        logger.info(f"Loading CSV file: {file.filename}")

        file_path = self._get_local_file_path(file)
        loader = CSVLoader(file_path=file_path)

        documents = loader.load()
        chunks = chunking_service.recursive_text_splitter(documents)

    def _load_image(self, file: UploadFile):
        logger.info(f"Loading Image file: {file.filename}")

        file_path = self._get_local_file_path(file)
        loader = UnstructuredImageLoader(file_path)

        documents = loader.load()
        chunks = chunking_service.recursive_text_splitter(documents)


loader_service = LoaderService()
