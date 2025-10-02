# === config.py ===
"""Configuration settings for SPL Shield Bot"""

from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Bot Configuration
    BOT_TOKEN: str
    
    # Backend API (localhost:8000 since running on same VPS)
    API_BASE_URL: str = "http://localhost:8000"
    
    # Admin Users (comma-separated Telegram user IDs)
    ADMIN_USER_IDS: str = ""
    
    # Environment
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"  # Added this field
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Added this to ignore extra fields
    
    @property
    def admin_ids(self) -> List[int]:
        """Parse admin IDs from string"""
        if not self.ADMIN_USER_IDS:
            return []
        return [int(id.strip()) for id in self.ADMIN_USER_IDS.split(",")]

def get_settings() -> Settings:
    return Settings()