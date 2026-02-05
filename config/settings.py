"""Application settings and configuration loader."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application configuration settings."""
    
    def __init__(self):
        # Database configuration
        self.DATABASE_URL = os.getenv(
            "DATABASE_URL", 
            "sqlite:///mindfulme.db"
        )
        
        # Secret key for security
        self.SECRET_KEY = os.getenv(
            "SECRET_KEY", 
            "dev-secret-key-change-in-production"
        )
        
        # Model cache directory
        self.MODEL_CACHE_DIR = os.getenv("MODEL_CACHE_DIR") or None
        
        # Debug mode
        self.DEBUG = os.getenv("DEBUG", "True").lower() == "true"
        
        # Application paths
        self.BASE_DIR = Path(__file__).parent.parent
        self.STATIC_DIR = self.BASE_DIR / "static"
        self.DATABASE_DIR = self.BASE_DIR
        
    @property
    def is_sqlite(self) -> bool:
        """Check if using SQLite database."""
        return self.DATABASE_URL.startswith("sqlite")
    
    @property
    def is_postgresql(self) -> bool:
        """Check if using PostgreSQL database."""
        return self.DATABASE_URL.startswith("postgresql")


# Global settings instance
settings = Settings()
