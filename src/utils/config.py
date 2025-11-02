"""Configuration management for AliExpress API service."""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv


class ConfigurationError(Exception):
    """Raised when configuration is invalid or missing."""
    pass


@dataclass
class Config:
    """Configuration class for AliExpress API service."""
    
    app_key: str
    app_secret: str
    tracking_id: str
    language: str = "EN"
    currency: str = "USD"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Load configuration from environment variables."""
        load_dotenv()
        
        # Required fields
        app_key = os.getenv('ALIEXPRESS_APP_KEY')
        app_secret = os.getenv('ALIEXPRESS_APP_SECRET')
        tracking_id = os.getenv('ALIEXPRESS_TRACKING_ID', 'gpt_chat')
        
        if not app_key:
            raise ConfigurationError("ALIEXPRESS_APP_KEY environment variable is required")
        if not app_secret:
            raise ConfigurationError("ALIEXPRESS_APP_SECRET environment variable is required")
        
        # Optional fields with defaults
        language = os.getenv('ALIEXPRESS_LANGUAGE', 'EN')
        currency = os.getenv('ALIEXPRESS_CURRENCY', 'USD')
        api_host = os.getenv('API_HOST', '0.0.0.0')
        api_port = int(os.getenv('API_PORT', '8000'))
        log_level = os.getenv('LOG_LEVEL', 'INFO')
        
        return cls(
            app_key=app_key,
            app_secret=app_secret,
            tracking_id=tracking_id,
            language=language,
            currency=currency,
            api_host=api_host,
            api_port=api_port,
            log_level=log_level
        )
    
    def validate(self) -> None:
        """Validate configuration values."""
        if not self.app_key or not self.app_key.strip():
            raise ConfigurationError("app_key cannot be empty")
        if not self.app_secret or not self.app_secret.strip():
            raise ConfigurationError("app_secret cannot be empty")
        if not self.tracking_id or not self.tracking_id.strip():
            raise ConfigurationError("tracking_id cannot be empty")
        
        # Validate language and currency codes
        valid_languages = ['EN', 'RU', 'PT', 'ES', 'FR', 'ID', 'IT', 'TH', 'JA', 'AR', 'VI', 'TR', 'DE', 'HE', 'KO', 'NL', 'PL', 'MX', 'CL', 'IN']
        valid_currencies = ['USD', 'GBP', 'CAD', 'EUR', 'UAH', 'MXN', 'TRY', 'RUB', 'BRL', 'AUD', 'INR', 'JPY', 'IDR', 'SEK', 'KRW']
        
        if self.language not in valid_languages:
            raise ConfigurationError(f"Invalid language '{self.language}'. Must be one of: {', '.join(valid_languages)}")
        if self.currency not in valid_currencies:
            raise ConfigurationError(f"Invalid currency '{self.currency}'. Must be one of: {', '.join(valid_currencies)}")
        
        if self.api_port < 1 or self.api_port > 65535:
            raise ConfigurationError("api_port must be between 1 and 65535")