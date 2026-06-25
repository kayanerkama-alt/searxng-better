# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Search Result Enhancer for Atomic Search
Enhances search results with additional metadata and safety checks
"""

import re
import hashlib
import time
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass
from urllib.parse import urlparse, unquote


@dataclass
class EnhancedResult:
    """Enhanced search result with additional metadata"""
    original: Dict[str, Any]
    parsed_domain: str
    is_secure: bool
    is_trusted: bool
    trust_score: float
    safety_level: str  # 'safe', 'warning', 'danger'
    content_type: str  # 'article', 'video', 'image', 'social', 'ecommerce', 'unknown'
    load_time_estimate: str  # 'fast', 'medium', 'slow'
    is_mobile_friendly: bool
    parsed_url: str


class ResultEnhancer:
    """
    Enhances search results with metadata and safety information
    """
    
    # Trusted domains that typically have quality content
    TRUSTED_DOMAINS = {
        'wikipedia.org': 0.95,
        'github.com': 0.9,
        'stackoverflow.com': 0.95,
        'medium.com': 0.75,
        'dev.to': 0.8,
        'reddit.com': 0.6,
        'twitter.com': 0.5,
        'youtube.com': 0.7,
        'vimeo.com': 0.7,
        'arxiv.org': 0.95,
        'scholar.google.com': 0.9,
        'duckduckgo.com': 0.8,
        'wolframalpha.com': 0.9,
        'khanacademy.org': 0.9,
    }
    
    # Suspicious patterns
    SUSPICIOUS_PATTERNS = [
        r'\.tk$', r'\.ml$', r'\.ga$', r'\.cf$', r'\.gq$',  # Free domains
        r'click\.", r'track\.", r'redirect\.",
        r'free-.*\.com', r'get-.*\.com',
    ]
    
    # Content type indicators
    CONTENT_PATTERNS = {
        'video': [r'youtube\.com', r'vimeo\.com', r'dailymotion\.com', r'tiktok\.com', r'twitch\.tv'],
        'social': [r'facebook\.com', r'twitter\.com', r'instagram\.com', r'linkedin\.com', r'tumblr\.com'],
        'ecommerce': [r'amazon\..*', r'ebay\..*', r'aliexpress\.com', r'walmart\.com', r'etsy\.com'],
        'news': [r'bbc\..*', r'cnn\..*', r'foxnews\.com', r'nytimes\.com', r'washingtonpost\.com'],
        'academic': [r'arxiv\.org', r'scholar\.google', r'pubmed\.ncbi\.nlm\.nih\.gov', r'researchgate\.net'],
    }
    
    def __init__(self):
        self._cache: Dict[str, EnhancedResult] = {}
        self._cache_ttl = 3600  # 1 hour
    
    def enhance_result(self, result: Dict[str, Any]) -> EnhancedResult:
        """
        Enhance a single search result with metadata
        
        Args:
            result: Original search result dict
        
        Returns:
            Enhanced result with additional metadata
        """
        url = result.get('url', '')
        
        # Check cache
        cache_key = hashlib.md5(url.encode()).hexdigest()
        if cache_key in self._cache:
            cached = self._cache[cache_key]
            age = time.time() - getattr(cached, '_cached_at', 0)
            if age < self._cache_ttl:
                cached.original = result
                return cached
        
        # Parse URL
        parsed = urlparse(url)
        domain = self._parse_domain(parsed.netloc)
        
        # Analyze result
        enhanced = EnhancedResult(
            original=result,
            parsed_domain=domain,
            is_secure=parsed.scheme == 'https',
            is_trusted=domain in self.TRUSTED_DOMAINS,
            trust_score=self.TRUSTED_DOMAINS.get(domain, 0.5),
            safety_level=self._check_safety(url, domain),
            content_type=self._detect_content_type(url, result),
            load_time_estimate='fast',  # Would need actual measurement
            is_mobile_friendly=True,  # Would need actual check
            parsed_url=url
        )
        
        enhanced._cached_at = time.time()
        self._cache[cache_key] = enhanced
        return enhanced
    
    def enhance_results(self, results: List[Dict[str, Any]]) -> List[EnhancedResult]:
        """Enhance multiple results"""
        return [self.enhance_result(r) for r in results]
    
    def _parse_domain(self, netloc: str) -> str:
        """Parse domain from netloc"""
        # Remove port
        domain = netloc.split(':')[0]
        # Remove www
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain.lower()
    
    def _check_safety(self, url: str, domain: str) -> str:
        """Check URL safety"""
        url_lower = url.lower()
        domain_lower = domain.lower()
        
        # Check for suspicious patterns
        for pattern in self.SUSPICIOUS_PATTERNS:
            if re.search(pattern, url_lower) or re.search(pattern, domain_lower):
                return 'warning'
        
        # Check for HTTPS
        if not url.startswith('https://'):
            return 'warning'
        
        # Check known bad domains (would be populated from threat feeds)
        # For now, default to safe
        return 'safe'
    
    def _detect_content_type(self, url: str, result: Dict[str, Any]) -> str:
        """Detect content type from URL and result"""
        url_lower = url.lower()
        
        # Check patterns
        for content_type, patterns in self.CONTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, url_lower):
                    return content_type
        
        # Check result type hints
        if result.get('img_src'):
            return 'image'
        if result.get('iframe'):
            return 'video'
        
        return 'article'  # Default
    
    def get_trusted_domains(self, results: List[Dict[str, Any]]) -> List[Tuple[str, float]]:
        """Get list of trusted domains in results"""
        trusted = []
        seen: Set[str] = set()
        
        for result in results:
            url = result.get('url', '')
            parsed = urlparse(url)
            domain = self._parse_domain(parsed.netloc)
            
            if domain not in seen and domain in self.TRUSTED_DOMAINS:
                trusted.append((domain, self.TRUSTED_DOMAINS[domain]))
                seen.add(domain)
        
        return trusted
    
    def filter_safe_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter out potentially unsafe results"""
        safe = []
        for result in results:
            enhanced = self.enhance_result(result)
            if enhanced.safety_level != 'danger':
                safe.append(result)
        return safe
    
    def sort_by_trust(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort results by trust score"""
        enhanced = self.enhance_results(results)
        enhanced.sort(key=lambda x: x.trust_score, reverse=True)
        return [e.original for e in enhanced]
    
    def clear_cache(self):
        """Clear enhancement cache"""
        self._cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get enhancer statistics"""
        safe_count = sum(1 for r in self._cache.values() if r.safety_level == 'safe')
        warning_count = sum(1 for r in self._cache.values() if r.safety_level == 'warning')
        return {
            'cached': len(self._cache),
            'safe': safe_count,
            'warnings': warning_count,
        }


# Global instance
_result_enhancer = ResultEnhancer()


def enhance_result(result: Dict[str, Any]) -> EnhancedResult:
    """Enhance a single result"""
    return _result_enhancer.enhance_result(result)


def enhance_results(results: List[Dict[str, Any]]) -> List[EnhancedResult]:
    """Enhance multiple results"""
    return _result_enhancer.enhance_results(results)


def get_result_enhancer() -> ResultEnhancer:
    """Get the result enhancer instance"""
    return _result_enhancer
