from typing import List
from langchain_core.documents import Document
from src.db.pinecone import vector_store, compressor, reordering
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
    min_score: float = 0.6,
) -> List[Document]:
    """
    Perform a similarity search in the vector store with a query.

    Args:
        query (str): The query string to search.
        k (int, optional): Number of top documents to return. Defaults to 4.
        filter (dict | None, optional): Optional filter to narrow search results. Defaults to None.
        namespace (str | None, optional): Optional namespace to search within. Defaults to None.
        min_score (float, optional): Minimum score to include document (Ranging from 0 to 1). Defaults to 0.6.

    Returns:
        List[Document]: List of documents matching the query with score.
    """
    search_results = vector_store.similarity_search_with_score(
        query=query, k=k, filter=filter, namespace=namespace
    )

    filtered_results = [
        (doc, score) for doc, score in search_results if score >= min_score
    ]

    documents = [doc for doc, _ in filtered_results]

    if not documents:
        logger.info("No documents passed the score threshold")
        return []

    optimized_search_results = optimize_vector_search_result(documents, query)

    logger.info(
        f"Retrieved {len(optimized_search_results)} documents with score >= {min_score} from vector DB for query: {query}"
    )

    return optimized_search_results


def optimize_vector_search_result(
    documents: List[Document], query: str
) -> List[Document]:
    """
    Optimizes retrieved vector search results by applying contextual compression
    and reordering to reduce noise and mitigate the 'lost in the middle' effect.

    Args:
        documents (List[Document]): List of documents retrieved from the vector store.
        query (str): The user query used for retrieval and compression context.

    Returns:
        List[Document]: A list of optimized documents that are compressed for relevance
                        and reordered to enhance LLM response quality.
    """

    compressed_documents = compressor.compress_documents(
        documents=documents, query=query
    )

    reordered_documents = reordering.transform_documents(compressed_documents)

    return reordered_documents


def delete_documents_from_vector_store(
    filter: dict,
    namespace: str | None = None,
    key: str = "",
):
    """
    Delete documents from the vector store using metadata filter.

    Args:
        filter (dict): The metadata filter used to select documents to delete.
        namespace (str | None, optional): Optional namespace to delete from. Defaults to None.
        key (str, optional): An optional identifier for logging. Defaults to "".
    """
    vector_store.delete(filter=filter, namespace=namespace)
    logger.info(f"Deleted documents from vector store using filter: {filter} | {key}")
