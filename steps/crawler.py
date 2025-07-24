from pytube import Playlist
from pytube import extract
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from zenml import step
from loguru import logger


def get_title(video_url: str) -> str:
    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        info = ydl.extract_info(video_url, download=False)
        return info.get('title', 'No Title Found')
    
def get_subtitles(video_id: str) -> dict:
    ytt_api = YouTubeTranscriptApi()
    transcript = ytt_api.fetch(video_id)
    subtitles = []
    for tr in transcript.snippets:
        subtitles.append(tr.text)

    return subtitles
        
@step
def get_vids_info(playlist:str) -> str:
    """
    Extracts video information (title, subtitles) from a YouTube playlist URL.

    Args:
        playlist (str): The URL of the YouTube playlist.

    Returns:
        str: A formatted string containing the title and subtitles of each video in the playlist.
    """
    pl = Playlist(playlist)
    videos_info = []
    
    for url in pl.video_urls:
        info = {
            'title': get_title(url),
            'subtitles': get_subtitles(extract.video_id(url)),
        }
        info_str = f"{info['title']}\n" + "\n".join(info['subtitles'])
        videos_info.append(info_str)

    logger.info(f"Extracted information for {len(videos_info)} videos from the playlist.")
    return "\n".join(videos_info)

