"""Service factory for creating AliExpress service instances based on environment."""

import logging
from typing import Union, Optional
from ..utils.config import Config
from ..utils.environment_detector import EnvironmentDetector
from .aliexpress_service import AliExpressService

logger = logging.getLogger(__name__)


class EnhancedServiceLoader:
    """Loader for enhanced AliExpress service with heavy dependencies."""
    
    @staticmethod
    def is_available() -> bool:
        """
        Check if enhanced service dependencies are available.
        
        Returns:
            True if enhanced service can be loaded
        """
        try:
            # Try importing enhanced service without triggering heavy imports
            from .enhanced_aliexpress_service import EnhancedAliExpressService
            return True
        except ImportError as e:
            logger.debug(f"Enhanced service not available: {e}")
            return False
    
    @staticmethod
    def load_enhanced_service(config: Config, cache_config: Optional[object] = None):
        """
        Load enhanced service with heavy dependencies.
        
        Args:
            config: AliExpress API configuration
            cache_config: Optional cache configuration
            
        Returns:
            EnhancedAliExpressService instance
            
        Raises:
            ImportError: If enhanced service cannot be loaded
        """
        try:
            from .enhanced_aliexpress_service import EnhancedAliExpressService
            from .cache_config import CacheConfig
            
            if cache_config is None:
                cache_config = CacheConfig.from_env()
            
            return EnhancedAliExpressService(config, cache_config)
        except ImportError as e:
            logger.error(f"Failed to load enhanced service: {e}")
            raise


class ServiceFactory:
    """Factory for creating appropriate AliExpress service instances."""
    
    @staticmethod
    def create_aliexpress_service(config: Config, 
                                force_basic: bool = False) -> Union[AliExpressService, object]:
        """
        Create appropriate AliExpress service based on environment and configuration.
        
        Args:
            config: AliExpress API configuration
            force_basic: Force creation of basic service even if enhanced is available
            
        Returns:
            AliExpressService or EnhancedAliExpressService instance
        """
        # Check if we should use enhanced features
        use_enhanced = (
            not force_basic and 
            EnvironmentDetector.should_enable_enhanced_features() and
            EnhancedServiceLoader.is_available()
        )
        
        if use_enhanced:
            try:
                enhanced_service = EnhancedServiceLoader.load_enhanced_service(config)
                logger.info("Created enhanced AliExpress service with caching and image processing")
                return enhanced_service
            except Exception as e:
                logger.warning(f"Failed to create enhanced service, falling back to basic: {e}")
        
        # Create basic service
        basic_service = AliExpressService(config)
        logger.info("Created basic AliExpress service")
        return basic_service
    
    @staticmethod
    def get_service_info() -> dict:
        """
        Get information about available services and current environment.
        
        Returns:
            Dictionary with service availability information
        """
        env_info = EnvironmentDetector.get_environment_info()
        enhanced_available = EnhancedServiceLoader.is_available()
        
        return {
            'environment': env_info,
            'services': {
                'basic_available': True,
                'enhanced_available': enhanced_available,
                'recommended_service': 'enhanced' if enhanced_available and env_info['enhanced_features_enabled'] else 'basic'
            }
        }