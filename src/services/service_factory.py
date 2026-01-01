"""Service factory for creating AliExpress service instances based on environment."""

import logging
from datetime import datetime
from dataclasses import dataclass
from typing import Union, Optional
from ..utils.config import Config
from ..utils.environment_detector import EnvironmentDetector
from .aliexpress_service import AliExpressService
from .service_capability_detector import ServiceCapabilityDetector

logger = logging.getLogger(__name__)


@dataclass
class ServiceCapabilities:
    """Service capability information."""
    has_smart_search: bool
    has_caching: bool
    has_image_processing: bool
    supports_affiliate_links: bool
    environment_type: str


@dataclass
class ServiceWithMetadata:
    """Service instance with capability metadata."""
    service: Union[AliExpressService, object]
    capabilities: ServiceCapabilities
    service_type: str
    created_at: datetime


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
        env_info = EnvironmentDetector.get_environment_info()
        
        # Log detailed environment detection results
        logger.info(f"Environment detection: is_serverless={env_info['is_serverless']}, "
                   f"enhanced_features_enabled={env_info['enhanced_features_enabled']}, "
                   f"explicit_config={env_info['explicit_config']}")
        
        # Check if we should use enhanced features
        use_enhanced = (
            not force_basic and 
            EnvironmentDetector.should_enable_enhanced_features() and
            EnhancedServiceLoader.is_available()
        )
        
        logger.info(f"Service creation decision: enhanced_enabled={env_info['enhanced_features_enabled']}, "
                   f"enhanced_available={EnhancedServiceLoader.is_available()}, "
                   f"force_basic={force_basic}, use_enhanced={use_enhanced}")
        
        # Log the reasoning behind service selection
        if force_basic:
            logger.info("Service selection: Forced to use basic service")
        elif not env_info['enhanced_features_enabled']:
            logger.info(f"Service selection: Enhanced features disabled in {env_info.get('environment_indicators', {})}")
        elif not EnhancedServiceLoader.is_available():
            logger.info("Service selection: Enhanced service dependencies not available")
        else:
            logger.info("Service selection: All conditions met for enhanced service")
        
        if use_enhanced:
            try:
                enhanced_service = EnhancedServiceLoader.load_enhanced_service(config)
                logger.info("✅ Created enhanced AliExpress service with caching and image processing")
                logger.info(f"Enhanced service capabilities: smart_search=True, caching=True, "
                           f"environment={env_info['environment_indicators']}")
                return enhanced_service
            except Exception as e:
                logger.warning(f"❌ Failed to create enhanced service, falling back to basic: {e}")
                logger.info("Fallback reason: Enhanced service initialization failed")
        
        # Create basic service
        basic_service = AliExpressService(config)
        logger.info("✅ Created basic AliExpress service")
        logger.info(f"Basic service capabilities: smart_search=False, caching=False, "
                   f"fallback_required=True")
        return basic_service
    
    @staticmethod
    def create_aliexpress_service_with_metadata(config: Config, 
                                              force_basic: bool = False) -> ServiceWithMetadata:
        """
        Create AliExpress service with capability metadata.
        
        Args:
            config: AliExpress API configuration
            force_basic: Force creation of basic service even if enhanced is available
            
        Returns:
            ServiceWithMetadata instance with service and capability information
        """
        # Create the service
        service = ServiceFactory.create_aliexpress_service(config, force_basic)
        
        # Get service capabilities
        capabilities = ServiceFactory.get_service_capabilities(service)
        
        # Get service type
        service_type = ServiceCapabilityDetector.get_service_type(service)
        
        # Get environment info
        env_info = EnvironmentDetector.get_environment_info()
        
        logger.info(f"📊 Created service with metadata: type={service_type}, "
                   f"smart_search={capabilities.has_smart_search}, "
                   f"caching={capabilities.has_caching}, "
                   f"environment={env_info['is_serverless']}")
        
        # Log detailed capability breakdown for debugging
        logger.debug(f"Service capabilities breakdown: {capabilities.__dict__}")
        logger.debug(f"Environment details: {env_info}")
        
        return ServiceWithMetadata(
            service=service,
            capabilities=capabilities,
            service_type=service_type,
            created_at=datetime.utcnow()
        )
    
    @staticmethod
    def get_service_capabilities(service) -> ServiceCapabilities:
        """
        Get detailed capability information for a service instance.
        
        Args:
            service: Service instance to analyze
            
        Returns:
            ServiceCapabilities with detailed capability information
        """
        capabilities_dict = ServiceCapabilityDetector.get_capabilities(service)
        env_info = EnvironmentDetector.get_environment_info()
        
        return ServiceCapabilities(
            has_smart_search=capabilities_dict['has_smart_search'],
            has_caching=capabilities_dict['has_caching'],
            has_image_processing=capabilities_dict['has_image_processing'],
            supports_affiliate_links=capabilities_dict['supports_affiliate_links'],
            environment_type='serverless' if env_info['is_serverless'] else 'local'
        )
    
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