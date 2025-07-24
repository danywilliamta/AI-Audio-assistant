

from model.mongo import VideoDocument, ArticleDocument
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from typing import List
from zenml import step
from loguru import logger

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", " "],
)


@step
def text_to_chunks(text: str) -> list[str]:
    """
    Splits the input text into chunks using the configured text splitter.

    Args:
        text (str): The text to be split into chunks.

    Returns:
        list[str]: A list of text chunks.
    """
    docs = [Document(page_content=text)]
    chunks = text_splitter.split_documents(docs)    
    
    return [chunk.page_content for chunk in chunks]

@step
def insert_document(text:str, chunks:List[str]):
    """
    Inserts a new document into the NoSQL database.

    Args:
        text (str): The full text of the document.
        chunks (List[str]): The list of text chunks derived from the document.

    Returns:
        VideoDocument: The inserted document object.
    """
    doc = VideoDocument(full_text=text, chunks=chunks)
    doc.add_metadata(chunking_strategy=text_splitter)
    
    return doc.insert() 
