from model.mongo import VideoDocument, ArticleDocument
from model.qdrant import QdrantVectorStore
from langchain.text_splitter import RecursiveCharacterTextSplitter

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
        if doc:
            chunks = doc.chunks    
            all_chunks.extend(chunks)
        else :
            logger.warning(f"No documents found in the {doc_class.__name__} collection.")

    return all_chunks