"""
Application Configuration
Handles all environment variables and settings
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Security
    SECRET_KEY: str = "development-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:password@postgres:5432/voice_agent_db"
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "voice_agent_db"
    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: str = "password"
    
    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    # API Keys
    OPENAI_API_KEY: str = "sk-placeholder-key"
    ELEVENLABS_API_KEY: str = "placeholder-key"
    
    # AWS Configuration
    AWS_ACCESS_KEY_ID: str = "placeholder-access-key"
    AWS_SECRET_ACCESS_KEY: str = "placeholder-secret-key"
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET: str = "placeholder-bucket"
    AWS_S3_BUCKET_AUDIO: str = "placeholder-audio-bucket"
    
    # Voice Configuration
    ELEVENLABS_VOICE_ID: str = "21m00Tcm4TlvDq8ikWAM"
    ELEVENLABS_STABILITY: float = 0.5
    ELEVENLABS_SIMILARITY_BOOST: float = 0.75
    
    # OpenAI Configuration
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_MAX_TOKENS: int = 1500
    OPENAI_TEMPERATURE: float = 0.7
    
    # Telephony
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None
    
    # Webhook Configuration
    WEBHOOK_SECRET: str = "development-webhook-secret"
    
    # Billing
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    
    # CORS  
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    ALLOWED_HOSTS: str = "*"
    
    # File Upload
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_FILE_TYPES: str = "pdf,txt,docx,md"
    
    def get_allowed_origins(self) -> List[str]:
        """Get ALLOWED_ORIGINS as a list"""
        if isinstance(self.ALLOWED_ORIGINS, str):
            return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
        return ["http://localhost:3000"]
    
    def get_allowed_hosts(self) -> List[str]:
        """Get ALLOWED_HOSTS as a list"""
        if isinstance(self.ALLOWED_HOSTS, str):
            return [host.strip() for host in self.ALLOWED_HOSTS.split(",")]
        return ["*"]
    
    def get_allowed_file_types(self) -> List[str]:
        """Get ALLOWED_FILE_TYPES as a list"""
        if isinstance(self.ALLOWED_FILE_TYPES, str):
            return [file_type.strip() for file_type in self.ALLOWED_FILE_TYPES.split(",")]
        return ["pdf", "txt", "docx", "md"]
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True
    }


# Create settings instance
settings = Settings()