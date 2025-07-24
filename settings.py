from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict
from zenml.client import Client
from zenml.exceptions import EntityExistsError


class Settings(BaseSettings):
  
    # OpenAI API
    OPENAI_MODEL_ID: str = "gpt-4o-mini"
    OPENAI_API_KEY: str | None = None

    # MongoDB database
    DATABASE_HOST: str = "mongodb://app_user:securepassword@127.0.0.1:27017/audio_eng_advices"
    DATABASE_NAME: str = "audio_eng_advices"

    PLAYLIST_URL: str = "https://www.youtube.com/playlist?list=PLnqsdcxUt078tNv8m6Xosn3bTxMrQmE8E" 
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    
    @classmethod
    def load_settings(cls) -> "Settings":
        """
        Tries to load the settings from the ZenML secret store. If the secret does not exist, it initializes the settings from the .env file and default values.

        Returns:
            Settings: The initialized settings object.
        """
        return Settings()


settings = Settings.load_settings()
