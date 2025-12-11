"""Environment detection utilities for serverless and deployment environments."""

import os
from typing import Dict, Any


class EnvironmentDetector:
    """Utility class for detecting deployment environment and capabilities."""
    
    @staticmethod
    def is_serverless() -> bool:
        """
        Detect if running in a serverless environment.
        
        Returns:
            True if running in serverless environment (Vercel, AWS Lambda, etc.)
        """
        serverless_indicators = [
            os.getenv('VERCEL') == '1',
            os.getenv('AWS_LAMBDA_FUNCTION_NAME') is not None,
            os.getenv('FUNCTIONS_WORKER_RUNTIME') is not None,  # Azure Functions
            os.getenv('K_SERVICE') is not None,  # Google Cloud Run
            os.getenv('RAILWAY_ENVIRONMENT') is not None,  # Railway
        ]
        
        return any(serverless_indicators)
    
    @staticmethod
    def should_enable_enhanced_features() -> bool:
        """
        Determine if enhanced features should be enabled.
        
        Enhanced features are disabled in serverless environments by default
        but can be force-enabled via environment variable.
        
        Returns:
            True if enhanced features should be enabled
        """
        # Check explicit override first
        explicit_enable = os.getenv('ENABLE_ENHANCED_FEATURES', '').lower()
        if explicit_enable in ('true', '1', 'yes'):
            return True
        elif explicit_enable in ('false', '0', 'no'):
            return False
        
        # Auto-detect: disable in serverless environments
        return not EnvironmentDetector.is_serverless()
    
    @staticmethod
    def get_environment_info() -> Dict[str, Any]:
        """
        Get comprehensive environment information.
        
        Returns:
            Dictionary with environment details
        """
        return {
            'is_serverless': EnvironmentDetector.is_serverless(),
            'enhanced_features_enabled': EnvironmentDetector.should_enable_enhanced_features(),
            'environment_indicators': {
                'vercel': os.getenv('VERCEL'),
                'aws_lambda': bool(os.getenv('AWS_LAMBDA_FUNCTION_NAME')),
                'azure_functions': bool(os.getenv('FUNCTIONS_WORKER_RUNTIME')),
                'google_cloud_run': bool(os.getenv('K_SERVICE')),
                'railway': bool(os.getenv('RAILWAY_ENVIRONMENT')),
            },
            'explicit_config': os.getenv('ENABLE_ENHANCED_FEATURES', 'auto'),
        }