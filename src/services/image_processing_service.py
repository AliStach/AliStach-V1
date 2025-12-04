"""Image processing service for visual product search using CLIP embeddings."""

import hashlib
import logging
import io
import base64
from typing import Any, Optional, Dict, List
from PIL import Image
import numpy as np
import requests
from datetime import datetime

try:
    import clip
    import torch
    CLIP_AVAILABLE = True
except ImportError:
    CLIP_AVAILABLE = False
    logging.warning("CLIP not available. Install with: pip install torch torchvision clip-by-openai")

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
        
        # Only check CUDA if CLIP is available (torch was successfully imported)
        if CLIP_AVAILABLE:
            self.device: str = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device: Optional[str] = None
        
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
        
        # Initialize CLIP model if available
        if CLIP_AVAILABLE:
            self._initialize_clip_model()
    
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
        
        Args:
            image_input: Image URL or base64 encoded image data
            input_type: "url" or "base64"
            max_keywords: Maximum number of keywords to generate
            
        Returns:
            Dictionary with extracted features and search keywords
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
    
    async def _load_image(self, image_input: str, input_type: str) -> Optional[Image.Image]:
        """Load image from URL or base64 data."""
        try:
            if input_type == "url":
                response = requests.get(image_input, timeout=10)
                response.raise_for_status()
                image = Image.open(io.BytesIO(response.content))
            elif input_type == "base64":
                # Remove data URL prefix if present
                if image_input.startswith('data:image'):
                    image_input = image_input.split(',')[1]
                image_data = base64.b64decode(image_input)
                image = Image.open(io.BytesIO(image_data))
            else:
                raise ValueError(f"Unsupported input type: {input_type}")
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize if too large (for performance)
            max_size = 512
            if max(image.size) > max_size:
                image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            return image
            
        except Exception as e:
            logger.error(f"Failed to load image: {e}")
            return None
    
    async def _extract_visual_features(self, image: Image.Image) -> Dict[str, Any]:
        """Extract visual features from image using CLIP or fallback methods."""
        start_time = datetime.utcnow()
        
        if not CLIP_AVAILABLE or not self.model:
            # Fallback to basic image analysis
            return await self._extract_basic_features(image)
        
        try:
            # Preprocess image for CLIP
            image_tensor = self.preprocess(image).unsqueeze(0).to(self.device)
            
            # Generate image embedding
            with torch.no_grad():
                image_features = self.model.encode_image(image_tensor)
                image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            
            # Convert to numpy for easier processing
            embedding = image_features.cpu().numpy().flatten()
            
            # Analyze image with text prompts to extract semantic features
            semantic_features = await self._analyze_with_text_prompts(image_tensor)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return {
                'embedding': embedding.tolist(),
                'semantic_features': semantic_features,
                'dominant_colors': self._extract_dominant_colors(image),
                'image_size': image.size,
                'confidence': 0.85,  # CLIP generally has high confidence
                'processing_time': processing_time,
                'method': 'clip'
            }
            
        except Exception as e:
            logger.error(f"CLIP feature extraction failed: {e}")
            return await self._extract_basic_features(image)
    
    async def _analyze_with_text_prompts(self, image_tensor: Any) -> Dict[str, float]:
        """Analyze image using CLIP text-image similarity."""
        try:
            # Define text prompts for different product categories and styles
            prompts = [
                "a piece of clothing", "fashion apparel", "shirt", "dress", "pants",
                "electronic device", "smartphone", "laptop", "headphones", "gadget",
                "home decoration", "furniture", "kitchen item", "tool",
                "jewelry", "watch", "accessory", "bag", "shoes",
                "toy", "game", "book", "sports equipment",
                "modern style", "vintage style", "luxury item", "casual wear",
                "colorful", "black and white", "metallic", "wooden", "plastic"
            ]
            
            # Tokenize text prompts
            text_tokens = clip.tokenize(prompts).to(self.device)
            
            # Get text features
            with torch.no_grad():
                text_features = self.model.encode_text(text_tokens)
                text_features = text_features / text_features.norm(dim=-1, keepdim=True)
                
                # Calculate similarities
                image_features = self.model.encode_image(image_tensor)
                image_features = image_features / image_features.norm(dim=-1, keepdim=True)
                
                similarities = (image_features @ text_features.T).squeeze(0)
                similarities = torch.softmax(similarities, dim=0)
            
            # Create feature dictionary
            semantic_features = {}
            for i, prompt in enumerate(prompts):
                semantic_features[prompt] = float(similarities[i])
            
            return semantic_features
            
        except Exception as e:
            logger.error(f"Text prompt analysis failed: {e}")
            return {}
    
    async def _extract_basic_features(self, image: Image.Image) -> Dict[str, Any]:
        """Fallback method for basic image feature extraction without CLIP."""
        start_time = datetime.utcnow()
        
        try:
            # Basic color analysis
            dominant_colors = self._extract_dominant_colors(image)
            
            # Simple image properties
            width, height = image.size
            aspect_ratio = width / height
            
            # Basic semantic guessing based on image properties
            semantic_features = {
                'rectangular_object': 0.7 if 0.5 < aspect_ratio < 2.0 else 0.3,
                'square_object': 0.8 if 0.9 < aspect_ratio < 1.1 else 0.2,
                'colorful': 0.8 if len(dominant_colors) > 3 else 0.4,
                'simple_design': 0.6 if len(dominant_colors) <= 2 else 0.3
            }
            
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return {
                'embedding': None,  # No embedding available
                'semantic_features': semantic_features,
                'dominant_colors': dominant_colors,
                'image_size': image.size,
                'aspect_ratio': aspect_ratio,
                'confidence': 0.5,  # Lower confidence for basic analysis
                'processing_time': processing_time,
                'method': 'basic'
            }
            
        except Exception as e:
            logger.error(f"Basic feature extraction failed: {e}")
            return {
                'embedding': None,
                'semantic_features': {},
                'dominant_colors': [],
                'confidence': 0.3,
                'method': 'fallback'
            }
    
    def _extract_dominant_colors(self, image: Image.Image, num_colors: int = 5) -> List[str]:
        """Extract dominant colors from image."""
        try:
            # Resize image for faster processing
            image_small = image.resize((50, 50))
            
            # Convert to numpy array
            pixels = np.array(image_small).reshape(-1, 3)
            
            # Simple color clustering (k-means alternative)
            from collections import Counter
            
            # Quantize colors to reduce complexity
            quantized_pixels = (pixels // 32) * 32
            
            # Count color frequencies
            color_counts = Counter(map(tuple, quantized_pixels))
            
            # Get most common colors
            dominant_colors = []
            for (r, g, b), count in color_counts.most_common(num_colors):
                color_name = self._rgb_to_color_name(r, g, b)
                if color_name and color_name not in dominant_colors:
                    dominant_colors.append(color_name)
            
            return dominant_colors[:3]  # Return top 3 colors
            
        except Exception as e:
            logger.error(f"Color extraction failed: {e}")
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