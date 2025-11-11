"""Unit tests for configuration management."""

import pytest
import os
from unittest.mock import patch

from src.utils.config import Config, ConfigurationError


class TestConfig:
    """Test configuration management."""
    
    def test_config_creation_with_valid_data(self):
        """Test creating config with valid data."""
        config = Config(
            app_key="test_key",
            app_secret="test_secret",
            tracking_id="test_tracking"
        )
        
        assert config.app_key == "test_key"
        assert config.app_secret == "test_secret"
        assert config.tracking_id == "test_tracking"
        assert config.language == "EN"  # Default value
        assert config.currency == "USD"  # Default value
    
    def test_config_validation_success(self):
        """Test successful config validation."""
        config = Config(
            app_key="test_key",
            app_secret="test_secret",
            tracking_id="test_tracking",
            language="EN",
            currency="USD"
        )
        
        # Should not raise any exception
        config.validate()
    
    def test_config_validation_empty_app_key(self):
        """Test validation fails with empty app key."""
        config = Config(
            app_key="",
            app_secret="test_secret",
            tracking_id="test_tracking"
        )
        
        # Error message updated to match actual Config.validate() implementation
        with pytest.raises(ConfigurationError, match="ALIEXPRESS_APP_KEY environment variable is required"):
            config.validate()
    
    def test_config_validation_empty_app_secret(self):
        """Test validation fails with empty app secret."""
        config = Config(
            app_key="test_key",
            app_secret="",
            tracking_id="test_tracking"
        )
        
        # Error message updated to match actual Config.validate() implementation
        with pytest.raises(ConfigurationError, match="ALIEXPRESS_APP_SECRET environment variable is required"):
            config.validate()
    
    def test_config_validation_invalid_language(self):
        """Test validation fails with invalid language."""
        config = Config(
            app_key="test_key",
            app_secret="test_secret",
            tracking_id="test_tracking",
            language="INVALID"
        )
        
        with pytest.raises(ConfigurationError, match="Invalid language"):
            config.validate()
    
    def test_config_validation_invalid_currency(self):
        """Test validation fails with invalid currency."""
        config = Config(
            app_key="test_key",
            app_secret="test_secret",
            tracking_id="test_tracking",
            currency="INVALID"
        )
        
        with pytest.raises(ConfigurationError, match="Invalid currency"):
            config.validate()
    
    def test_config_validation_invalid_port(self):
        """Test validation fails with invalid port."""
        config = Config(
            app_key="test_key",
            app_secret="test_secret",
            tracking_id="test_tracking",
            api_port=99999
        )
        
        with pytest.raises(ConfigurationError, match="api_port must be between"):
            config.validate()
    
    @patch.dict(os.environ, {
        'ALIEXPRESS_APP_KEY': 'env_test_key',
        'ALIEXPRESS_APP_SECRET': 'env_test_secret',
        'ALIEXPRESS_TRACKING_ID': 'env_test_tracking',
        'ALIEXPRESS_LANGUAGE': 'FR',
        'ALIEXPRESS_CURRENCY': 'EUR'
    })
    def test_config_from_env_success(self):
        """Test loading config from environment variables."""
        config = Config.from_env()
        
        assert config.app_key == "env_test_key"
        assert config.app_secret == "env_test_secret"
        assert config.tracking_id == "env_test_tracking"
        assert config.language == "FR"
        assert config.currency == "EUR"
    
    @patch.dict(os.environ, {}, clear=True)
    @patch('src.utils.config.load_dotenv')
    def test_config_from_env_missing_app_key(self, mock_load_dotenv):
        """Test loading config with missing app key uses graceful degradation.
        
        The Config.from_env() method now allows the app to start without credentials
        (for serverless environments), but validate() will raise an error.
        """
        mock_load_dotenv.return_value = None
        
        # Step 1: Config creation should succeed (graceful degradation)
        config = Config.from_env()
        assert config.app_key == 'MISSING_APP_KEY'  # Default placeholder
        
        # Step 2: Validation should fail with clear error message
        with pytest.raises(ConfigurationError, match="ALIEXPRESS_APP_KEY environment variable is required"):
            config.validate()
    
    @patch.dict(os.environ, {
        'ALIEXPRESS_APP_KEY': 'test_key'
    }, clear=True)
    @patch('src.utils.config.load_dotenv')
    def test_config_from_env_missing_app_secret(self, mock_load_dotenv):
        """Test loading config with missing app secret uses graceful degradation.
        
        The Config.from_env() method now allows the app to start without credentials
        (for serverless environments), but validate() will raise an error.
        """
        mock_load_dotenv.return_value = None
        
        # Step 1: Config creation should succeed (graceful degradation)
        config = Config.from_env()
        assert config.app_key == 'test_key'
        assert config.app_secret == 'MISSING_APP_SECRET'  # Default placeholder
        
        # Step 2: Validation should fail with clear error message
        with pytest.raises(ConfigurationError, match="ALIEXPRESS_APP_SECRET environment variable is required"):
            config.validate()
    
    @patch.dict(os.environ, {
        'ALIEXPRESS_APP_KEY': 'test_key',
        'ALIEXPRESS_APP_SECRET': 'test_secret',
        'API_PORT': '8080',
        'LOG_LEVEL': 'DEBUG'
    }, clear=True)
    def test_config_from_env_with_defaults(self):
        """Test loading config with default values."""
        config = Config.from_env()
        
        assert config.app_key == "test_key"
        assert config.app_secret == "test_secret"
        assert config.tracking_id == "gpt_chat"  # Default value
        assert config.api_port == 8080
        assert config.log_level == "DEBUG"