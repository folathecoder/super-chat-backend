from typing import List
from langchain_core.documents import Document
from src.db.pinecone import vector_store
from src.core.logger import logger


def add_documents_to_vector_store(documents: List[Document], key: str = ""):
    """
    Add a list of Document objects to the vector store.

    Args:
        documents (List[Document]): The documents to be added.
        key (str, optional): An optional identifier for logging. Defaults to "".
    """
    vector_store.add_documents(documents=documents)
    logger.info(f"Stored {len(documents)} documents in the vector database: {key}")


def search_documents_from_vector_store(
    query: str,
    k: int = 4,
    filter: dict | None = None,
    namespace: str | None = None,
) -> List[Document]:
    """
    Perform a similarity search in the vector store with a query.

    Args:
        query (str): The query string to search.
        k (int, optional): Number of top documents to return. Defaults to 4.
        filter (dict | None, optional): Optional filter to narrow search results. Defaults to None.
        namespace (str | None, optional): Optional namespace to search within. Defaults to None.

    Returns:
        List[Document]: List of documents matching the query.
    """
    search_results = vector_store.similarity_search(
        query=query, k=k, filter=filter, namespace=namespace
    )
    logger.info(
        f"Retrieved {len(search_results)} documents from the vector database for query: {query}"
    )
    return search_results
