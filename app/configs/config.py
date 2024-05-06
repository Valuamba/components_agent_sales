from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import find_dotenv, load_dotenv
from typing import List

load_dotenv()


class AppSettings(BaseSettings):
    openai_api_key: str = Field(env="OPENAI_API_KEY")
    serper_api_key: str = Field(env="SERPER_API_KEY")
    famaga_db_url: str = Field(env="FAMAGA_DB_URL")
    bot_token: str = Field(env="BOT_TOKEN")
    redis_host: str = Field(env="REDIS_HOST")
    environment: str = Field(env="ENVIRONMENT", default="local")
    notify_users_ids: List[int] = [6102292898]

    vector_collection_name: str = "details"
    similarity_search_limit: float = 0.1
    embeddings_model: str = "text-embedding-ada-002"
    index_dimensions: int = 1536
    top_k: int = 6
    search_4price_restricted_websites: List[str] = [
        "alibaba.com",
        "youtube.com",
        "ebay.com",
        "famaga.de",
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"


app_settings = AppSettings()
