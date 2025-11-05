"""Base class for AliExpress API service modules."""

import logging
import time
import hashlib
import hmac
import json
from typing import Dict, Any, Optional
from ...utils.config import Config

logger = logging.getLogger(__name__)


class RestApi:
    """Base class for AliExpress API service modules."""
    
    def __init__(self, domain: str = "api-sg.aliexpress.com", port: int = 80):
        """Initialize the REST API base class."""
        self.domain = domain
        self.port = port
        self.protocol = "https" if port == 443 else "http"
        self.config: Optional[Config] = None
        
        # Common parameters that will be set by child classes
        self.app_signature = None
        self.tracking_id = None
        
    def set_config(self, config: Config):
        """Set the configuration for API calls."""
        self.config = config
        self.tracking_id = config.tracking_id
        
    def getapiname(self) -> str:
        """Get the API method name. Must be implemented by child classes."""
        raise NotImplementedError("Child classes must implement getapiname()")
    
    def get_api_url(self) -> str:
        """Get the full API URL."""
        return f"{self.protocol}://{self.domain}/sync"
    
    def _generate_signature(self, params: Dict[str, Any], app_secret: str) -> str:
        """Generate API signature for AliExpress API calls."""
        # Sort parameters
        sorted_params = sorted(params.items())
        
        # Create query string
        query_string = ''.join([f'{k}{v}' for k, v in sorted_params])
        
        # Create signature string
        sign_string = app_secret + query_string + app_secret
        
        # Generate SHA256 hash
        signature = hashlib.sha256(sign_string.encode('utf-8')).hexdigest().upper()
        
        return signature
    
    def _prepare_common_params(self) -> Dict[str, Any]:
        """Prepare common parameters for API calls."""
        if not self.config:
            raise ValueError("Configuration not set. Call set_config() first.")
            
        return {
            'method': self.getapiname(),
            'app_key': self.config.app_key,
            'timestamp': str(int(time.time() * 1000)),
            'format': 'json',
            'v': '2.0',
            'sign_method': 'sha256',
            'tracking_id': self.config.tracking_id
        }
    
    def _prepare_request_params(self) -> Dict[str, Any]:
        """Prepare all parameters for the API request."""
        # Get common parameters
        params = self._prepare_common_params()
        
        # Add specific parameters from the instance
        for attr_name in dir(self):
            if not attr_name.startswith('_') and not callable(getattr(self, attr_name)):
                attr_value = getattr(self, attr_name)
                if attr_value is not None and attr_name not in ['domain', 'port', 'protocol', 'config']:
                    params[attr_name] = attr_value
        
        return params
    
    def execute(self) -> Dict[str, Any]:
        """Execute the API request."""
        import requests
        
        if not self.config:
            raise ValueError("Configuration not set. Call set_config() first.")
        
        try:
            # Prepare parameters
            params = self._prepare_request_params()
            
            # Generate signature
            signature = self._generate_signature(params, self.config.app_secret)
            params['sign'] = signature
            
            # Make API request
            url = self.get_api_url()
            logger.debug(f"Making API request to {url} with method {self.getapiname()}")
            
            response = requests.post(url, data=params, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            # Check for API errors
            if 'error_response' in result:
                error_info = result['error_response']
                error_msg = error_info.get('msg', 'Unknown API error')
                error_code = error_info.get('code', 'unknown')
                raise Exception(f"AliExpress API error ({error_code}): {error_msg}")
            
            logger.debug(f"API request successful for {self.getapiname()}")
            return result
            
        except requests.RequestException as e:
            logger.error(f"Network error during API request: {e}")
            raise Exception(f"Network error: {e}")
        except Exception as e:
            logger.error(f"API request failed: {e}")
            raise