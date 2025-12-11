"""Configuration management for AliExpress API service."""

import os
import logging
from dataclasses import dataclass
from typing import Any, List, Optional
from dotenv import load_dotenv
from ..exceptions import ConfigurationError

logger: logging.Logger = logging.getLogger(__name__)

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
    
    def validate(self) -> None:
        """
        Validate configuration values.
        
        Raises:
            ConfigurationError: If configuration is invalid
        """
        # Validate app credentials
        if not self.app_key or len(self.app_key) < 5:
            logger.error(
                "Configuration validation failed: invalid app_key",
                extra={"app_key_length": len(self.app_key) if self.app_key else 0}
            )
            raise ConfigurationError(
                "Invalid app_key: must be at least 5 characters",
                details={"app_key_length": len(self.app_key) if self.app_key else 0}
            )
        
        if not self.app_secret or len(self.app_secret) < 10:
            logger.error(
                "Configuration validation failed: invalid app_secret",
                extra={"app_secret_length": len(self.app_secret) if self.app_secret else 0}
            )
            raise ConfigurationError(
                "Invalid app_secret: must be at least 10 characters",
                details={"app_secret_length": len(self.app_secret) if self.app_secret else 0}
            )
        
        if not self.tracking_id:
            logger.error("Configuration validation failed: tracking_id is required")
            raise ConfigurationError(
                "tracking_id is required",
                details={"tracking_id": self.tracking_id}
            )
        
        # Validate language
        valid_languages = ['EN', 'RU', 'PT', 'ES', 'FR', 'ID', 'IT', 'TH', 'JA', 'AR', 'VI', 'TR', 'DE', 'HE', 'KO', 'NL', 'PL', 'MX', 'CL', 'IN']
        if self.language not in valid_languages:
            logger.error(
                "Configuration validation failed: invalid language",
                extra={"language": self.language, "valid_languages": valid_languages}
            )
            raise ConfigurationError(
                f"Invalid language: {self.language}. Must be one of {valid_languages}",
                details={"language": self.language, "valid_languages": valid_languages}
            )
        
        # Validate currency
        valid_currencies = ['USD', 'GBP', 'CAD', 'EUR', 'UAH', 'MXN', 'TRY', 'RUB', 'BRL', 'AUD', 'INR', 'JPY', 'IDR', 'SEK', 'KRW']
        if self.currency not in valid_currencies:
            logger.error(
                "Configuration validation failed: invalid currency",
                extra={"currency": self.currency, "valid_currencies": valid_currencies}
            )
            raise ConfigurationError(
                f"Invalid currency: {self.currency}. Must be one of {valid_currencies}",
                details={"currency": self.currency, "valid_currencies": valid_currencies}
            )
        
        # Validate port
        if not (1 <= self.api_port <= 65535):
            logger.error(
                "Configuration validation failed: invalid api_port",
                extra={"api_port": self.api_port}
            )
            raise ConfigurationError(
                f"Invalid api_port: {self.api_port}. Must be between 1 and 65535",
                details={"api_port": self.api_port}
            )
        
        # Validate log level
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.log_level.upper() not in valid_log_levels:
            logger.error(
                "Configuration validation failed: invalid log_level",
                extra={"log_level": self.log_level, "valid_log_levels": valid_log_levels}
            )
            raise ConfigurationError(
                f"Invalid log_level: {self.log_level}. Must be one of {valid_log_levels}",
                details={"log_level": self.log_level, "valid_log_levels": valid_log_levels}
            )
        
        # Validate rate limits
        if self.max_requests_per_minute < 1:
            logger.error(
                "Configuration validation failed: invalid max_requests_per_minute",
                extra={"max_requests_per_minute": self.max_requests_per_minute}
            )
            raise ConfigurationError(
                "max_requests_per_minute must be at least 1",
                details={"max_requests_per_minute": self.max_requests_per_minute}
            )
        
        if self.max_requests_per_second < 1:
            logger.error(
                "Configuration validation failed: invalid max_requests_per_second",
                extra={"max_requests_per_second": self.max_requests_per_second}
            )
            raise ConfigurationError(
                "max_requests_per_second must be at least 1",
                details={"max_requests_per_second": self.max_requests_per_second}
            )
        
        # Validate environment
        valid_environments = ['development', 'staging', 'production']
        if self.environment not in valid_environments:
            logger.error(
                "Configuration validation failed: invalid environment",
                extra={"environment": self.environment, "valid_environments": valid_environments}
            )
            raise ConfigurationError(
                f"Invalid environment: {self.environment}. Must be one of {valid_environments}",
                details={"environment": self.environment, "valid_environments": valid_environments}
            )
        
        # Security warnings for production
        if self.environment == 'production':
            if self.admin_api_key == 'admin-secret-key-change-in-production':
                logger.error("Configuration validation failed: ADMIN_API_KEY must be changed in production")
                raise ConfigurationError(
                    "ADMIN_API_KEY must be changed in production!",
                    details={"environment": "production"}
                )
            
            if self.debug:
                logger.error("Configuration validation failed: DEBUG mode must be disabled in production")
                raise ConfigurationError(
                    "DEBUG mode must be disabled in production!",
                    details={"environment": "production", "debug": self.debug}
                )
        
        logger.info(
            "Configuration validated successfully",
            extra={
                "environment": self.environment,
                "language": self.language,
                "currency": self.currency
            }
        )
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Load configuration from environment variables."""
        # Only load .env file if not in serverless environment (Vercel, AWS Lambda, etc.)
        is_serverless = any([
            os.getenv('VERCEL') == '1',
            os.getenv('AWS_LAMBDA_FUNCTION_NAME'),
            os.getenv('FUNCTIONS_WORKER_RUNTIME'),
            os.getenv('K_SERVICE'),
        ])
        
        if not is_serverless:
            # Load .env file for local development (override=True to override existing env vars)
            try:
                load_dotenv(override=True)
                logger.debug("Loaded configuration from .env file")
            except Exception as e:
                logger.debug(
                    ".env file not found or could not be loaded (this is optional)",
                    extra={
                        "error_type": type(e).__name__,
                        "error_message": str(e)
                    }
                )
                pass  # .env file is optional
        
        # Required fields - fail fast if missing
        # Strip whitespace/newlines to handle copy-paste errors in Vercel dashboard
        app_key = os.getenv('ALIEXPRESS_APP_KEY', '').strip()
        app_secret = os.getenv('ALIEXPRESS_APP_SECRET', '').strip()
        tracking_id = os.getenv('ALIEXPRESS_TRACKING_ID', 'gpt_chat').strip()
        
        # Debug logging for serverless (removed print statements for Vercel compatibility)
        
        # Validate credentials immediately
        if not app_key or not app_key.strip():
            raise ConfigurationError(
                "ALIEXPRESS_APP_KEY environment variable is required. "
                "Get your credentials at https://open.aliexpress.com/"
            )
        if not app_secret or not app_secret.strip():
            raise ConfigurationError(
                "ALIEXPRESS_APP_SECRET environment variable is required. "
                "Get your credentials at https://open.aliexpress.com/"
            )
        
        # Optional fields with defaults
        # Strip all values to prevent whitespace issues
        language = os.getenv('ALIEXPRESS_LANGUAGE', 'EN').strip()
        currency = os.getenv('ALIEXPRESS_CURRENCY', 'USD').strip()
        api_host = os.getenv('API_HOST', '0.0.0.0').strip()
        api_port = int(os.getenv('API_PORT', '8000').strip())
        log_level = os.getenv('LOG_LEVEL', 'INFO').strip()
        
        # Security settings - strip to prevent whitespace issues
        admin_api_key = os.getenv('ADMIN_API_KEY', 'admin-secret-key-change-in-production').strip()
        internal_api_key = os.getenv('INTERNAL_API_KEY', 'ALIINSIDER-2025').strip()
        max_requests_per_minute = int(os.getenv('MAX_REQUESTS_PER_MINUTE', '60').strip())
        max_requests_per_second = int(os.getenv('MAX_REQUESTS_PER_SECOND', '5').strip())
        allowed_origins = os.getenv(
            'ALLOWED_ORIGINS', 
            'https://chat.openai.com,https://chatgpt.com,https://platform.openai.com,'
            'http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000,http://127.0.0.1:8000,'
            'https://aliexpress-api-proxy.vercel.app'
        ).strip()
        environment = os.getenv('ENVIRONMENT', 'development').strip()
        debug = os.getenv('DEBUG', 'false').strip().lower() == 'true'
        
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
    
