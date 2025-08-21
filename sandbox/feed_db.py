import asyncio
import os

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import FastEmbedEmbeddings


db_path = os.getenv("DB_PATH")

# Embeddings + split config
embedding = FastEmbedEmbeddings()
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", " "],
)


async def get_pdf_text(file_path):

    loader = PyPDFLoader(file_path)
    docs = loader.load()
    await store_chunks(docs)

    text = ""
    for doc in docs:
        text += doc.page_content + "\n"

    return text


async def query_chroma(query):
    
    vector_store = Chroma(persist_directory=db_path, embedding_function=embedding)
    results = vector_store.similarity_search(query, k=8)
   
    return results


async def store_chunks(docs):
    chunks = text_splitter.split_documents(docs)
 
    vector_store = Chroma(
        embedding_function=embedding,
        persist_directory=db_path
    )
    vector_store.add_documents(chunks)
    vector_store.persist()


async def main():
    ressources = os.getenv("RESSOURCES")
    docs = [ressources]
    for doc in docs:

        await get_pdf_text(doc)

    res = await query_chroma("What are good compression settings for vocals?")


if __name__ == "__main__":
    asyncio.run(main())
