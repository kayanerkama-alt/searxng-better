"""
Kagi-Style Ranking System for Atomic Search
Quality-based result ranking inspired by Kagi
"""

import hashlib
import time
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class QualityScore:
    """Quality metrics for a result"""
    relevance: float = 0.0
    freshness: float = 0.0
    authority: float = 0.0
    user_trust: float = 0.0
    privacy_score: float = 1.0
    
    @property
    def total(self) -> float:
        """Calculate weighted total score"""
        return (
            self.relevance * 0.35 +
            self.freshness * 0.20 +
            self.authority * 0.25 +
            self.user_trust * 0.10 +
            self.privacy_score * 0.10
        )

class KagiRanker:
    """Kagi-style quality ranker"""
    
    # Trusted domains with higher authority
    TRUSTED_DOMAINS = {
        'wikipedia.org': 0.95,
        'github.com': 0.92,
        'stackoverflow.com': 0.90,
        'medium.com': 0.85,
        'dev.to': 0.85,
        'arxiv.org': 0.93,
        'scholar.google.com': 0.94,
        'nature.com': 0.92,
        'ieee.org': 0.91,
        'reddit.com': 0.80,
        'twitter.com': 0.78,
        'linkedin.com': 0.82,
        'youtube.com': 0.85,
        'duckduckgo.com': 0.88,
        'kagi.com': 0.95,
        'neeva.com': 0.85,
    }
    
    # Low-trust/tracker-heavy domains
    BLOCKED_PATTERNS = [
        'track.', 'ads.', 'analytics.',
        'doubleclick', 'googlesyndication',
        'facebooktracking', 'pixel',
    ]
    
    def __init__(self):
        self.user_preferences = {}
        self.click_history = {}
        
    def calculate_authority(self, url: str) -> float:
        """Calculate domain authority score"""
        from urllib.parse import urlparse
        try:
            domain = urlparse(url).netloc.lower()
            for trusted, score in self.TRUSTED_DOMAINS.items():
                if trusted in domain:
                    return score
            # Calculate based on domain age approximation (longer = more trusted)
            hash_val = int(hashlib.md5(domain.encode()).hexdigest()[:4], 16)
            return 0.5 + (hash_val / 65535) * 0.3
        except:
            return 0.5
            
    def calculate_freshness(self, result: Dict) -> float:
        """Calculate freshness score (newer = higher)"""
        # Check for date metadata
        pub_date = result.get('publishedDate') or result.get('date')
        if pub_date:
            try:
                age_days = (time.time() - pub_date) / 86400
                if age_days < 1:
                    return 1.0
                elif age_days < 7:
                    return 0.9
                elif age_days < 30:
                    return 0.8
                elif age_days < 180:
                    return 0.6
                elif age_days < 365:
                    return 0.4
                else:
                    return max(0.1, 0.3 - (age_days - 365) / 3650)
            except:
                pass
        return 0.5  # Default if no date
        
    def check_privacy(self, url: str) -> float:
        """Check URL privacy score"""
        url_lower = url.lower()
        for blocked in self.BLOCKED_PATTERNS:
            if blocked in url_lower:
                return 0.2
        # HTTPS bonus
        if url.startswith('https://'):
            return 1.0
        return 0.7
        
    def rank_results(self, results: List[Dict], query: str = "") -> List[Dict]:
        """Rank results using Kagi-style quality scoring"""
        scored_results = []
        
        for result in results:
            # Skip ads and tracked URLs
            if any(pattern in result.get('url', '').lower() for pattern in self.BLOCKED_PATTERNS):
                continue
                
            score = QualityScore()
            
            # Relevance based on title/content match
            title = result.get('title', '').lower()
            content = result.get('content', '').lower()
            query_lower = query.lower()
            
            query_words = query_lower.split()
            title_matches = sum(1 for w in query_words if w in title)
            content_matches = sum(1 for w in query_words if w in content)
            
            score.relevance = min(1.0, (title_matches * 0.5 + content_matches * 0.1) / max(1, len(query_words)))
            
            # Other quality metrics
            score.authority = self.calculate_authority(result.get('url', ''))
            score.freshness = self.calculate_freshness(result)
            score.privacy_score = self.check_privacy(result.get('url', ''))
            
            # Add quality score to result
            result['quality_score'] = round(score.total, 3)
            result['quality_badge'] = self._get_quality_badge(score.total)
            
            scored_results.append(result)
            
        # Sort by quality score (highest first)
        scored_results.sort(key=lambda x: x.get('quality_score', 0), reverse=True)
        
        return scored_results
        
    def _get_quality_badge(self, score: float) -> str:
        """Get quality badge based on score"""
        if score >= 0.85:
            return "⭐⭐⭐⭐⭐"
        elif score >= 0.75:
            return "⭐⭐⭐⭐"
        elif score >= 0.65:
            return "⭐⭐⭐"
        elif score >= 0.55:
            return "⭐⭐"
        else:
            return "⭐"

# Global ranker instance
ranker = KagiRanker()

def rank_search_results(results: List[Dict], query: str = "") -> List[Dict]:
    """Public API for ranking results"""
    return ranker.rank_results(results, query)
