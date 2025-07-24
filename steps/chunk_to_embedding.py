from model.mongo import VideoDocument, ArticleDocument
from model.qdrant import QdrantVectorStore

from typing import List
from zenml import step

from loguru import logger

DOC_OBJECTS = [VideoDocument, ArticleDocument]

@step
def store_chunks_in_qdrant(chunks: List[str]):
    """
    Stores the text chunks in a Qdrant vector store.

    Args:
        chunks (List[str]): The list of text chunks to be stored.
    """
    logger.info(f"Storing {len(chunks)} chunks in Qdrant vector store.")
    vector_store = QdrantVectorStore()
    vector_store.store_embeddings(chunks)

@step
def retrieve_chunks_from_mango():
    """
    Retrieves the latest document from the MongoDB collection and extracts its chunks.

    Returns:
        List[str]: The list of text chunks from the latest document.
    """
    all_chunks = []
    for doc_class in DOC_OBJECTS:
        doc = doc_class.retrieve_latest_doc()
        if doc != None:
            chunks = doc.chunks    
            all_chunks.extend(chunks)
        else :
            logger.warning(f"No documents found in the {doc_class.__name__} collection.")
    logger.info(f"Retrieved {all_chunks} chunks from MongoDB.")
    return all_chunks