"""Utility functions for API signature generation."""

import hashlib
from typing import Any, Dict

def generate_api_signature(params: Dict[str, Any], app_secret: str) -> str:
    """
    Generate API signature for AliExpress API calls.
    
    Args:
        params: Dictionary of API parameters
        app_secret: Application secret key
        
    Returns:
        SHA256 signature string in uppercase
    """
    # Sort parameters
    sorted_params = sorted(params.items())
    
    # Create query string
    query_string = ''.join([f'{k}{v}' for k, v in sorted_params])
    
    # Create signature string
    sign_string = app_secret + query_string + app_secret
    
    # Generate SHA256 hash
    signature = hashlib.sha256(sign_string.encode('utf-8')).hexdigest().upper()
    
    return signature
