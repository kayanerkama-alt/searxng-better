# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Privacy-First Search History Manager
Stores minimal data, auto-deletes, and respects user privacy
"""

import time
import hashlib
import json
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import OrderedDict
import threading


class RetentionPolicy(Enum):
    """Data retention policies"""
    NONE = 0          # No storage at all
    SESSION = 1       # Only current session
    SHORT = 24 * 3600  # 24 hours
    MEDIUM = 7 * 24 * 3600  # 7 days
    LONG = 30 * 24 * 3600  # 30 days


@dataclass
class SearchEntry:
    """A single search entry (anonymized)"""
    query_hash: str       # SHA256 hash of query (no plain text)
    timestamp: int        # Unix timestamp
    result_count: int     # Number of results shown
    category: str         # Search category used
    duration_ms: int      # Search duration
    session_id: str       # Anonymized session ID
    
    def to_dict(self) -> Dict:
        return {
            'q': self.query_hash[:16] + '...',  # Truncated hash
            't': self.timestamp,
            'n': self.result_count,
            'c': self.category,
            'd': self.duration_ms
        }


@dataclass  
class PrivacySettings:
    """User privacy settings for history"""
    retention: RetentionPolicy = RetentionPolicy.SHORT
    store_queries: bool = True
    store_clicks: bool = False
    store_timestamps: bool = False
    anonymize: bool = True
    local_only: bool = True  # Don't send to server


class PrivateSearchHistory:
    """
    Privacy-first search history manager
    
    Features:
    - Minimal data collection
    - Automatic expiration
    - Full anonymization
    - Optional local-only storage
    - Session isolation
    """
    
    MAX_ENTRIES = 1000  # Maximum entries to keep
    
    def __init__(self, settings: Optional[PrivacySettings] = None):
        self._settings = settings or PrivacySettings()
        self._history: OrderedDict[str, SearchEntry] = OrderedDict()
        self._sessions: Set[str] = set()
        self._lock = threading.RLock()
        self._session_id = self._generate_session_id()
        
        # Start cleanup thread
        self._cleanup_thread = threading.Thread(target=self._auto_cleanup, daemon=True)
        self._cleanup_thread.start()
    
    def _generate_session_id(self) -> str:
        """Generate anonymous session ID"""
        import secrets
        # Use random bytes, no user-identifiable info
        return hashlib.sha256(secrets.token_bytes(32)).hexdigest()[:24]
    
    def _hash_query(self, query: str) -> str:
        """Hash query for storage"""
        if not self._settings.anonymize:
            return query
        # Salt with session to prevent cross-session correlation
        salt = self._session_id.encode() if self._session_id else b''
        return hashlib.sha256((query + str(salt)).encode()).hexdigest()
    
    def add_search(
        self,
        query: str,
        result_count: int = 0,
        category: str = "general",
        duration_ms: int = 0
    ) -> None:
        """Add a search to history (anonymized)"""
        if not self._settings.store_queries:
            return
        
        with self._lock:
            entry = SearchEntry(
                query_hash=self._hash_query(query),
                timestamp=int(time.time()) if self._settings.store_timestamps else 0,
                result_count=result_count,
                category=category,
                duration_ms=duration_ms,
                session_id=self._session_id[:12] if not self._settings.anonymize else ''
            )
            
            # Use hash as key for deduplication
            self._history[entry.query_hash] = entry
            
            # Enforce max entries
            while len(self._history) > self.MAX_ENTRIES:
                self._history.popitem(last=False)
    
    def get_recent(self, limit: int = 10) -> List[SearchEntry]:
        """Get recent searches (anonymized)"""
        with self._lock:
            entries = list(self._history.values())[-limit:]
            return entries if self._settings.anonymize else entries
    
    def search_history(self, partial_hash: str, limit: int = 5) -> List[Dict]:
        """
        Search history by partial query hash
        Used for autocomplete - only matches hashed prefixes
        """
        if not self._settings.store_queries:
            return []
        
        with self._lock:
            matches = []
            for entry in reversed(list(self._history.values())):
                if entry.query_hash.startswith(partial_hash.lower()):
                    matches.append(entry.to_dict())
                    if len(matches) >= limit:
                        break
            return matches
    
    def clear_history(self) -> None:
        """Clear all search history"""
        with self._lock:
            self._history.clear()
    
    def delete_entry(self, query_hash: str) -> bool:
        """Delete a specific entry"""
        with self._lock:
            if query_hash in self._history:
                del self._history[query_hash]
                return True
            return False
    
    def _should_expire(self, entry: SearchEntry) -> bool:
        """Check if entry should be expired"""
        if self._settings.retention == RetentionPolicy.NONE:
            return True
        
        if self._settings.retention == RetentionPolicy.SESSION:
            return entry.session_id != self._session_id[:12]
        
        if entry.timestamp > 0:
            age = time.time() - entry.timestamp
            return age > self._settings.retention.value
        
        return False
    
    def _auto_cleanup(self) -> None:
        """Background thread to clean up expired entries"""
        while True:
            time.sleep(3600)  # Run every hour
            self.cleanup_expired()
    
    def cleanup_expired(self) -> int:
        """Remove expired entries"""
        with self._lock:
            before = len(self._history)
            self._history = OrderedDict(
                (k, v) for k, v in self._history.items()
                if not self._should_expire(v)
            )
            return before - len(self._history)
    
    def get_stats(self) -> Dict:
        """Get history statistics (anonymized)"""
        with self._lock:
            total = len(self._history)
            by_category = {}
            for entry in self._history.values():
                by_category[entry.category] = by_category.get(entry.category, 0) + 1
            
            return {
                'total_searches': total,
                'retention_policy': self._settings.retention.name,
                'by_category': by_category,
                'session_active': True,
                'auto_delete': self._settings.retention != RetentionPolicy.NONE
            }
    
    def set_retention(self, policy: RetentionPolicy) -> None:
        """Change retention policy"""
        self._settings.retention = policy
        # Trigger cleanup with new policy
        self.cleanup_expired()
    
    def export_anonymized(self) -> Dict:
        """Export data in anonymized format"""
        with self._lock:
            return {
                'version': '1.0',
                'exported_at': int(time.time()),
                'settings': asdict(self._settings),
                'history': [e.to_dict() for e in self._history.values()],
                'stats': self.get_stats()
            }
    
    def new_session(self) -> str:
        """Start a new anonymous session"""
        with self._lock:
            self._session_id = self._generate_session_id()
            self._sessions.add(self._session_id)
            return self._session_id


# Global instance
_search_history = PrivateSearchHistory()


def get_search_history() -> PrivateSearchHistory:
    """Get the search history instance"""
    return _search_history


def add_to_history(query: str, **kwargs) -> None:
    """Quick function to add search to history"""
    _search_history.add_search(query, **kwargs)


def clear_all_history() -> None:
    """Clear all search history"""
    _search_history.clear_history()


def get_recent_searches(limit: int = 10) -> List[Dict]:
    """Get recent searches"""
    return [e.to_dict() for e in _search_history.get_recent(limit)]
