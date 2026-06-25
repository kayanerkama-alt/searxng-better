# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Privacy Proxy Module for Atomic Search
Routes requests through multiple proxies to hide user identity
"""

import hashlib
import random
import time
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse

# Proxy rotation settings
PROXY_POOL: List[Dict[str, str]] = []
CURRENT_PROXY_INDEX = 0
_LAST_ROTATION = 0
PROXY_ROTATION_INTERVAL = 300  # 5 minutes


def init_proxies(proxy_list: Optional[str] = None) -> None:
    """
    Initialize proxy pool from environment variable or config
    
    Args:
        proxy_list: Comma-separated list of proxies (socks5://host:port, http://host:port)
    """
    global PROXY_POOL
    
    if not proxy_list:
        PROXY_POOL = []
        return
    
    for proxy in proxy_list.split(','):
        proxy = proxy.strip()
        if not proxy:
            continue
        
        parsed = urlparse(proxy)
        proxy_config = {
            'url': proxy,
            'scheme': parsed.scheme or 'http',
            'host': parsed.hostname or '',
            'port': parsed.port or (1080 if parsed.scheme == 'socks5' else 8080),
            'username': parsed.username,
            'password': parsed.password,
            'fail_count': 0,
            'last_used': 0,
            'success_count': 0,
        }
        PROXY_POOL.append(proxy_config)


def get_next_proxy() -> Optional[Dict[str, str]]:
    """
    Get next proxy from pool using rotation with load balancing
    
    Returns:
        Proxy config dict or None if pool is empty
    """
    global CURRENT_PROXY_INDEX, _LAST_ROTATION, PROXY_POOL
    
    if not PROXY_POOL:
        return None
    
    # Periodic rotation to distribute load
    current_time = time.time()
    if current_time - _LAST_ROTATION > PROXY_ROTATION_INTERVAL:
        CURRENT_PROXY_INDEX = (CURRENT_PROXY_INDEX + 1) % len(PROXY_POOL)
        _LAST_ROTATION = current_time
    
    # Get proxy with lowest fail count among available
    available = [p for p in PROXY_POOL if p['fail_count'] < 3]
    if not available:
        # Reset all if all are failing
        for p in PROXY_POOL:
            p['fail_count'] = 0
        available = PROXY_POOL
    
    # Sort by success rate
    available.sort(key=lambda x: x['success_count'] / max(x['fail_count'] + 1, 1), reverse=True)
    
    proxy = available[0]
    proxy['last_used'] = current_time
    return proxy


def report_proxy_success(proxy: Dict[str, str]) -> None:
    """Mark proxy as successful"""
    proxy['success_count'] += 1
    proxy['fail_count'] = max(0, proxy['fail_count'] - 1)


def report_proxy_failure(proxy: Dict[str, str]) -> None:
    """Mark proxy as failed"""
    proxy['fail_count'] += 1


def get_request_headers() -> Dict[str, str]:
    """
    Generate privacy-focused request headers
    
    Returns:
        Dict of headers that hide original request characteristics
    """
    # Rotate user agents among common browsers
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
    ]
    
    return {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }


def anonymize_ip(ip: str) -> str:
    """
    Partially mask IP address for logging privacy
    
    Args:
        ip: Original IP address
    
    Returns:
        Masked IP (e.g., "192.168.1.XXX")
    """
    parts = ip.split('.')
    if len(parts) == 4:
        # Keep first two octets, mask last two
        return f"{parts[0]}.{parts[1]}.xxx.xxx"
    return "xxx.xxx.xxx.xxx"


def generate_request_id() -> str:
    """Generate anonymous request ID"""
    timestamp = str(int(time.time() * 1000))
    random_part = hashlib.sha256(str(random.random()).encode()).hexdigest()[:8]
    return f"atomic-{timestamp}-{random_part}"


class ProxyPool:
    """Thread-safe proxy pool manager"""
    
    def __init__(self):
        self._lock = False
        self._proxies: List[Dict[str, Any]] = []
    
    def add_proxy(self, proxy_url: str) -> bool:
        """Add proxy to pool"""
        if not self._lock:
            self._lock = True
            try:
                parsed = urlparse(proxy_url)
                proxy = {
                    'url': proxy_url,
                    'scheme': parsed.scheme or 'http',
                    'host': parsed.hostname or '',
                    'port': parsed.port or 8080,
                    'username': parsed.username,
                    'password': parsed.password,
                    'fail_count': 0,
                    'success_count': 0,
                    'added_at': time.time(),
                }
                self._proxies.append(proxy)
                return True
            finally:
                self._lock = False
        return False
    
    def get_proxy(self) -> Optional[Dict[str, Any]]:
        """Get best available proxy"""
        if self._lock:
            return None
        
        self._lock = True
        try:
            available = [p for p in self._proxies if p['fail_count'] < 3]
            if not available:
                # Reset failures
                for p in self._proxies:
                    p['fail_count'] = 0
                available = self._proxies
            
            if not available:
                return None
            
            # Prefer proxies with best success rate
            available.sort(key=lambda x: x['success_count'] / max(x['fail_count'] + 1, 1), reverse=True)
            return available[0]
        finally:
            self._lock = False
    
    def report_success(self, proxy_url: str) -> None:
        """Report successful proxy usage"""
        for p in self._proxies:
            if p['url'] == proxy_url:
                p['success_count'] += 1
                p['fail_count'] = max(0, p['fail_count'] - 1)
                break
    
    def report_failure(self, proxy_url: str) -> None:
        """Report failed proxy usage"""
        for p in self._proxies:
            if p['url'] == proxy_url:
                p['fail_count'] += 1
                break
    
    def remove_proxy(self, proxy_url: str) -> bool:
        """Remove proxy from pool"""
        for i, p in enumerate(self._proxies):
            if p['url'] == proxy_url:
                self._proxies.pop(i)
                return True
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics"""
        return {
            'total': len(self._proxies),
            'available': len([p for p in self._proxies if p['fail_count'] < 3]),
            'failing': len([p for p in self._proxies if p['fail_count'] >= 3]),
            'total_success': sum(p['success_count'] for p in self._proxies),
            'total_failures': sum(p['fail_count'] for p in self._proxies),
        }


# Global proxy pool instance
_global_pool = ProxyPool()


def get_global_pool() -> ProxyPool:
    """Get the global proxy pool instance"""
    return _global_pool
