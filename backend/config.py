from functools import lru_cache
import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


class Settings(BaseModel):
    gemini_api_key: str = Field(default="")
    gemini_model: str = Field(default="gemini-2.5-flash")
    max_document_chars: int = Field(default=50000, ge=1000, le=200000)
    cors_origins: list[str] = Field(default_factory=lambda: [
        "http://localhost:8501",
        "http://127.0.0.1:8501",
    ])


@lru_cache
def get_settings() -> Settings:
    origins = os.getenv("CORS_ORIGINS", "")
    parsed_origins = [item.strip() for item in origins.split(",") if item.strip()]
    return Settings(
        gemini_api_key=os.getenv("GEMINI_API_KEY", "").strip(),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip(),
        max_document_chars=int(os.getenv("MAX_DOCUMENT_CHARS", "50000")),
        cors_origins=parsed_origins or [
            "http://localhost:8501",
            "http://127.0.0.1:8501",
        ],
    )
