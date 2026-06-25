# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Free API Key System for Atomic Search
Zero-config API access for everyone
"""

import hashlib
import secrets
import time
from typing import Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum


class APITier(Enum):
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    UNLIMITED = "unlimited"


@dataclass
class APIKey:
    key_id: str
    key_hash: str
    tier: str
    created_at: int
    last_used: int
    requests_today: int
    requests_total: int
    rate_limit: int
    daily_limit: int


class FreeAPIKeyManager:
    """
    Manages free API keys with tiered access
    """
    
    TIER_LIMITS = {
        APITier.FREE: {"daily": 100, "minute": 10},
        APITier.BASIC: {"daily": 1000, "minute": 50},
        APITier.PREMIUM: {"daily": 10000, "minute": 200},
        APITier.UNLIMITED: {"daily": -1, "minute": -1},
    }
    
    def __init__(self):
        self._keys: Dict[str, APIKey] = {}
        self._ip_usage: Dict[str, Dict[int, int]] = {}
        self._daily_reset: Dict[str, int] = {}
    
    def generate_key(self, tier: APITier = APITier.FREE) -> tuple:
        plain_key = f"atomic_{secrets.token_urlsafe(32)}"
        key_hash = self._hash_key(plain_key)
        key_id = key_hash[:12]
        limits = self.TIER_LIMITS[tier]
        
        api_key = APIKey(
            key_id=key_id,
            key_hash=key_hash,
            tier=tier.value,
            created_at=int(time.time()),
            last_used=0,
            requests_today=0,
            requests_total=0,
            rate_limit=limits["minute"],
            daily_limit=limits["daily"]
        )
        
        self._keys[key_hash] = api_key
        return plain_key, api_key
    
    def validate_key(self, plain_key: str, ip: str = "") -> tuple:
        if not plain_key or not plain_key.startswith("atomic_"):
            return False, None, "Invalid API key"
        
        key_hash = self._hash_key(plain_key)
        api_key = self._keys.get(key_hash)
        
        if not api_key:
            return False, None, "Invalid API key"
        
        tier = APITier(api_key.tier)
        limits = self.TIER_LIMITS[tier]
        
        # Check minute limit
        if ip and limits["minute"] > 0:
            current_minute = int(time.time() / 60)
            if ip in self._ip_usage:
                count = self._ip_usage[ip].get(current_minute, 0)
                if count >= limits["minute"]:
                    return False, api_key, f"Rate limit: {limits['minute']}/min"
        
        # Update
        api_key.last_used = int(time.time())
        api_key.requests_total += 1
        if ip:
            self._increment_ip_usage(ip)
        
        return True, api_key, "OK"
    
    def _hash_key(self, key: str) -> str:
        return hashlib.sha256(key.encode()).hexdigest()
    
    def _increment_ip_usage(self, ip: str) -> None:
        current_minute = int(time.time() / 60)
        if ip not in self._ip_usage:
            self._ip_usage[ip] = {}
        self._ip_usage[ip][current_minute] = self._ip_usage[ip].get(current_minute, 0) + 1
    
    def get_key_info(self, key_id: str) -> Optional[Dict]:
        for api_key in self._keys.values():
            if api_key.key_id == key_id:
                return {"id": api_key.key_id, "tier": api_key.tier, "requests_total": api_key.requests_total}
        return None


_api_manager = FreeAPIKeyManager()


def generate_free_api_key(tier: APITier = APITier.FREE) -> tuple:
    return _api_manager.generate_key(tier)


def validate_api_key(key: str, ip: str = "") -> tuple:
    return _api_manager.validate_key(key, ip)
