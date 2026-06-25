# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Instant Answers Module for Atomic Search
Provides direct answers to common queries
"""

import re
import json
import time
import hashlib
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass


@dataclass
class InstantAnswer:
    """An instant answer to a query"""
    answer_type: str  # 'calculator', 'definition', 'weather', 'conversion', etc.
    answer: str       # The answer text/markdown
    sources: List[str]  # Source URLs
    confidence: float  # 0.0 to 1.0
    extra: Dict[str, Any] = None  # Additional data
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'type': self.answer_type,
            'answer': self.answer,
            'sources': self.sources,
            'confidence': self.confidence,
            'extra': self.extra or {}
        }


class InstantAnswerEngine:
    """
    Engine for providing instant answers to queries
    Handles: calculators, definitions, weather, conversions, etc.
    """
    
    # Known triggers for instant answers
    CALCULATOR_TRIGGERS = [
        r'^calc[:\s]*(.+)', r'^=\s*(.+)', r'^(\d+[\+\-\*\/\^]\d+)$'
    ]
    
    DEFINITION_TRIGGERS = [
        r'^def(ine)?[:\s]+(.+)', r'^what is (a |an )?(.+)',
        r"^meaning of (.+)", r"^(.+) means"
    ]
    
    WEATHER_TRIGGERS = [
        r'^weather (?:in |at |for )?(.+)', r"^how's? (?:the )?weather",
        r'^temp(?:erature)? (?:in |at )?(.+)', r'^weather$'
    ]
    
    def __init__(self):
        self._engines: Dict[str, Callable] = {}
        self._cache: Dict[str, InstantAnswer] = {}
        self._cache_ttl = 300  # 5 minutes
        
        # Register built-in engines
        self._register_engines()
    
    def _register_engines(self):
        """Register built-in answer engines"""
        pass  # Engines are defined as methods
    
    def get_answer(self, query: str) -> Optional[InstantAnswer]:
        """
        Get instant answer for query
        
        Args:
            query: The search query
        
        Returns:
            InstantAnswer if found, None otherwise
        """
        query = query.strip()
        
        # Check cache
        cache_key = self._get_cache_key(query)
        if cache_key in self._cache:
            cached = self._cache[cache_key]
            if time.time() - cached.get('_cached_at', 0) < self._cache_ttl:
                return cached
        
        # Try each answer type
        answer = (
            self._check_calculator(query) or
            self._check_conversion(query) or
            self._check_weather(query) or
            self._check_time(query) or
            self._check_ip(query)
        )
        
        if answer:
            answer._cached_at = time.time()
            self._cache[cache_key] = answer
        
        return answer
    
    def _get_cache_key(self, query: str) -> str:
        """Get cache key for query"""
        return hashlib.md5(query.lower().encode()).hexdigest()
    
    def _check_calculator(self, query: str) -> Optional[InstantAnswer]:
        """Check if query is a calculator expression"""
        for pattern in self.CALCULATOR_TRIGGERS:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                expr = match.group(1) if match.lastindex else query
                try:
                    # Safe evaluation
                    result = self._safe_eval(expr)
                    if result is not None:
                        return InstantAnswer(
                            answer_type='calculator',
                            answer=f"{expr} = {result}",
                            sources=[],
                            confidence=0.95,
                            extra={'expression': expr, 'result': result}
                        )
                except:
                    pass
        return None
    
    def _safe_eval(self, expr: str) -> Optional[float]:
        """Safely evaluate a math expression"""
        # Only allow safe characters
        if not re.match(r'^[\d\s\+\-\*\/\.\,\(\)\^]+$', expr):
            return None
        
        try:
            # Replace ^ with ** for power
            expr = expr.replace('^', '**')
            # Evaluate safely
            result = eval(expr, {"__builtins__": {}}, {})
            return float(result) if isinstance(result, (int, float)) else None
        except:
            return None
    
    def _check_conversion(self, query: str) -> Optional[InstantAnswer]:
        """Check if query is a unit conversion"""
        patterns = [
            (r'(\d+(?:\.\d+)?)\s*(?:mph|kmh|km\/h|m/s)\s*(?:to|in)?\s*(mph|kmh|km\/h|m/s)', 'speed'),
            (r'(\d+(?:\.\d+)?)\s*(?:celsius|c|f)\s*(?:to|in)?\s*(celsius|c|f)', 'temperature'),
            (r'(\d+(?:\.\d+)?)\s*(?:km|miles|mi|m|feet|ft)\s*(?:to|in)?\s*(km|miles|mi|m|feet|ft)', 'distance'),
            (r'(\d+(?:\.\d+)?)\s*(?:kg|lbs?|pounds?)\s*(?:to|in)?\s*(kg|lbs?|pounds?)', 'weight'),
        ]
        
        for pattern, conv_type in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return self._do_conversion(match, conv_type)
        
        return None
    
    def _do_conversion(self, match: re.Match, conv_type: str) -> Optional[InstantAnswer]:
        """Perform the actual conversion"""
        try:
            value = float(match.group(1))
            from_unit = match.group(2).lower()
            to_unit = match.group(3).lower()
            
            if conv_type == 'temperature':
                if from_unit in ['c', 'celsius'] and to_unit in ['f']:
                    result = (value * 9/5) + 32
                    return InstantAnswer(
                        answer_type='conversion',
                        answer=f"{value}°C = {result:.1f}°F",
                        sources=[],
                        confidence=0.95
                    )
                elif from_unit in ['f'] and to_unit in ['c', 'celsius']:
                    result = (value - 32) * 5/9
                    return InstantAnswer(
                        answer_type='conversion',
                        answer=f"{value}°F = {result:.1f}°C",
                        sources=[],
                        confidence=0.95
                    )
            
            elif conv_type == 'distance':
                conversions = {
                    ('km', 'mi'): (value * 0.621371, 'miles'),
                    ('mi', 'km'): (value * 1.60934, 'km'),
                    ('m', 'ft'): (value * 3.28084, 'feet'),
                    ('ft', 'm'): (value * 0.3048, 'meters'),
                }
                key = (from_unit[:2], to_unit[:2])
                if key in conversions:
                    result, unit = conversions[key]
                    return InstantAnswer(
                        answer_type='conversion',
                        answer=f"{value} {from_unit} = {result:.2f} {unit}",
                        sources=[],
                        confidence=0.95
                    )
            
            elif conv_type == 'weight':
                conversions = {
                    ('kg', 'lb'): (value * 2.20462, 'lbs'),
                    ('lb', 'kg'): (value * 0.453592, 'kg'),
                }
                key = (from_unit[:2], to_unit[:2])
                if key in conversions:
                    result, unit = conversions[key]
                    return InstantAnswer(
                        answer_type='conversion',
                        answer=f"{value} {from_unit} = {result:.2f} {unit}",
                        sources=[],
                        confidence=0.95
                    )
        
        except:
            pass
        
        return None
    
    def _check_weather(self, query: str) -> Optional[InstantAnswer]:
        """Check if query is a weather query"""
        for pattern in self.WEATHER_TRIGGERS:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                location = match.group(1) if match.lastindex and match.group(1) else "current location"
                return InstantAnswer(
                    answer_type='weather_search',
                    answer=f"Weather search for: {location}",
                    sources=[],
                    confidence=0.8,
                    extra={'location': location}
                )
        return None
    
    def _check_time(self, query: str) -> Optional[InstantAnswer]:
        """Check if query is a time query"""
        from datetime import datetime
        
        # Time zone patterns
        tz_patterns = [
            (r'time (?:in |at )?(.+)', 'timezone'),
            (r"what'?s? (?:the )?time', 'current'),
            (r'time$', 'current'),
        ]
        
        for pattern, time_type in tz_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                now = datetime.now()
                if time_type == 'current':
                    return InstantAnswer(
                        answer_type='time',
                        answer=f"Current time: {now.strftime('%H:%M:%S')}",
                        sources=[],
                        confidence=0.9
                    )
                else:
                    location = match.group(1)
                    return InstantAnswer(
                        answer_type='time',
                        answer=f"Time in {location}",
                        sources=[],
                        confidence=0.7
                    )
        
        return None
    
    def _check_ip(self, query: str) -> Optional[InstantAnswer]:
        """Check if query is about IP address"""
        if query.lower() in ['my ip', 'ip address', 'what is my ip', 'show my ip']:
            return InstantAnswer(
                answer_type='ip',
                answer="Your IP address is hidden for privacy",
                sources=[],
                confidence=1.0,
                extra={'privacy': True}
            )
        return None
    
    def clear_cache(self):
        """Clear the answer cache"""
        self._cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get engine statistics"""
        return {
            'cached_answers': len(self._cache),
            'cache_ttl': self._cache_ttl,
        }


# Global instance
_instant_engine = InstantAnswerEngine()


def get_instant_answer(query: str) -> Optional[InstantAnswer]:
    """Get instant answer for query"""
    return _instant_engine.get_answer(query)


def get_instant_engine() -> InstantAnswerEngine:
    """Get the instant answer engine"""
    return _instant_engine
