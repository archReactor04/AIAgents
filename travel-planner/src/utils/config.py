"""Configuration management"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration"""
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    
    # Model Configuration
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")  # or gpt-4o-mini for faster/cheaper
    
    # Feature Flags
    ENABLE_CACHE = True
    CACHE_TTL = 3600  # 1 hour
    
    # Swarm Configuration
    MAX_TURNS = 20
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY is not set. "
                "Please add it to your .env file or environment variables."
            )
        return True

