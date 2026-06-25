# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Smart Domain Ranking for Atomic Search
Provides Kagi-style domain control: pin, block, and weight domains
"""

import hashlib
import json
import time
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, asdict
from enum import Enum


class DomainAction(Enum):
    """Domain action types"""
    PINNED = "pinned"      # Always show at top
    BOOSTED = "boosted"    # Higher priority
    NEUTRAL = "neutral"   # Default behavior
    DEMOTED = "demoted"   # Lower priority
    BLOCKED = "blocked"   # Never show


@dataclass
class DomainRule:
    """Rule for a domain"""
    domain: str
    action: str
    weight: float = 1.0  # 0.0 to 2.0 multiplier
    reason: str = ""
    added_at: int = 0
    expires_at: int = 0  # 0 = never expires
    click_count: int = 0
    search_count: int = 0
    
    def is_expired(self) -> bool:
        """Check if rule has expired"""
        if self.expires_at == 0:
            return False
        return time.time() > self.expires_at


class DomainRanking:
    """
    Manages domain ranking rules for search results
    Supports: pinning, blocking, boosting, and custom weights
    """
    
    # Default weights for different content types
    CONTENT_WEIGHTS = {
        'news': 1.2,
        'academic': 1.3,
        'official': 1.4,
        'social': 0.8,
        'aggregator': 0.7,
        'spam': 0.0,
    }
    
    # Known reputable domains (auto-boosted)
    TRUSTED_DOMAINS = {
        'wikipedia.org': 1.5,
        'github.com': 1.3,
        'stackoverflow.com': 1.4,
        'medium.com': 1.1,
        'dev.to': 1.2,
        'reddit.com': 0.9,
        'twitter.com': 0.8,
        'youtube.com': 0.9,
        'google.com': 0.7,
        'duckduckgo.com': 0.8,
    }
    
    def __init__(self):
        self._rules: Dict[str, DomainRule] = {}
        self._search_history: Dict[str, List[str]] = {}  # query -> domains shown
        self._click_history: Dict[str, int] = {}  # domain -> click count
    
    def add_rule(
        self,
        domain: str,
        action: str,
        weight: float = 1.0,
        reason: str = "",
        duration: int = 0
    ) -> DomainRule:
        """
        Add a ranking rule for a domain
        
        Args:
            domain: Domain name (e.g., "example.com")
            action: One of "pinned", "boosted", "neutral", "demoted", "blocked"
            weight: Custom weight multiplier (0.0 to 2.0)
            reason: Reason for the rule
            duration: Duration in seconds (0 = permanent)
        
        Returns:
            The created DomainRule
        """
        domain = self._normalize_domain(domain)
        
        rule = DomainRule(
            domain=domain,
            action=action,
            weight=weight,
            reason=reason,
            added_at=int(time.time()),
            expires_at=int(time.time() + duration) if duration > 0 else 0
        )
        
        self._rules[domain] = rule
        return rule
    
    def remove_rule(self, domain: str) -> bool:
        """Remove ranking rule for domain"""
        domain = self._normalize_domain(domain)
        if domain in self._rules:
            del self._rules[domain]
            return True
        return False
    
    def get_rule(self, domain: str) -> Optional[DomainRule]:
        """Get rule for domain"""
        domain = self._normalize_domain(domain)
        return self._rules.get(domain)
    
    def is_blocked(self, domain: str) -> bool:
        """Check if domain is blocked"""
        rule = self.get_rule(domain)
        return rule is not None and rule.action == DomainAction.BLOCKED.value
    
    def is_pinned(self, domain: str) -> bool:
        """Check if domain is pinned"""
        rule = self.get_rule(domain)
        return rule is not None and rule.action == DomainAction.PINNED.value
    
    def get_weight(self, domain: str) -> float:
        """
        Get effective weight for domain
        
        Returns:
            Weight multiplier (0.0 to 2.0+)
        """
        domain = self._normalize_domain(domain)
        
        # Check custom rule first
        rule = self.get_rule(domain)
        if rule:
            if rule.action == DomainAction.BLOCKED.value:
                return 0.0
            return rule.weight
        
        # Check trusted domains
        for trusted, weight in self.TRUSTED_DOMAINS.items():
            if domain.endswith(trusted) or domain == trusted:
                return weight
        
        # Default weight
        return 1.0
    
    def rank_results(
        self,
        results: List[Dict[str, Any]],
        pinned_first: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Re-rank search results based on domain rules
        
        Args:
            results: List of search result dicts with 'url' and optional 'base_url'
            pinned_first: Whether to put pinned domains first
        
        Returns:
            Re-ranked list of results
        """
        if not results:
            return results
        
        # Calculate scores for each result
        scored_results = []
        for i, result in enumerate(results):
            url = result.get('url', '')
            base_url = result.get('base_url', '')
            domain = base_url if base_url else self._extract_domain(url)
            
            weight = self.get_weight(domain)
            rule = self.get_rule(domain)
            
            # Base score from position (lower is better)
            base_score = i
            
            # Apply domain weight
            if weight > 0:
                effective_score = base_score / weight
            else:
                effective_score = float('inf')  # Blocked
            
            # Pinned domains go first
            if pinned_first and rule and rule.action == DomainAction.PINNED.value:
                effective_score = -1000
            
            scored_results.append({
                'result': result,
                'domain': domain,
                'weight': weight,
                'score': effective_score,
                'rule': rule
            })
        
        # Sort by score (lower is better)
        scored_results.sort(key=lambda x: x['score'])
        
        # Extract sorted results
        ranked = []
        for sr in scored_results:
            if sr['score'] != float('inf'):  # Skip blocked
                result = sr['result'].copy()
                result['_domain_rank'] = self._get_rank_label(sr['rule'], sr['weight'])
                result['_domain_trusted'] = sr['weight'] > 1.0
                ranked.append(result)
        
        return ranked
    
    def record_impression(self, domain: str) -> None:
        """Record that a domain was shown in results"""
        domain = self._normalize_domain(domain)
        rule = self.get_rule(domain)
        if rule:
            rule.search_count += 1
    
    def record_click(self, domain: str) -> None:
        """Record that a user clicked on a domain"""
        domain = self._normalize_domain(domain)
        rule = self.get_rule(domain)
        if rule:
            rule.click_count += 1
        self._click_history[domain] = self._click_history.get(domain, 0) + 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get ranking statistics"""
        total_rules = len(self._rules)
        blocked = sum(1 for r in self._rules.values() if r.action == DomainAction.BLOCKED.value)
        pinned = sum(1 for r in self._rules.values() if r.action == DomainAction.PINNED.value)
        
        return {
            'total_rules': total_rules,
            'blocked': blocked,
            'pinned': pinned,
            'boosted': sum(1 for r in self._rules.values() if r.action == DomainAction.BOOSTED.value),
            'total_clicks': sum(self._click_history.values()),
            'unique_clicked_domains': len(self._click_history),
        }
    
    def export_rules(self) -> List[Dict[str, Any]]:
        """Export all rules as list"""
        return [asdict(r) for r in self._rules.values() if not r.is_expired()]
    
    def import_rules(self, rules: List[Dict[str, Any]]) -> int:
        """Import rules from list"""
        count = 0
        for rule_data in rules:
            try:
                rule = DomainRule(**rule_data)
                if not rule.is_expired():
                    self._rules[rule.domain] = rule
                    count += 1
            except Exception:
                continue
        return count
    
    def cleanup_expired(self) -> int:
        """Remove expired rules"""
        expired = [d for d, r in self._rules.items() if r.is_expired()]
        for d in expired:
            del self._rules[d]
        return len(expired)
    
    @staticmethod
    def _normalize_domain(domain: str) -> str:
        """Normalize domain for consistent lookup"""
        domain = domain.lower().strip()
        # Remove protocol
        if '://' in domain:
            domain = domain.split('://', 1)[1]
        # Remove path
        domain = domain.split('/', 1)[0]
        # Remove www
        if domain.startswith('www.'):
            domain = domain[4:]
        # Remove port
        domain = domain.split(':', 1)[0]
        return domain
    
    @staticmethod
    def _extract_domain(url: str) -> str:
        """Extract domain from URL"""
        if not url:
            return ''
        return DomainRanking._normalize_domain(url)
    
    @staticmethod
    def _get_rank_label(rule: Optional[DomainRule], weight: float) -> str:
        """Get human-readable rank label"""
        if not rule:
            if weight > 1.2:
                return "trusted"
            elif weight < 0.8:
                return "low"
            return "standard"
        
        return rule.action


# Global ranking instance
_domain_ranking = DomainRanking()


def get_domain_ranking() -> DomainRanking:
    """Get the global domain ranking instance"""
    return _domain_ranking
