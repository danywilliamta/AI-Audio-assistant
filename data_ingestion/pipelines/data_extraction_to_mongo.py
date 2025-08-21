from zenml import pipeline
from steps.crawler import get_vids_info
from steps.process_text import text_to_chunks, insert_document
from settings import settings
from loguru import logger

playlist_url = settings.PLAYLIST_URL


@pipeline
def insert_video_document(playlist_url: str):
    """
    Pipeline to extract video information from a YouTube playlist and store it in a NoSQL database.

    Args:
        playlist_url (str): The URL of the YouTube playlist.
    """
    text = get_vids_info(playlist_url)
    chunks = text_to_chunks(text)
    insert_document(text, chunks)

if __name__ == "__main__":
    insert_video_document(playlist_url=playlist_url)
    logger.info("Pipeline executed successfully.")