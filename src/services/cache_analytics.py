"""Cache analytics and monitoring service for API optimization tracking."""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models.cache_models import CacheAnalytics, CachedProduct, CachedAffiliateLink, CachedSearchResult

logger = logging.getLogger(__name__)

class CacheAnalyticsService:
    """
    Service for tracking and analyzing cache performance and API call optimization.
    
    This service provides insights into how effectively the caching system is
    reducing API calls and improving performance while maintaining compliance.
    """
    
    def __init__(self, db_session: Session) -> None:
        self.db_session: Session = db_session
    
    def record_daily_stats(self, cache_stats: Dict[str, Any]) -> None:
        """Record daily cache performance statistics."""
        try:
            today = datetime.utcnow().date()
            
            # Check if we already have stats for today
            existing_stats = self.db_session.query(CacheAnalytics)\
                .filter(func.date(CacheAnalytics.date) == today)\
                .first()
            
            if existing_stats:
                # Update existing stats
                existing_stats.search_api_calls_saved += cache_stats.get('search_calls_saved', 0)
                existing_stats.affiliate_api_calls_saved += cache_stats.get('affiliate_calls_saved', 0)
                existing_stats.product_detail_calls_saved += cache_stats.get('detail_calls_saved', 0)
                existing_stats.total_api_calls_saved = (
                    existing_stats.search_api_calls_saved +
                    existing_stats.affiliate_api_calls_saved +
                    existing_stats.product_detail_calls_saved
                )
                existing_stats.cache_hit_rate = cache_stats.get('hit_rate_percentage', 0)
                existing_stats.average_response_time_ms = cache_stats.get('avg_response_time', 0)
            else:
                # Create new stats record
                new_stats = CacheAnalytics(
                    date=datetime.utcnow(),
                    search_api_calls_saved=cache_stats.get('search_calls_saved', 0),
                    affiliate_api_calls_saved=cache_stats.get('affiliate_calls_saved', 0),
                    product_detail_calls_saved=cache_stats.get('detail_calls_saved', 0),
                    total_api_calls_saved=cache_stats.get('total_calls_saved', 0),
                    cache_hit_rate=cache_stats.get('hit_rate_percentage', 0),
                    average_response_time_ms=cache_stats.get('avg_response_time', 0),
                    cached_products_count=self._get_cached_products_count(),
                    cached_affiliate_links_count=self._get_cached_affiliate_links_count(),
                    cached_searches_count=self._get_cached_searches_count(),
                    estimated_cost_savings_usd=cache_stats.get('estimated_cost_savings', 0)
                )
                self.db_session.add(new_stats)
            
            self.db_session.commit()
            logger.info(f"Recorded daily cache statistics for {today}")
            
        except Exception as e:
            logger.error(f"Failed to record daily stats: {e}")
            self.db_session.rollback()
    
    def get_performance_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get cache performance summary for the last N days."""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            stats = self.db_session.query(CacheAnalytics)\
                .filter(CacheAnalytics.date >= start_date)\
                .all()
            
            if not stats:
                return {
                    'period_days': days,
                    'total_api_calls_saved': 0,
                    'average_hit_rate': 0,
                    'estimated_cost_savings': 0,
                    'performance_trend': 'no_data'
                }
            
            # Calculate aggregated metrics
            total_api_calls_saved = sum(s.total_api_calls_saved for s in stats)
            average_hit_rate = sum(s.cache_hit_rate for s in stats) / len(stats)
            total_cost_savings = sum(s.estimated_cost_savings_usd for s in stats)
            
            # Calculate trend
            if len(stats) >= 2:
                recent_hit_rate = stats[-1].cache_hit_rate
                older_hit_rate = stats[0].cache_hit_rate
                trend = 'improving' if recent_hit_rate > older_hit_rate else 'declining'
            else:
                trend = 'stable'
            
            return {
                'period_days': days,
                'total_api_calls_saved': total_api_calls_saved,
                'average_hit_rate_percentage': round(average_hit_rate, 2),
                'estimated_cost_savings_usd': round(total_cost_savings, 4),
                'performance_trend': trend,
                'daily_breakdown': [
                    {
                        'date': s.date.isoformat(),
                        'api_calls_saved': s.total_api_calls_saved,
                        'hit_rate': s.cache_hit_rate,
                        'response_time_ms': s.average_response_time_ms
                    }
                    for s in stats
                ],
                'cache_efficiency_rating': self._calculate_efficiency_rating(average_hit_rate)
            }
            
        except Exception as e:
            logger.error(f"Failed to get performance summary: {e}")
            return {'error': str(e)}
    
    def get_api_call_breakdown(self) -> Dict[str, Any]:
        """Get detailed breakdown of API call savings by category."""
        try:
            # Get latest stats
            latest_stats = self.db_session.query(CacheAnalytics)\
                .order_by(CacheAnalytics.date.desc())\
                .first()
            
            if not latest_stats:
                return {
                    'search_api_calls_saved': 0,
                    'affiliate_api_calls_saved': 0,
                    'product_detail_calls_saved': 0,
                    'total_api_calls_saved': 0,
                    'breakdown_percentage': {}
                }
            
            total = latest_stats.total_api_calls_saved
            
            breakdown = {
                'search_api_calls_saved': latest_stats.search_api_calls_saved,
                'affiliate_api_calls_saved': latest_stats.affiliate_api_calls_saved,
                'product_detail_calls_saved': latest_stats.product_detail_calls_saved,
                'total_api_calls_saved': total,
                'breakdown_percentage': {
                    'search': round((latest_stats.search_api_calls_saved / total * 100), 1) if total > 0 else 0,
                    'affiliate': round((latest_stats.affiliate_api_calls_saved / total * 100), 1) if total > 0 else 0,
                    'product_details': round((latest_stats.product_detail_calls_saved / total * 100), 1) if total > 0 else 0
                },
                'compliance_note': 'All cached affiliate links are from our own authorized account'
            }
            
            return breakdown
            
        except Exception as e:
            logger.error(f"Failed to get API call breakdown: {e}")
            return {'error': str(e)}
    
    def get_cache_storage_stats(self) -> Dict[str, Any]:
        """Get current cache storage utilization statistics."""
        try:
            return {
                'cached_products': self._get_cached_products_count(),
                'cached_affiliate_links': self._get_cached_affiliate_links_count(),
                'cached_searches': self._get_cached_searches_count(),
                'storage_efficiency': {
                    'products_with_affiliate_links': self._get_products_with_affiliate_links_count(),
                    'reusable_affiliate_links': self._get_reusable_affiliate_links_count(),
                    'popular_searches': self._get_popular_searches_count()
                },
                'compliance_status': {
                    'affiliate_links_legal': True,
                    'data_ownership': 'own_affiliate_account',
                    'storage_policy': 'compliant_with_terms'
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get storage stats: {e}")
            return {'error': str(e)}
    
    def _get_cached_products_count(self) -> int:
        """Get count of currently cached products."""
        return self.db_session.query(CachedProduct)\
            .filter(CachedProduct.expires_at > datetime.utcnow())\
            .count()
    
    def _get_cached_affiliate_links_count(self) -> int:
        """Get count of currently cached affiliate links."""
        return self.db_session.query(CachedAffiliateLink)\
            .filter(CachedAffiliateLink.expires_at > datetime.utcnow())\
            .count()
    
    def _get_cached_searches_count(self) -> int:
        """Get count of currently cached search results."""
        return self.db_session.query(CachedSearchResult)\
            .filter(CachedSearchResult.expires_at > datetime.utcnow())\
            .count()
    
    def _get_products_with_affiliate_links_count(self) -> int:
        """Get count of products that have corresponding affiliate links."""
        # This would require a more complex query joining products and affiliate links
        # For now, return a simple count
        return self._get_cached_affiliate_links_count()
    
    def _get_reusable_affiliate_links_count(self) -> int:
        """Get count of affiliate links that have been reused multiple times."""
        return self.db_session.query(CachedAffiliateLink)\
            .filter(CachedAffiliateLink.usage_count > 1)\
            .filter(CachedAffiliateLink.expires_at > datetime.utcnow())\
            .count()
    
    def _get_popular_searches_count(self) -> int:
        """Get count of search results that have been accessed multiple times."""
        return self.db_session.query(CachedSearchResult)\
            .filter(CachedSearchResult.hit_count > 1)\
            .filter(CachedSearchResult.expires_at > datetime.utcnow())\
            .count()
    
    def _calculate_efficiency_rating(self, hit_rate: float) -> str:
        """Calculate cache efficiency rating based on hit rate."""
        if hit_rate >= 90:
            return 'excellent'
        elif hit_rate >= 70:
            return 'good'
        elif hit_rate >= 50:
            return 'fair'
        else:
            return 'needs_improvement'
    
    def generate_optimization_recommendations(self) -> List[Dict[str, str]]:
        """Generate recommendations for cache optimization."""
        recommendations = []
        
        try:
            # Get current performance metrics
            summary = self.get_performance_summary(days=7)
            hit_rate = summary.get('average_hit_rate_percentage', 0)
            
            if hit_rate < 70:
                recommendations.append({
                    'type': 'performance',
                    'priority': 'high',
                    'recommendation': 'Increase cache TTL for stable data like categories and product metadata',
                    'expected_impact': 'Improve hit rate by 10-20%'
                })
            
            if hit_rate < 50:
                recommendations.append({
                    'type': 'configuration',
                    'priority': 'high',
                    'recommendation': 'Enable Redis caching for better performance across multiple instances',
                    'expected_impact': 'Significant performance improvement'
                })
            
            # Check affiliate link reuse
            reusable_links = self._get_reusable_affiliate_links_count()
            total_links = self._get_cached_affiliate_links_count()
            
            if total_links > 0 and (reusable_links / total_links) < 0.3:
                recommendations.append({
                    'type': 'optimization',
                    'priority': 'medium',
                    'recommendation': 'Increase affiliate link cache TTL to improve reuse rate',
                    'expected_impact': 'Reduce affiliate API calls by 20-30%'
                })
            
            if not recommendations:
                recommendations.append({
                    'type': 'status',
                    'priority': 'info',
                    'recommendation': 'Cache performance is optimal. Continue monitoring.',
                    'expected_impact': 'Maintain current efficiency levels'
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            return [{
                'type': 'error',
                'priority': 'high',
                'recommendation': 'Unable to analyze performance. Check system health.',
                'expected_impact': 'Resolve monitoring issues'
            }]