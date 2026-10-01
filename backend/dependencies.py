from fastapi import HTTPException

from .config import get_settings


def require_gemini_key() -> str:
    key = get_settings().gemini_api_key
    if not key:
        raise HTTPException(
            status_code=503,
            detail="Gemini API key is not configured. Add GEMINI_API_KEY to .env and restart the backend.",
        )
    return key
