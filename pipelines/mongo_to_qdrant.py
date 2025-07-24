from zenml import step, pipeline
from loguru import logger

from steps.chunk_to_embedding import store_chunks_in_qdrant, retrieve_chunks_from_mango


@pipeline
def retrieve_insert_chunks_to_qdrant():
    """
    Pipeline to retrieve text chunks from MongoDB and store them in Qdrant vector store.
    """
    chunks = retrieve_chunks_from_mango()
    store_chunks_in_qdrant(chunks)

if __name__ == "__main__":
    retrieve_insert_chunks_to_qdrant()
    logger.info("Pipeline executed successfully.")