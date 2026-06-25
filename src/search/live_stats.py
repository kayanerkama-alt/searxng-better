# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Live Statistics & Search Counter for Atomic Search
Tracks global searches with a dramatic counter
"""

import time
import threading
import random
from typing import Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import json


@dataclass
class SearchStats:
    """Statistics for a single search"""
    query: str
    timestamp: int
    engine: str
    result_count: int
    response_time_ms: float
    cached: bool = False
    private_mode: bool = True


@dataclass
class GlobalStats:
    """Global statistics across all searches"""
    total_searches: int = 125_000_000_000  # Start at 125 billion
    searches_today: int = 0
    searches_this_hour: int = 0
    searches_this_minute: int = 0
    avg_response_time_ms: float = 0.0
    cache_hit_rate: float = 0.0
    top_queries: list = field(default_factory=list)
    searches_by_engine: Dict[str, int] = field(default_factory=dict)
    searches_by_country: Dict[str, int] = field(default_factory=dict)
    privacy_enabled_searches: int = 0
    trackers_blocked: int = 0
    anonymous_proxies_used: int = 0
    last_updated: int = 0


class LiveStatsManager:
    """
    Manages live statistics and the global search counter
    """
    
    # Base number - starts at 100 billion
    BASE_COUNTER = 100_000_000_000
    
    # Searches added per real search (simulated global count)
    SIMULATED_INCREMENT = 15  # Real Google does ~3.5B/day, we scale up
    
    def __init__(self):
        self._lock = threading.RLock()
        self._total_searches = self.BASE_COUNTER
        self._today_searches = 0
        self._hour_searches = 0
        self._minute_searches = 0
        self._day_start = self._get_day_start()
        self._hour_start = self._get_hour_start()
        self._minute_start = self._get_minute_start()
        
        # Tracking
        self._search_history: list = []
        self._max_history = 1000
        self._top_queries: Dict[str, int] = defaultdict(int)
        self._by_engine: Dict[str, int] = defaultdict(int)
        self._by_country: Dict[str, int] = defaultdict(int)
        
        # Response time tracking
        self._response_times: list = []
        self._max_response_times = 100
        
        # Privacy stats
        self._privacy_enabled = 0
        self._trackers_blocked = 0
        self._proxy_used = 0
        
        # Nodes (distributed computing)
        self._nodes: Dict[str, Dict] = {}
        self._node_stats: Dict[str, int] = defaultdict(int)
        
        # Start background simulation
        self._running = True
        self._sim_thread = threading.Thread(target=self._simulate_traffic, daemon=True)
        self._sim_thread.start()
        
        # Start cleanup thread
        self._cleanup_thread = threading.Thread(target=self._periodic_cleanup, daemon=True)
        self._cleanup_thread.start()
    
    def _get_day_start(self) -> int:
        return int(time.time()) // 86400 * 86400
    
    def _get_hour_start(self) -> int:
        return int(time.time()) // 3600 * 3600
    
    def _get_minute_start(self) -> int:
        return int(time.time()) // 60 * 60
    
    def _simulate_traffic(self):
        """Background thread to simulate global traffic"""
        while self._running:
            try:
                # Add simulated searches periodically
                # Real search engines get 3-5 searches per second globally
                time.sleep(0.2)  # Every 200ms
                
                with self._lock:
                    # Simulate varying traffic
                    hour = datetime.now().hour
                    
                    # Peak hours (9am-9pm) have 3x traffic
                    if 9 <= hour <= 21:
                        increment = random.randint(20, 50)
                    else:
                        increment = random.randint(5, 15)
                    
                    self._total_searches += increment
                    self._today_searches += increment
                    self._hour_searches += increment
                    self._minute_searches += increment
                    
            except Exception:
                pass
    
    def _periodic_cleanup(self):
        """Reset counters periodically"""
        while self._running:
            time.sleep(60)  # Every minute
            self._reset_minute()
            
            if int(time.time()) // 3600 != self._hour_start // 3600:
                self._reset_hour()
            
            if int(time.time()) // 86400 != self._day_start // 86400:
                self._reset_day()
    
    def _reset_minute(self):
        with self._lock:
            self._minute_searches = 0
            self._minute_start = self._get_minute_start()
    
    def _reset_hour(self):
        with self._lock:
            self._hour_searches = 0
            self._hour_start = self._get_hour_start()
    
    def _reset_day(self):
        with self._lock:
            self._today_searches = 0
            self._day_start = self._get_day_start()
    
    def record_search(
        self,
        query: str,
        engine: str = "atomic",
        result_count: int = 0,
        response_time_ms: float = 0.0,
        cached: bool = False,
        country: Optional[str] = None
    ) -> int:
        """
        Record a search and return the new total
        
        Returns:
            The new total search count
        """
        with self._lock:
            # Add real search
            self._total_searches += 1
            self._today_searches += 1
            self._hour_searches += 1
            self._minute_searches += 1
            
            # Track stats
            self._by_engine[engine] += 1
            if country:
                self._by_country[country] += 1
            
            # Top queries
            query_key = query.lower()[:50]  # Normalize and limit
            self._top_queries[query_key] += 1
            
            # Response times
            self._response_times.append(response_time_ms)
            if len(self._response_times) > self._max_response_times:
                self._response_times.pop(0)
            
            # Privacy stats
            self._privacy_enabled += 1
            
            # Store in history
            stats = SearchStats(
                query=query[:100],  # Limit stored query length
                timestamp=int(time.time()),
                engine=engine,
                result_count=result_count,
                response_time_ms=response_time_ms,
                cached=cached
            )
            self._search_history.append(stats)
            if len(self._search_history) > self._max_history:
                self._search_history.pop(0)
            
            return self._total_searches
    
    def record_tracker_blocked(self):
        """Record a blocked tracker"""
        with self._lock:
            self._trackers_blocked += 1
    
    def record_proxy_used(self):
        """Record anonymous proxy usage"""
        with self._lock:
            self._proxy_used += 1
    
    def get_live_counter(self) -> Dict[str, Any]:
        """Get the live counter value"""
        with self._lock:
            return {
                "total": self._total_searches,
                "formatted": self._format_number(self._total_searches),
                "per_second": self._calculate_qps(),
                "today": self._today_searches,
                "this_hour": self._hour_searches,
                "this_minute": self._minute_searches
            }
    
    def _calculate_qps(self) -> float:
        """Calculate queries per second"""
        current_minute_start = self._get_minute_start()
        if current_minute_start > self._minute_start:
            return 0
        elapsed = time.time() - self._minute_start
        if elapsed > 0:
            return self._minute_searches / elapsed
        return 0
    
    def _format_number(self, num: int) -> str:
        """Format large numbers nicely"""
        if num >= 1_000_000_000_000:
            return f"{num / 1_000_000_000_000:.2f}T"
        elif num >= 1_000_000_000:
            return f"{num / 1_000_000_000:.2f}B"
        elif num >= 1_000_000:
            return f"{num / 1_000_000:.2f}M"
        elif num >= 1_000:
            return f"{num / 1_000:.2f}K"
        return str(num)
    
    def get_full_stats(self) -> Dict[str, Any]:
        """Get all statistics"""
        with self._lock:
            avg_response = sum(self._response_times) / len(self._response_times) if self._response_times else 0
            cache_hits = sum(1 for s in self._search_history if s.cached)
            cache_rate = cache_hits / len(self._search_history) if self._search_history else 0
            
            return {
                "counter": {
                    "total": self._total_searches,
                    "formatted": self._format_number(self._total_searches),
                    "per_second": round(self._calculate_qps(), 1),
                    "today": self._today_searches,
                    "this_hour": self._hour_searches
                },
                "performance": {
                    "avg_response_ms": round(avg_response, 2),
                    "cache_hit_rate": round(cache_rate * 100, 1)
                },
                "top_queries": sorted(
                    self._top_queries.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10],
                "by_engine": dict(sorted(
                    self._by_engine.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:10]),
                "privacy": {
                    "privacy_enabled": self._privacy_enabled,
                    "trackers_blocked": self._trackers_blocked,
                    "proxies_used": self._proxy_used
                },
                "nodes": {
                    "active": len(self._nodes),
                    "total_contributions": sum(self._node_stats.values())
                },
                "updated_at": int(time.time())
            }
    
    # === NODE SYSTEM ===
    
    def register_node(self, node_id: str, info: Dict) -> Dict:
        """Register a new node"""
        with self._lock:
            self._nodes[node_id] = {
                "id": node_id,
                "registered_at": int(time.time()),
                "last_ping": int(time.time()),
                "ip": info.get("ip", "unknown"),
                "location": info.get("location", "unknown"),
                "status": "active"
            }
            return {"success": True, "node_id": node_id, "token": self._generate_node_token(node_id)}
    
    def _generate_node_token(self, node_id: str) -> str:
        """Generate a secure token for a node"""
        import hashlib
        import secrets
        return hashlib.sha256(f"{node_id}{secrets.token_hex(16)}{time.time()}".encode()).hexdigest()
    
    def node_ping(self, node_id: str) -> bool:
        """Node heartbeat"""
        with self._lock:
            if node_id in self._nodes:
                self._nodes[node_id]["last_ping"] = int(time.time())
                return True
            return False
    
    def node_contribute(self, node_id: str, searches: int) -> Dict:
        """Record node contribution"""
        with self._lock:
            if node_id in self._nodes:
                self._node_stats[node_id] += searches
                self._total_searches += searches  # Add to global count
                return {"success": True, "new_total": self._total_searches}
            return {"success": False, "error": "Node not registered"}
    
    def get_nodes(self) -> list:
        """Get list of active nodes"""
        with self._lock:
            now = int(time.time())
            return [
                {**node, "online": now - node["last_ping"] < 300}
                for node in self._nodes.values()
            ]
    
    def shutdown(self):
        """Shutdown the stats manager"""
        self._running = False


# Global instance
_stats_manager = LiveStatsManager()


def get_live_stats() -> LiveStatsManager:
    """Get the live stats manager"""
    return _stats_manager


def get_counter() -> Dict[str, Any]:
    """Get the live counter"""
    return _stats_manager.get_live_counter()


def get_full_stats() -> Dict[str, Any]:
    """Get all statistics"""
    return _stats_manager.get_full_stats()


def record_search(query: str, **kwargs) -> int:
    """Record a search"""
    return _stats_manager.record_search(query, **kwargs)
