# SPDX-License-Identifier: AGPL-3.0-or-later
"""
AI Summary Feature for Atomic Search
Generate summaries of search results
"""

import re
import hashlib
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class Summary:
    """Search result summary"""
    query: str
    key_points: List[str]
    overview: str
    related_topics: List[str]


class AISummary:
    """
    Generate AI-like summaries of search results
    Uses heuristics to extract key information
    """
    
    # Common patterns for extracting information
    YEAR_PATTERN = r'\b(19|20)\d{2}\b'
    NUMBER_PATTERN = r'\b\d+(?:\.\d+)?(?: million| billion| thousand)?\b'
    PERCENT_PATTERN = r'\b\d+(?:\.\d+)?%\b'
    
    # Trusted domains
    TRUSTED_DOMAINS = {
        'wikipedia.org': 1.0,
        'github.com': 0.9,
        'stackoverflow.com': 0.9,
        'medium.com': 0.7,
        'reddit.com': 0.6,
    }
    
    def __init__(self):
        self.cache: Dict[str, Summary] = {}
    
    def generate_summary(self, query: str, results: List[Dict[str, Any]]) -> Summary:
        """
        Generate a summary of search results
        
        Args:
            query: The search query
            results: List of search result dicts with 'title', 'url', 'description', 'content'
        
        Returns:
            Summary object with key points and overview
        """
        # Check cache
        cache_key = hashlib.md5((query + str(len(results))).encode()).hexdigest()
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Extract key information
        key_points = self._extract_key_points(query, results)
        overview = self._generate_overview(query, results)
        related = self._extract_related_topics(results)
        
        summary = Summary(
            query=query,
            key_points=key_points,
            overview=overview,
            related_topics=related
        )
        
        self.cache[cache_key] = summary
        return summary
    
    def _extract_key_points(self, query: str, results: List[Dict]) -> List[str]:
        """Extract key points from results"""
        points = []
        seen = set()
        
        for result in results[:10]:
            title = result.get('title', '')
            desc = result.get('description', '')
            content = result.get('content', desc)
            
            # Extract years
            years = re.findall(self.YEAR_PATTERN, content)
            if years and len(years) <= 3:
                year = max(set(years), key=years.count)
                if year not in seen:
                    points.append(f"{title[:50]}... ({year})")
                    seen.add(year)
            
            # Extract percentages
            percents = re.findall(self.PERCENT_PATTERN, content)
            if percents and len(percents) == 1:
                if percents[0] not in seen:
                    points.append(f"{title[:40]}: {percents[0]}")
                    seen.add(percents[0])
            
            # Numbers
            numbers = re.findall(self.NUMBER_PATTERN, content[:200])
            if numbers and len(numbers) == 1:
                num = numbers[0]
                if len(num) < 15 and num not in seen:
                    points.append(f"{title[:40]}: {num}")
                    seen.add(num)
        
        return points[:5]
    
    def _generate_overview(self, query: str, results: List[Dict]) -> str:
        """Generate overview of the topic"""
        if not results:
            return "No results found."
        
        # Count trusted sources
        trusted_count = sum(
            1 for r in results
            if any(domain in r.get('url', '') for domain in self.TRUSTED_DOMAINS)
        )
        
        # Build overview
        overview = f"Found {len(results)} results for '{query}'. "
        
        if trusted_count > 0:
            overview += f"{trusted_count} from trusted sources. "
        
        # Extract common themes from titles
        titles = [r.get('title', '') for r in results[:5]]
        if titles:
            overview += f"Top result: {titles[0][:60]}..."
        
        return overview
    
    def _extract_related_topics(self, results: List[Dict]) -> List[str]:
        """Extract related topics from results"""
        topics = set()
        
        for result in results[:10]:
            title = result.get('title', '')
            desc = result.get('description', '')
            
            # Extract capitalized words (likely proper nouns)
            words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', title + ' ' + desc)
            topics.update(words[:3])
        
        return list(topics)[:5]
    
    def get_trust_score(self, url: str) -> float:
        """Get trust score for a URL"""
        for domain, score in self.TRUSTED_DOMAINS.items():
            if domain in url:
                return score
        return 0.5  # Default neutral score
    
    def enhance_results(self, results: List[Dict]) -> List[Dict]:
        """Enhance results with trust scores and highlights"""
        enhanced = []
        
        for result in results:
            url = result.get('url', '')
            trust = self.get_trust_score(url)
            
            # Add trust badge
            if trust >= 0.9:
                badge = "✓ Trusted"
            elif trust >= 0.7:
                badge = "○ Verified"
            elif trust >= 0.5:
                badge = "? Unknown"
            else:
                badge = "⚠ Caution"
            
            enhanced.append({
                **result,
                'trust_score': trust,
                'trust_badge': badge,
                'ai_summary': self.generate_summary(result.get('title', ''), [result])
            })
        
        return enhanced
    
    def clear_cache(self):
        """Clear the summary cache"""
        self.cache.clear()


# Global instance
_ai_summary = AISummary()


def generate_summary(query: str, results: List[Dict]) -> Summary:
    """Generate summary for search results"""
    return _ai_summary.generate_summary(query, results)


def enhance_results(results: List[Dict]) -> List[Dict]:
    """Enhance results with trust scores"""
    return _ai_summary.enhance_results(results)


def get_ai_summary() -> AISummary:
    """Get AI summary instance"""
    return _ai_summary
