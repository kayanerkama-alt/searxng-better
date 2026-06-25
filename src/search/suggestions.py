# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Smart Suggestions Module for Atomic Search
Provides context-aware search suggestions
"""

import re
import time
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class SearchSuggestion:
    """A search suggestion with metadata"""
    text: str
    source: str  # 'history', 'trending', 'related', 'correction'
    confidence: float = 0.5
    category: Optional[str] = None  # 'news', 'shopping', 'video', etc.


class SuggestionEngine:
    """
    Context-aware search suggestions engine
    Provides suggestions based on:
    - Search history (local)
    - Trending topics
    - Related searches
    - Typo corrections
    - Language detection
    """
    
    # Common typo corrections
    TYPO_CORRECTIONS = {
        'teh': 'the',
        'recieve': 'receive',
        'definately': 'definitely',
        'occured': 'occurred',
        'seperate': 'separate',
        'tommorow': 'tomorrow',
        'wether': 'weather',
        'wierd': 'weird',
        'accomodate': 'accommodate',
        'occurence': 'occurrence',
    }
    
    # Category keywords
    CATEGORY_KEYWORDS = {
        'shopping': ['buy', 'price', 'shop', 'store', 'amazon', 'ebay', 'sale', 'discount'],
        'news': ['news', 'breaking', 'latest', 'today', 'headline'],
        'video': ['youtube', 'video', 'watch', 'tiktok', 'stream'],
        'images': ['image', 'photo', 'picture', 'gallery', 'img'],
        'weather': ['weather', 'temperature', 'forecast', 'rain'],
        'map': ['map', 'location', 'directions', 'nearby', 'address'],
        'recipe': ['recipe', 'cook', 'food', 'restaurant', 'ingredients'],
        'newsletter': ['subscribe', 'newsletter', 'email', 'mailing'],
    }
    
    def __init__(self):
        self._history: List[Tuple[str, int]] = []  # (query, timestamp)
        self._max_history = 100
        self._cache: Dict[str, List[SearchSuggestion]] = {}
        self._cache_ttl = 300  # 5 minutes
    
    def add_to_history(self, query: str) -> None:
        """Add query to local history"""
        query = query.strip().lower()
        if query:
            # Remove duplicates and add to front
            self._history = [(q, t) for q, t in self._history if q != query]
            self._history.insert(0, (query, int(time.time())))
            # Trim history
            self._history = self._history[:self._max_history]
            # Clear relevant cache
            self._clear_cache_for_query(query)
    
    def get_suggestions(self, query: str, limit: int = 10) -> List[SearchSuggestion]:
        """
        Get suggestions for a query
        
        Args:
            query: The partial query
            limit: Maximum number of suggestions
        
        Returns:
            List of SearchSuggestion objects
        """
        query = query.strip().lower()
        if not query or len(query) < 2:
            return []
        
        # Check cache
        cache_key = self._get_cache_key(query)
        if cache_key in self._cache:
            cached = self._cache[cache_key]
            if time.time() - cached[0].get('_cached_at', 0) < self._cache_ttl:
                return cached[:limit]
        
        suggestions = []
        seen = set()
        
        # 1. Typo corrections (highest priority)
        correction = self._check_typo(query)
        if correction and correction not in seen:
            suggestions.append(SearchSuggestion(
                text=correction,
                source='correction',
                confidence=0.9,
                category=self._detect_category(correction)
            ))
            seen.add(correction)
        
        # 2. Search history matches
        for hist_query, _ in self._history[:20]:
            if hist_query.startswith(query) and hist_query != query and hist_query not in seen:
                suggestions.append(SearchSuggestion(
                    text=hist_query,
                    source='history',
                    confidence=0.8
                ))
                seen.add(hist_query)
        
        # 3. Word completions
        completions = self._get_word_completions(query)
        for comp in completions:
            if comp not in seen:
                suggestions.append(SearchSuggestion(
                    text=comp,
                    source='completion',
                    confidence=0.6,
                    category=self._detect_category(comp)
                ))
                seen.add(comp)
        
        # 4. Related searches (would integrate with search engine API)
        related = self._get_related_searches(query)
        for rel in related:
            if rel not in seen:
                suggestions.append(SearchSuggestion(
                    text=rel,
                    source='related',
                    confidence=0.5,
                    category=self._detect_category(rel)
                ))
                seen.add(rel)
        
        # Cache results
        if suggestions:
            suggestions[0]._cached_at = time.time()
            self._cache[cache_key] = suggestions
        
        return suggestions[:limit]
    
    def _check_typo(self, query: str) -> Optional[str]:
        """Check for common typos"""
        words = query.split()
        if len(words) > 0:
            first_word = words[0].lower()
            if first_word in self.TYPO_CORRECTIONS:
                correction = self.TYPO_CORRECTIONS[first_word]
                if len(words) > 1:
                    return f"{correction} {' '.join(words[1:])}"
                return correction
        return None
    
    def _get_word_completions(self, query: str) -> List[str]:
        """Get common word completions"""
        completions = []
        
        # Common query prefixes
        prefixes = [
            'how to', 'how to ' + query,
            'what is', 'what is ' + query,
            'why does', 'why is ' + query,
            'best', 'best ' + query,
            'top', 'top ' + query,
            'free', 'free ' + query,
            'cheap', 'cheap ' + query,
            'near me', query + ' near me',
            'online', query + ' online',
        ]
        
        for prefix in prefixes:
            if prefix.startswith(query) and prefix != query and len(prefix) > len(query) + 2:
                completions.append(prefix)
        
        return completions[:3]
    
    def _get_related_searches(self, query: str) -> List[str]:
        """Get related searches (placeholder - would integrate with search API)"""
        # This would normally query the search engine for related terms
        # For now, return common patterns
        related = []
        
        # Add query variations
        if 'how to' not in query:
            related.append(f"how to {query}")
        if 'what is' not in query:
            related.append(f"what is {query}")
        
        return related[:2]
    
    def _detect_category(self, query: str) -> Optional[str]:
        """Detect search category from query"""
        query_lower = query.lower()
        
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in query_lower:
                    return category
        
        return None
    
    def _get_cache_key(self, query: str) -> str:
        """Get cache key for query"""
        return hashlib.md5(query.encode()).hexdigest()
    
    def _clear_cache_for_query(self, query: str) -> None:
        """Clear cache entries that might be affected by new query"""
        # Simple implementation - clear all cache if history changes significantly
        if len(self._history) % 10 == 0:
            self._cache.clear()
    
    def get_history(self, limit: int = 20) -> List[str]:
        """Get recent search history"""
        return [q for q, _ in self._history[:limit]]
    
    def clear_history(self) -> None:
        """Clear search history"""
        self._history.clear()
        self._cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get engine statistics"""
        return {
            'history_size': len(self._history),
            'cache_size': len(self._cache),
            'categories': list(self.CATEGORY_KEYWORDS.keys()),
        }


# Global instance
_suggestion_engine = SuggestionEngine()


def get_suggestions(query: str, limit: int = 10) -> List[SearchSuggestion]:
    """Get suggestions for query"""
    return _suggestion_engine.get_suggestions(query, limit)


def add_to_history(query: str) -> None:
    """Add query to history"""
    _suggestion_engine.add_to_history(query)


def get_suggestion_engine() -> SuggestionEngine:
    """Get the suggestion engine"""
    return _suggestion_engine
