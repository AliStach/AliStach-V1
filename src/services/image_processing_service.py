"""Image processing service for visual product search using CLIP embeddings."""

import hashlib
import logging
import io
import base64
from typing import Any, Optional, Dict, List
import requests
from datetime import datetime

# Heavy ML imports are DISABLED for Vercel compatibility
# These libraries (torch, clip, PIL, numpy) exceed Vercel's 250MB deployment limit
# and cause cold start timeouts. Image processing features are temporarily disabled.
CLIP_AVAILABLE = False
HEAVY_IMPORTS_DISABLED = True

# Lazy imports - only load if explicitly enabled via environment variable
def _lazy_import_heavy_libs():
    """Lazy import of heavy ML libraries - only when explicitly needed."""
    import os
    if os.getenv("ENABLE_IMAGE_PROCESSING", "false").lower() != "true":
        return None, None, None, None, False
    
    try:
        from PIL import Image
        import numpy as np
        import clip
        import torch
        return Image, np, clip, torch, True
    except ImportError as e:
        logging.warning(f"Heavy ML libraries not available: {e}")
        return None, None, None, None, False

from .cache_service import CacheService

logger = logging.getLogger(__name__)

class ImageProcessingService:
    """
    Service for processing images and extracting visual features for product search.
    
    Uses CLIP (Contrastive Language-Image Pre-training) to convert images into
    embeddings that can be matched against product descriptions and categories.
    """
    
    def __init__(self, cache_service: Optional[CacheService] = None) -> None:
        self.cache_service: Optional[CacheService] = cache_service
        self.model: Optional[Any] = None
        self.preprocess: Optional[Any] = None
        self.device: Optional[str] = None
        
        # Heavy ML features are disabled for Vercel compatibility
        # Image processing will return feature-disabled errors
        
        # Visual feature to keyword mappings
        self.color_keywords: Dict[str, List[str]] = {
            'red': ['red', 'crimson', 'scarlet', 'burgundy'],
            'blue': ['blue', 'navy', 'azure', 'cobalt'],
            'green': ['green', 'emerald', 'olive', 'mint'],
            'black': ['black', 'dark', 'charcoal'],
            'white': ['white', 'ivory', 'cream'],
            'yellow': ['yellow', 'gold', 'amber'],
            'pink': ['pink', 'rose', 'magenta'],
            'purple': ['purple', 'violet', 'lavender'],
            'orange': ['orange', 'coral', 'peach'],
            'brown': ['brown', 'tan', 'beige', 'khaki']
        }
        
        self.style_keywords: Dict[str, List[str]] = {
            'modern': ['modern', 'contemporary', 'sleek', 'minimalist'],
            'vintage': ['vintage', 'retro', 'classic', 'antique'],
            'casual': ['casual', 'everyday', 'comfortable', 'relaxed'],
            'formal': ['formal', 'elegant', 'sophisticated', 'professional'],
            'sporty': ['sport', 'athletic', 'active', 'fitness'],
            'luxury': ['luxury', 'premium', 'high-end', 'designer']
        }
        
        # CLIP model initialization disabled for Vercel compatibility
        # Image processing features are temporarily unavailable
    
    def _initialize_clip_model(self) -> None:
        """Initialize CLIP model for image processing."""
        try:
            self.model, self.preprocess = clip.load("ViT-B/32", device=self.device)
            logger.info(f"CLIP model initialized successfully on {self.device}")
        except Exception as e:
            logger.error(f"Failed to initialize CLIP model: {e}")
            self.model = None
            self.preprocess = None
    
    async def process_image_for_search(self, 
                                     image_input: str, 
                                     input_type: str = "url",
                                     max_keywords: int = 10) -> Dict[str, Any]:
        """
        Process image and extract search-relevant features.
        
        NOTE: Image processing features are temporarily disabled for Vercel compatibility.
        Heavy ML libraries (PyTorch, CLIP, Pillow, Numpy) exceed serverless limits.
        
        Args:
            image_input: Image URL or base64 encoded image data
            input_type: "url" or "base64"
            max_keywords: Maximum number of keywords to generate
            
        Returns:
            Dictionary with extracted features and search keywords
        """
        # Image processing is disabled for Vercel compatibility
        raise ValueError(
            "Image processing features are temporarily disabled. "
            "Heavy ML libraries (PyTorch, CLIP) are incompatible with Vercel's serverless environment. "
            "Please use text-based search instead."
        )
        
        # Original implementation preserved below for future re-enablement
        """
        try:
            # Generate image hash for caching
            image_hash = self._generate_image_hash(image_input, input_type)
            
            # Check cache first
            if self.cache_service:
                cached_result = await self._get_cached_image_features(image_hash)
                if cached_result:
                    logger.info(f"Using cached image features for hash: {image_hash}")
                    return cached_result
            
            # Load and preprocess image
            image = await self._load_image(image_input, input_type)
            if not image:
                raise ValueError("Failed to load image")
            
            # Extract visual features
            features = await self._extract_visual_features(image)
            
            # Generate search keywords from features
            keywords = self._generate_search_keywords(features, max_keywords)
            
            # Determine likely product categories
            categories = self._predict_product_categories(features)
            
            result = {
                'image_hash': image_hash,
                'extracted_features': features,
                'search_keywords': keywords,
                'predicted_categories': categories,
                'confidence_score': features.get('confidence', 0.7),
                'processing_time_ms': features.get('processing_time', 0),
                'created_at': datetime.utcnow().isoformat()
            }
            
            # Cache the result
            if self.cache_service:
                await self._cache_image_features(image_hash, result)
            
            logger.info(f"Image processed successfully. Keywords: {keywords[:3]}...")
            return result
            
        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            raise ValueError(f"Image processing failed: {e}")
        """
    
    async def _load_image(self, image_input: str, input_type: str) -> Optional[Any]:
        """Load image from URL or base64 data. DISABLED for Vercel compatibility."""
        raise NotImplementedError("Image loading disabled for Vercel compatibility")
    
    async def _extract_visual_features(self, image: Any) -> Dict[str, Any]:
        """Extract visual features from image. DISABLED for Vercel compatibility."""
        raise NotImplementedError("Visual feature extraction disabled for Vercel compatibility")
    
    async def _analyze_with_text_prompts(self, image_tensor: Any) -> Dict[str, float]:
        """Analyze image using CLIP. DISABLED for Vercel compatibility."""
        raise NotImplementedError("CLIP analysis disabled for Vercel compatibility")
    
    async def _extract_basic_features(self, image: Any) -> Dict[str, Any]:
        """Basic feature extraction. DISABLED for Vercel compatibility."""
        raise NotImplementedError("Basic feature extraction disabled for Vercel compatibility")
    
    def _extract_dominant_colors(self, image: Any, num_colors: int = 5) -> List[str]:
        """Extract dominant colors. DISABLED for Vercel compatibility."""
        return []
    
    def _rgb_to_color_name(self, r: int, g: int, b: int) -> Optional[str]:
        """Convert RGB values to color name."""
        # Simple color mapping based on RGB values
        if r > 200 and g < 100 and b < 100:
            return 'red'
        elif r < 100 and g < 100 and b > 200:
            return 'blue'
        elif r < 100 and g > 200 and b < 100:
            return 'green'
        elif r > 200 and g > 200 and b < 100:
            return 'yellow'
        elif r > 200 and g < 150 and b > 200:
            return 'pink'
        elif r < 100 and g > 150 and b > 200:
            return 'purple'
        elif r > 200 and g > 150 and b < 100:
            return 'orange'
        elif r < 50 and g < 50 and b < 50:
            return 'black'
        elif r > 200 and g > 200 and b > 200:
            return 'white'
        elif r > 100 and g > 50 and b < 50:
            return 'brown'
        else:
            return None
    
    def _generate_search_keywords(self, features: Dict[str, Any], max_keywords: int) -> List[str]:
        """Generate search keywords from extracted visual features."""
        keywords = []
        
        # Add color keywords
        dominant_colors = features.get('dominant_colors', [])
        for color in dominant_colors[:2]:  # Top 2 colors
            if color in self.color_keywords:
                keywords.extend(self.color_keywords[color][:2])
        
        # Add semantic keywords based on CLIP analysis
        semantic_features = features.get('semantic_features', {})
        
        # Sort by confidence and add top features
        sorted_features = sorted(semantic_features.items(), key=lambda x: x[1], reverse=True)
        
        for feature_name, confidence in sorted_features[:5]:
            if confidence > 0.3:  # Only include confident predictions
                # Convert feature names to search keywords
                if 'clothing' in feature_name or 'apparel' in feature_name:
                    keywords.extend(['clothing', 'fashion', 'apparel'])
                elif 'electronic' in feature_name or 'device' in feature_name:
                    keywords.extend(['electronics', 'gadget', 'device'])
                elif 'jewelry' in feature_name:
                    keywords.extend(['jewelry', 'accessory'])
                elif 'home' in feature_name or 'furniture' in feature_name:
                    keywords.extend(['home', 'decor', 'furniture'])
                elif 'luxury' in feature_name:
                    keywords.extend(['premium', 'luxury', 'high-quality'])
                elif 'modern' in feature_name:
                    keywords.extend(['modern', 'contemporary'])
                elif 'vintage' in feature_name:
                    keywords.extend(['vintage', 'retro', 'classic'])
        
        # Remove duplicates and limit to max_keywords
        unique_keywords = list(dict.fromkeys(keywords))  # Preserve order
        return unique_keywords[:max_keywords]
    
    def _predict_product_categories(self, features: Dict[str, Any]) -> List[str]:
        """Predict likely product categories based on visual features."""
        categories = []
        semantic_features = features.get('semantic_features', {})
        
        # Category mapping based on semantic features
        category_mappings = {
            'clothing': ['1', '200001996'],  # Fashion categories
            'electronics': ['502', '200216143'],  # Electronics categories
            'jewelry': ['1509', '200000297'],  # Jewelry categories
            'home': ['1503', '200001075'],  # Home & Garden categories
            'sports': ['18', '200003482'],  # Sports categories
        }
        
        # Find best matching categories
        for feature_name, confidence in semantic_features.items():
            if confidence > 0.4:
                for category_key, category_ids in category_mappings.items():
                    if category_key in feature_name.lower():
                        categories.extend(category_ids)
        
        return list(set(categories))[:3]  # Return top 3 unique categories
    
    def _generate_image_hash(self, image_input: str, input_type: str) -> str:
        """Generate hash for image caching."""
        # Create hash based on image input
        hash_input = f"{input_type}:{image_input}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]
    
    async def _get_cached_image_features(self, image_hash: str) -> Optional[Dict[str, Any]]:
        """Get cached image features if available."""
        if not self.cache_service or not self.cache_service.redis_client:
            return None
        
        try:
            redis_key = f"image_features:{image_hash}"
            cached_data = self.cache_service.redis_client.get(redis_key)
            if cached_data:
                import json
                return json.loads(cached_data)
        except Exception as e:
            logger.error(f"Failed to get cached image features: {e}")
        
        return None
    
    async def _cache_image_features(self, image_hash: str, features: Dict[str, Any]) -> None:
        """Cache image features for future use."""
        if not self.cache_service or not self.cache_service.redis_client:
            return
        
        try:
            redis_key = f"image_features:{image_hash}"
            # Cache for 24 hours (image features are relatively stable)
            ttl = 86400
            import json
            self.cache_service.redis_client.setex(
                redis_key,
                ttl,
                json.dumps(features, default=str)
            )
            logger.debug(f"Cached image features for hash: {image_hash}")
        except Exception as e:
            logger.error(f"Failed to cache image features: {e}")