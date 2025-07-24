import uuid
from abc import ABC
from typing import Generic, Type, TypeVar
from pydantic import UUID4, BaseModel, Field
from typing import List, Dict, ClassVar, Any
from connection.connector import connection
from settings import settings
from pymongo import errors
from loguru import logger
from datetime import datetime, timezone
from pymongo import DESCENDING
from langchain.text_splitter import RecursiveCharacterTextSplitter
T = TypeVar("T", bound="NoSQLBaseDocument")

_database = connection.get_database(settings.DATABASE_NAME)

class NoSQLBaseDocument(BaseModel, Generic[T], ABC):
    collection_name: ClassVar[str]
    
    @classmethod
    def from_dict(cls: Type[T], data: dict) -> T:
        if "_id" in data and "id" not in data:
            data["id"] = data.pop("_id")
        return cls(**data)

    def to_dict(self: T) -> dict:
        parsed = self.model_dump(mode="json", exclude_none=True)
        if "_id" not in parsed and "id" in parsed:
            parsed["_id"] = str(parsed.pop("id"))

        return parsed
    
    def insert(self:T) -> T | None:
        """
        Inserts the document into the MongoDB collection.

        Returns:
            str: The ID of the inserted document.
        """
        logger.info(f"Inserting document into collection: {self.collection_name} DB {_database}")
        collection = _database[self.collection_name]
        try:
            collection.insert_one(self.to_dict())

            return self
        except errors.WriteError:
            logger.exception("Failed to insert document.")

            return None
    @classmethod    
    def retrieve_latest_doc(cls: Type[T], limit: int = 1) -> List[T]:
        """
        Retrieves the latest document from the collection.

        Args:
            limit (int): The maximum number of documents to retrieve.

        Returns:
            Instance of T: the latest document.
        """
        logger.info(f"Retrieving latest {limit} documents from collection: {cls.collection_name}")
        collection = _database[cls.collection_name]
        if not collection:
            logger.error(f"Collection {cls.collection_name} does not exist in the database.")
            return []
        cursor = collection.find().sort("metadata.created_at", DESCENDING).limit(limit)
        doc = list(cursor)[0]

        return cls.from_dict(doc)
    

class VideoDocument(NoSQLBaseDocument):
    collection_name: ClassVar[str] = "videos_document"

    id: UUID4 = Field(default_factory=uuid.uuid4)
    full_text: str
    chunks: List[str]
    metadata: Dict[str, Any] = {}

    def add_metadata(self, chunking_strategy: RecursiveCharacterTextSplitter) -> None:
        """
        Adds metadata to the document.
        """
      
        self.metadata.update({
            "created_at": datetime.now(timezone.utc).isoformat(),
            "chunking_strategy": {"chunk_size": chunking_strategy._chunk_size, 
                                    "chunk_overlap": chunking_strategy._chunk_overlap,
                                    "separators": chunking_strategy._separators}
        })
        
class ArticleDocument(NoSQLBaseDocument):
    collection_name: ClassVar[str] = "articles_document"
    #TODO: Implement ArticleDocument class
    pass