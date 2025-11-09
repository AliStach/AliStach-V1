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
    
    # Security settings
    admin_api_key: str = "admin-secret-key-change-in-production"
    internal_api_key: str = "ALIINSIDER-2025"
    max_requests_per_minute: int = 60
    max_requests_per_second: int = 5
    allowed_origins: str = "https://chat.openai.com,https://chatgpt.com"
    environment: str = "development"
    debug: bool = False
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Load configuration from environment variables."""
        # Load .env file if it exists (silently fails if not found)
        try:
            load_dotenv()
        except Exception:
            pass  # .env file is optional
        
        # Required fields - use safe defaults for serverless environments
        app_key = os.getenv('ALIEXPRESS_APP_KEY', '')
        app_secret = os.getenv('ALIEXPRESS_APP_SECRET', '')
        tracking_id = os.getenv('ALIEXPRESS_TRACKING_ID', 'gpt_chat')
        
        # In serverless environments, allow app to start without credentials
        # The app will run in degraded mode and return 503 errors
        if not app_key or not app_key.strip():
            # Don't raise immediately - let the app start in degraded mode
            # The lifespan will handle this gracefully
            app_key = app_key or 'MISSING_APP_KEY'
        if not app_secret or not app_secret.strip():
            app_secret = app_secret or 'MISSING_APP_SECRET'
        
        # Optional fields with defaults
        language = os.getenv('ALIEXPRESS_LANGUAGE', 'EN')
        currency = os.getenv('ALIEXPRESS_CURRENCY', 'USD')
        api_host = os.getenv('API_HOST', '0.0.0.0')
        api_port = int(os.getenv('API_PORT', '8000'))
        log_level = os.getenv('LOG_LEVEL', 'INFO')
        
        # Security settings
        admin_api_key = os.getenv('ADMIN_API_KEY', 'admin-secret-key-change-in-production')
        internal_api_key = os.getenv('INTERNAL_API_KEY', 'ALIINSIDER-2025')
        max_requests_per_minute = int(os.getenv('MAX_REQUESTS_PER_MINUTE', '60'))
        max_requests_per_second = int(os.getenv('MAX_REQUESTS_PER_SECOND', '5'))
        allowed_origins = os.getenv('ALLOWED_ORIGINS', 'https://chat.openai.com,https://chatgpt.com')
        environment = os.getenv('ENVIRONMENT', 'development')
        debug = os.getenv('DEBUG', 'false').lower() == 'true'
        
        return cls(
            app_key=app_key,
            app_secret=app_secret,
            tracking_id=tracking_id,
            language=language,
            currency=currency,
            api_host=api_host,
            api_port=api_port,
            log_level=log_level,
            admin_api_key=admin_api_key,
            internal_api_key=internal_api_key,
            max_requests_per_minute=max_requests_per_minute,
            max_requests_per_second=max_requests_per_second,
            allowed_origins=allowed_origins,
            environment=environment,
            debug=debug
        )
    
    def validate(self) -> None:
        """Validate configuration values."""
        # Check for missing credentials but don't crash - allow degraded mode
        if not self.app_key or not self.app_key.strip() or self.app_key == 'MISSING_APP_KEY':
            raise ConfigurationError("ALIEXPRESS_APP_KEY environment variable is required")
        if not self.app_secret or not self.app_secret.strip() or self.app_secret == 'MISSING_APP_SECRET':
            raise ConfigurationError("ALIEXPRESS_APP_SECRET environment variable is required")
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