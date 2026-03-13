"""Global configuration management for the ZURU Melon Company Assistant."""

from typing import List, Optional
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """
    Application settings with type validation.
    All values are read from environment variables, no hardcoded secrets.
    """

    # OpenRouter API Configuration
    OPENROUTER_API_KEY: str
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    # Search API Configuration (Optional, for internet search)
    SERPER_API_KEY: Optional[str] = None

    # Model Configuration
    LLM_MODEL: str = "meta-llama/llama-3-8b-instruct"
    TEMPERATURE: float = 0.0

    # Retrieval Configuration
    RETRIEVE_TOP_K: int = 3
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    KNOWLEDGE_BASE_PATH: str = "data/"
    VECTOR_INDEX_PATH: str = "data/faiss_index/"

    # Dialogue Configuration
    MAX_DIALOGUE_HISTORY: int = 5

    # Safety Configuration
    BLOCKED_KEYWORDS: List[str] = [
        "hack",
        "illegal",
        "phishing",
        "malware",
        "virus",
        "confidential",
        "secret",
        "proprietary",
        "exploit",
        "crack",
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True


# Initialize settings singleton
settings = Settings()