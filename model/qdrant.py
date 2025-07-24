from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Qdrant
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from loguru import logger 
from settings import settings


class QdrantVectorStore:
    """
    A class to handle storing and retrieving embeddings in Qdrant vector database.
    """

    def __init__(self, embedding_model=settings.EMBEDDING_MODEL, collection_name="embeddings"):
        self.embedding_model = HuggingFaceEmbeddings(model_name=embedding_model)
        self.collection_name = collection_name
        self.client = QdrantClient(host="localhost", port=6333)
        if not self.client.collection_exists(self.collection_name):
            try:
                # Create a new collection with the specified vector parameters
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
                )
            except Exception as e:
                logger.error(f"Failed to create collection '{self.collection_name}': {e}")
                raise
         
       

    def store_embeddings(self, texts):
        """
        Store embeddings in Qdrant vector database.
        
        Args:
            texts (list): List of texts to be embedded and stored.
        """
        # Create a Qdrant instance with the specified embedding model
        qdrant = Qdrant.from_texts(
            texts=texts,
            embedding=self.embedding_model,
            collection_name=self.collection_name,
            client=self.client
        )
        return qdrant

    
    def search_embeddings(self, query, limit=5):
        """
        Search for similar embeddings in Qdrant vector database.
        
        Args:
            query (str): The query text to search for.
            limit (int): The number of results to return.
        
        Returns:
            list: List of similar texts found in the database.
        """
        qdrant = Qdrant(client=self.client, collection_name=self.collection_name, embeddings=self.embedding_model)
        results = qdrant.similarity_search(query, k=limit)
        return results
