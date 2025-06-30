from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
)


class ChunkingService:
    def recursive_text_splitter(
        self,
        documents: List[Document],
        chunk_size: int = 1000,
        chunk_overlap: int = 100,
    ) -> List[Document]:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )

        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        split_docs = text_splitter.create_documents(texts, metadatas)

        return split_docs


chunking_service = ChunkingService()
