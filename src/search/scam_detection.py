# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Scam Detection Engine for Atomic Search
Proxies requests to ScamAdvisor API for URL safety checks
"""

import re
import hashlib
import urllib.parse
from typing import Dict, Any, Optional
from searx.exceptions import SearxEngineAPIException

# ScamAdvisor API endpoint (free tier)
SCAMADVISOR_API_URL = "https://www.scamadviser.com/api/v2/check"

# Cache for results (in production, use Redis)
_scam_cache: Dict[str, Dict[str, Any]] = {}


def get_scamadvisor_score(url: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Check URL safety using ScamAdvisor API
    
    Args:
        url: The URL to check
        api_key: Optional ScamAdvisor API key for higher limits
    
    Returns:
        Dict with score (0-100), verdict, and details
    """
    # Normalize URL
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Create cache key
    cache_key = hashlib.md5(url.encode()).hexdigest()
    
    # Check cache first (5 min TTL)
    if cache_key in _scam_cache:
        cached = _scam_cache[cache_key]
        if cached.get('_cached_at', 0) > __import__('time').time() - 300:
            return cached
    
    try:
        # Build API URL
        params = {'url': url}
        if api_key:
            params['key'] = api_key
        
        api_url = f"{SCAMADVISOR_API_URL}?{urllib.parse.urlencode(params)}"
        
        # Make request (handled by searxng's request library)
        response = __import__('searx.network').get(api_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            result = {
                'score': data.get('score', -1),
                'verdict': _get_verdict(data.get('score', -1)),
                'suspicious': data.get('score', -1) >= 50,
                'unsafe': data.get('score', -1) >= 75,
                'domain': data.get('domain', ''),
                'domain_age': data.get('domainAge', {}),
                'connection_secure': data.get('connectionSecure', False),
                'is_malware': data.get('isMalware', False),
                'is_phishing': data.get('isPhishing', False),
                'is_parking': data.get('isParking', False),
                '_cached_at': __import__('time').time()
            }
            _scam_cache[cache_key] = result
            return result
        else:
            return _error_result(f"API returned status {response.status_code}")
    
    except Exception as e:
        return _error_result(str(e))


def _get_verdict(score: int) -> str:
    """Convert score to human-readable verdict"""
    if score < 0:
        return "Unknown"
    elif score < 20:
        return "Very Safe"
    elif score < 40:
        return "Safe"
    elif score < 60:
        return "Some Concerns"
    elif score < 80:
        return "Likely Risky"
    else:
        return "Scam/Potentially Dangerous"


def _error_result(error: str) -> Dict[str, Any]:
    """Return error result"""
    return {
        'score': -1,
        'verdict': 'Error',
        'error': error,
        'suspicious': False,
        'unsafe': False
    }


def add_scam_warnings_to_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add scam warning indicators to a search result
    
    Args:
        result: Search result dictionary
    
    Returns:
        Result with added scam_warning field if applicable
    """
    url = result.get('url', '')
    
    # Only check http/https URLs
    if not url.startswith(('http://', 'https://')):
        return result
    
    # Skip localhost/private IPs for privacy
    if _is_private_url(url):
        return result
    
    try:
        scam_info = get_scamadvisor_score(url)
        
        if scam_info.get('unsafe'):
            result['scam_warning'] = {
                'level': 'danger',
                'message': f"⚠️ This site may be unsafe (ScamAdvisor: {scam_info['verdict']})",
                'score': scam_info['score']
            }
        elif scam_info.get('suspicious'):
            result['scam_warning'] = {
                'level': 'warning',
                'message': f"⚡ Exercise caution ({scam_info['verdict']})",
                'score': scam_info['score']
            }
        elif scam_info.get('score', -1) >= 0:
            result['trust_score'] = {
                'level': 'safe',
                'score': scam_info['score'],
                'label': scam_info['verdict']
            }
        
    except Exception:
        pass  # Silently fail - don't block search results
    
    return result


def _is_private_url(url: str) -> bool:
    """Check if URL points to private/internal network"""
    private_patterns = [
        r'^localhost',
        r'^127\.',
        r'^10\.',
        r'^172\.(1[6-9]|2[0-9]|3[0-1])\.',
        r'^192\.168\.',
        r'\.local$',
        r'^0\.0\.0\.0',
        r'^::1',
    ]
    return any(re.match(p, url) for p in private_patterns)


# Atomic Search Engine
def request(query: Dict[str, Any], params: Dict[str, Any], url: str) -> Dict[str, Any]:
    """ScamAdvisor search engine request handler"""
    # This would be called as a search engine
    pass


def response(resp_search: Dict[str, Any], response: Any) -> List[Dict[str, Any]]:
    """Process ScamAdvisor API response"""
    pass
