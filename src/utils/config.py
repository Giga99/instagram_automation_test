"""
Environment Configuration Management
Centralized handling of environment variables with validation.
"""
import os
from typing import Optional

from dotenv import load_dotenv


class Config:
    """Centralized configuration management."""

    def __init__(self):
        load_dotenv()

    # Instagram Configuration
    @property
    def instagram_post_url(self) -> str:
        return os.getenv("INSTAGRAM_POST_URL", "")

    @property
    def comment_prompt(self) -> str:
        return os.getenv("COMMENT_PROMPT", "gym workout motivation")

    # OpenAI Configuration
    @property
    def openai_api_key(self) -> str:
        return os.getenv("OPENAI_API_KEY", "")

    # AdsPower Configuration  
    @property
    def adspower_base_url(self) -> str:
        return os.getenv("ADSPOWER_BASE_URL", "http://localhost:50325")

    @property
    def adspower_api_key(self) -> Optional[str]:
        return os.getenv("ADSPOWER_API_KEY")

    # Automation Settings
    @property
    def headless_mode(self) -> bool:
        return os.getenv("HEADLESS_MODE", "true").lower() == "true"

    @property
    def post_comment(self) -> bool:
        return os.getenv("POST_COMMENT", "false").lower() == "true"

    # Telegram Configuration
    @property
    def telegram_bot_token(self) -> Optional[str]:
        return os.getenv("TELEGRAM_BOT_TOKEN")

    @property
    def telegram_chat_id(self) -> Optional[str]:
        return os.getenv("TELEGRAM_CHAT_ID")


# Global config instance
config = Config()
