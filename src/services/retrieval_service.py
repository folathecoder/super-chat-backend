from typing import Optional, List
from src.services.loader_service import loader_service
from src.core.logger import logger
from src.models.file import FileData
from src.services.conversation_service import get_conversation
from src.utils.filters.filter_empty_files import filter_empty_files
from src.services.vector_store_service import search_documents_from_vector_store


class RetrievalService:
    conversation_id: str
    message_id: str

    async def run(
        self,
        query: str,
        conversation_id: str,
        message_id: str,
        files: Optional[List[FileData]] = None,
    ) -> str:
        valid_files = filter_empty_files(files)

        self.conversation_id = conversation_id
        self.message_id = message_id

        conversation = await get_conversation(conversation_id=self.conversation_id)
        has_uploaded_files = conversation.get("hasFilesUploaded", False)

        if not valid_files:
            if not has_uploaded_files:
                logger.info("No valid files and no uploads in conversation history.")
                return query

            logger.info("No new valid files. Use existing vector store context.")
            return self._retrieve_context_from_vector_store(query)

        logger.info("Valid files detected. Sending to loader service.")
        return await self._load_documents_and_retrieve_context_from_vector_store(
            query=query,
            files=valid_files,
        )

    def _retrieve_context_from_vector_store(self, query: str) -> str:
        search_filter = {"conversation_id": {"$eq": self.conversation_id}}

        documents = search_documents_from_vector_store(
            query=query, k=4, filter=search_filter
        )

        page_contents = []
        for document in documents:
            page_contents.append(document.page_content)

        context = " ".join(page_contents)

        logger.info("Context retrieved from vector store")
        return context

    async def _load_documents_and_retrieve_context_from_vector_store(
        self,
        query: str,
        files: List[FileData],
    ) -> str:
        loading_status = await loader_service.run(
            files=files,
            conversation_id=self.conversation_id,
            message_id=self.message_id,
        )

        if loading_status is True:
            return self._retrieve_context_from_vector_store(query=query)

        logger.warning(f"Document loading failed or incomplete: {loading_status}")
        return query


retrieval_service = RetrievalService()
