# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Anonymous Search Analytics for Atomic Search
Provides insights without tracking users
"""

import time
import hashlib
import json
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from collections import defaultdict
import threading


@dataclass
class SearchStats:
    """Aggregated search statistics"""
    total_searches: int = 0
    unique_queries: int = 0
    popular_queries: List[tuple] = None
    engines_used: Dict[str, int] = None
    avg_response_time: float = 0.0
    errors: int = 0
    uptime_seconds: int = 0
    
    def __post_init__(self):
        self.popular_queries = self.popular_queries or []
        self.engines_used = self.engines_used or {}


class AnonymousAnalytics:
    """
    Privacy-respecting search analytics
    
    - No individual queries are stored
    - Only hashed data is aggregated
    - No user identification
    - All data is ephemeral
    """
    
    def __init__(self):
        self._lock = threading.Lock()
        self._total_searches = 0
        self._query_counts: Dict[str, int] = defaultdict(int)  # Hash -> count
        self._engine_counts: Dict[str, int] = defaultdict(int)
        self._response_times: List[float] = []
        self._errors = 0
        self._start_time = time.time()
        self._unique_users: Set[str] = set()
        self._max_samples = 10000  # Keep rolling window
    
    def record_search(
        self,
        query: str,
        engines: List[str],
        response_time: float,
        result_count: int = 0,
        has_error: bool = False
    ) -> None:
        """
        Record a search (privacy-preserving)
        
        Args:
            query: Search query (will be hashed)
            engines: List of engines used
            response_time: Response time in seconds
            result_count: Number of results returned
            has_error: Whether search had an error
        """
        with self._lock:
            self._total_searches += 1
            
            # Hash query for aggregation (privacy!)
            query_hash = hashlib.sha256(query.lower().encode()).hexdigest()[:16]
            self._query_counts[query_hash] += 1
            
            # Track engines used
            for engine in engines:
                self._engine_counts[engine] += 1
            
            # Track response time (rolling average)
            self._response_times.append(response_time)
            if len(self._response_times) > self._max_samples:
                self._response_times.pop(0)
            
            # Track errors
            if has_error:
                self._errors += 1
    
    def record_click(self, result_url: str, query_hash: str = "") -> None:
        """
        Record a click on a result
        
        Args:
            result_url: URL of clicked result
            query_hash: Optional hash of original query
        """
        # We don't track individual clicks to preserve privacy
        # This is just a placeholder for potential future use
        pass
    
    def get_stats(self) -> SearchStats:
        """
        Get aggregated statistics
        
        Returns:
            SearchStats with anonymized data
        """
        with self._lock:
            # Calculate popular queries (by hashed name)
            sorted_queries = sorted(
                self._query_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:20]
            
            # Calculate average response time
            avg_time = sum(self._response_times) / max(len(self._response_times), 1)
            
            # Calculate uptime
            uptime = int(time.time() - self._start_time)
            
            return SearchStats(
                total_searches=self._total_searches,
                unique_queries=len(self._query_counts),
                popular_queries=[(h, c) for h, c in sorted_queries],
                engines_used=dict(self._engine_counts),
                avg_response_time=avg_time,
                errors=self._errors,
                uptime_seconds=uptime
            )
    
    def get_trending_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get trending queries (anonymized)
        
        Returns:
            List of trending query hashes with counts
        """
        with self._lock:
            # Get queries with significant activity
            trending = [
                {'hash': h[:8], 'count': c}
                for h, c in self._query_counts.items()
                if c >= 3  # Only show queries with multiple searches
            ]
            
            trending.sort(key=lambda x: x['count'], reverse=True)
            return trending[:limit]
    
    def get_engine_stats(self) -> Dict[str, Any]:
        """Get search engine usage statistics"""
        with self._lock:
            total = sum(self._engine_counts.values())
            if total == 0:
                return {}
            
            return {
                engine: {
                    'count': count,
                    'percentage': round(100 * count / total, 2)
                }
                for engine, count in self._engine_counts.items()
            }
    
    def reset_stats(self) -> None:
        """Reset all statistics"""
        with self._lock:
            self._total_searches = 0
            self._query_counts.clear()
            self._engine_counts.clear()
            self._response_times.clear()
            self._errors = 0
            self._start_time = time.time()
            self._unique_users.clear()
    
    def export_stats(self, format: str = 'json') -> str:
        """
        Export statistics in various formats
        
        Args:
            format: 'json', 'text', or 'csv'
        
        Returns:
            Formatted statistics string
        """
        stats = self.get_stats()
        
        if format == 'json':
            return json.dumps(asdict(stats), indent=2)
        
        elif format == 'text':
            lines = [
                "=== Atomic Search Analytics ===",
                f"Total Searches: {stats.total_searches}",
                f"Unique Queries: {stats.unique_queries}",
                f"Avg Response Time: {stats.avg_response_time:.3f}s",
                f"Errors: {stats.errors}",
                f"Uptime: {stats.uptime_seconds}s",
                "",
                "=== Engine Usage ===",
            ]
            for engine, count in sorted(stats.engines_used.items(), key=lambda x: x[1], reverse=True):
                lines.append(f"  {engine}: {count}")
            
            lines.extend([
                "",
                "=== Top Queries (Anonymized) ===",
            ])
            for h, c in stats.popular_queries[:10]:
                lines.append(f"  {h[:8]}...: {c}")
            
            return "\n".join(lines)
        
        elif format == 'csv':
            lines = ["engine,count,percentage"]
            for engine, data in self.get_engine_stats().items():
                lines.append(f"{engine},{data['count']},{data['percentage']}")
            return "\n".join(lines)
        
        return ""


# Global analytics instance
_analytics = AnonymousAnalytics()


def record_search(
    query: str,
    engines: List[str],
    response_time: float,
    result_count: int = 0,
    has_error: bool = False
) -> None:
    """Record a search"""
    _analytics.record_search(query, engines, response_time, result_count, has_error)


def get_stats() -> SearchStats:
    """Get analytics statistics"""
    return _analytics.get_stats()


def get_analytics() -> AnonymousAnalytics:
    """Get the analytics instance"""
    return _analytics
