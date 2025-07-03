import os
import asyncio
import inspect
import aioboto3
from uuid import uuid4
from langchain_core.documents import Document
from langchain_community.document_loaders import S3FileLoader
from fastapi import UploadFile, HTTPException, status
from typing import List
from botocore.exceptions import ClientError

from src.utils.constants.file_type import FILE_TYPE
from src.core.logger import logger
from src.models.file import FileData
from src.services.chunking_service import chunking_service
from src.services.vector_store_service import add_documents_to_vector_store
from src.services.user_service import get_current_user
from src.models.conversation import UpdateConversation
from src.services.conversation_service import update_conversation
from src.core.config import ENV_VARS

BUCKET_NAME = ENV_VARS["AWS_S3_BUCKET_NAME"]
session = aioboto3.Session()


class LoaderService:
    upload_dir: str = "uploads"
    conversation_id: str
    message_id: str

    async def run(
        self, files: List[FileData], conversation_id: str, message_id: str
    ) -> bool:
        """
        Process multiple files: upload to S3, split and index their content,
        then update conversation status.

        Args:
            files (List[FileData]): List of files to process.
            conversation_id (str): Conversation ID related to the files.
            message_id (str): Message ID related to the files.

        Returns:
            bool: True if all files processed successfully, False otherwise.
        """
        if not files:
            logger.info("No files provided and the loader run is terminated early.")
            return False

        self.conversation_id = conversation_id
        self.message_id = message_id

        try:
            tasks = [self._process_file(file) for file in files]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for res in results:
                if isinstance(res, Exception):
                    logger.error(f"Error loading file: {res}")
                    return False

            # Mark conversation as having files uploaded
            updated_conversation = UpdateConversation(hasFilesUploaded=True)
            await update_conversation(
                conversation_id=conversation_id,
                update_conversation=updated_conversation,
            )

            logger.info("All files loaded successfully.")
            return True

        except Exception as e:
            logger.error(f"Error in background file processing: {e}")
            return False

    async def _process_file(self, file: UploadFile):
        """
        Upload file to S3 and load its content based on type.

        Args:
            file (UploadFile): The file to process.
        """
        file_key = await self._upload_file_to_s3(file)
        logger.info(f"Uploaded file with key: {file_key}")
        await self._load_file_by_type(file_key=file_key, content_type=file.content_type)

    async def _upload_file_to_s3(self, file_data: FileData) -> str:
        """
        Upload a file to S3 asynchronously.

        Args:
            file_data (FileData): File data to upload.

        Returns:
            str: Generated S3 key for the uploaded file.

        Raises:
            HTTPException: If upload fails.
        """
        ext = os.path.splitext(file_data.filename)[1]
        file_key = f"{uuid4()}{ext}"

        async with session.client("s3") as s3_client:
            try:
                await s3_client.put_object(
                    Bucket=BUCKET_NAME,
                    Key=file_key,
                    Body=file_data.content,
                    ContentType=file_data.content_type,
                    Metadata={
                        "original_filename": file_data.filename,
                        "conversation_id": self.conversation_id,
                        "message_id": self.message_id,
                    },
                )
                logger.info(f"Successfully uploaded file to S3: {file_key}")

            except ClientError as e:
                logger.error(f"Failed to upload file to S3: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error uploading file {file_data.filename} to storage: {str(e)}",
                )

        return file_key

    def _load_file_from_s3(self, file_key: str) -> List[Document]:
        """
        Load file content from S3 using the S3FileLoader.

        Args:
            file_key (str): The S3 key of the file.

        Returns:
            List[Document]: List of loaded documents.
        """
        loader = S3FileLoader(BUCKET_NAME, file_key)
        return loader.load()

    async def _load_file_by_type(self, file_key: str, content_type: str):
        """
        Dispatch file loading based on MIME type.

        Args:
            file_key (str): S3 key of the file.
            content_type (str): MIME type of the file.

        Raises:
            HTTPException: For unsupported file types.
        """
        handlers = {
            FILE_TYPE["PDF"]: self._load_pdf,
            FILE_TYPE["JPEG"]: self._load_image,
            FILE_TYPE["PNG"]: self._load_image,
            FILE_TYPE["CSV"]: self._load_csv,
        }

        handler = handlers.get(content_type)

        if handler:
            if inspect.iscoroutinefunction(handler):
                return await handler(file_key)
            return handler(file_key)
        else:
            logger.error(f"Unsupported file type: {content_type}")
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Unsupported file type: {content_type}",
            )

    async def _load_pdf(self, file_key: str):
        """
        Load and chunk PDF document, enrich metadata, then add to vector store.

        Args:
            file_key (str): S3 key of the PDF file.
        """
        documents = self._load_file_from_s3(file_key)
        chunks = chunking_service.recursive_text_splitter(documents=documents)
        enriched_chunks = await self._enrich_documents_with_metadata(chunks)

        logger.info(
            f"Loaded PDF document and splitted into {len(chunks)} chunks: {file_key}"
        )

        add_documents_to_vector_store(documents=enriched_chunks, key=file_key)

    async def _load_image(self, file_key: str):
        """
        Load and chunk image document, enrich metadata, then add to vector store.

        Args:
            file_key (str): S3 key of the image file.
        """
        documents = self._load_file_from_s3(file_key)
        chunks = chunking_service.recursive_text_splitter(documents)
        enriched_chunks = await self._enrich_documents_with_metadata(chunks)

        logger.info(
            f"Loaded Image document and splitted into {len(chunks)} chunks: {file_key}"
        )

        add_documents_to_vector_store(documents=enriched_chunks, key=file_key)

    async def _load_csv(self, file_key: str):
        """
        Load and chunk CSV document, enrich metadata, then add to vector store.

        Args:
            file_key (str): S3 key of the CSV file.
        """
        documents = self._load_file_from_s3(file_key)
        chunks = chunking_service.recursive_text_splitter(documents)
        enriched_chunks = await self._enrich_documents_with_metadata(chunks)

        logger.info(
            f"Loaded CSV document and splitted into {len(chunks)} chunks: {file_key}"
        )

        add_documents_to_vector_store(documents=enriched_chunks, key=file_key)

    async def _enrich_documents_with_metadata(
        self, documents: List[Document]
    ) -> List[Document]:
        """
        Add conversation, message, user IDs, and chunk order to document metadata.

        Args:
            documents (List[Document]): List of documents to enrich.

        Returns:
            List[Document]: Enriched documents.
        """
        user = await get_current_user()

        for i, document in enumerate(documents):
            document.metadata.update(
                {
                    "conversation_id": self.conversation_id,
                    "message_id": self.message_id,
                    "user_id": user["id"],
                    "order": i,
                }
            )

        return documents


loader_service = LoaderService()
