# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Advanced Tracker Blocker for Atomic Search
Blocks known trackers, fingerprinting scripts, and malicious domains
"""

import re
import json
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import ipaddress


class TrackerCategory(Enum):
    """Categories of trackers"""
    ANALYTICS = "analytics"
    AD = "advertising"
    SOCIAL = "social"
    FINGERPRINT = "fingerprinting"
    CRYPTOMINING = "cryptomining"
    MALICIOUS = "malicious"
    WIDGET = "widget"
    CUSTOM = "custom"


@dataclass
class TrackerRule:
    """Rule for blocking trackers"""
    pattern: str
    category: TrackerCategory
    description: str
    action: str = "block"  # block, warn, allow
    source: str = "default"
    weight: int = 1


@dataclass
class BlockingStats:
    """Statistics for tracker blocking"""
    trackers_blocked: int = 0
    scripts_removed: int = 0
    requests_blocked: int = 0
    by_category: Dict[str, int] = field(default_factory=dict)
    blocked_domains: Set[str] = field(default_factory=set)


class AdvancedTrackerBlocker:
    """
    Advanced tracker blocking system
    Blocks trackers based on domain lists, patterns, and heuristics
    """
    
    # Built-in tracker domains (partial list)
    BUILTIN_TRACKERS: Dict[str, TrackerRule] = {
        # Analytics
        'google-analytics.com': TrackerRule(
            'google-analytics.com', TrackerCategory.ANALYTICS, 'Google Analytics'
        ),
        'googletagmanager.com': TrackerRule(
            'googletagmanager.com', TrackerCategory.ANALYTICS, 'Google Tag Manager'
        ),
        'googlesyndication.com': TrackerRule(
            'googlesyndication.com', TrackerCategory.AD, 'Google AdSense'
        ),
        'googleadservices.com': TrackerRule(
            'googleadservices.com', TrackerCategory.AD, 'Google Ad Services'
        ),
        'doubleclick.net': TrackerRule(
            'doubleclick.net', TrackerCategory.AD, 'DoubleClick (Google)'
        ),
        'facebook.net': TrackerRule(
            'facebook.net', TrackerCategory.SOCIAL, 'Facebook SDK'
        ),
        'facebook.com/plugins': TrackerRule(
            'facebook.com/plugins', TrackerCategory.SOCIAL, 'Facebook Plugins'
        ),
        'connect.facebook.net': TrackerRule(
            'connect.facebook.net', TrackerCategory.SOCIAL, 'Facebook Connect'
        ),
        'twitter.com/widgets': TrackerRule(
            'twitter.com/widgets', TrackerCategory.WIDGET, 'Twitter Widgets'
        ),
        'platform.twitter.com': TrackerRule(
            'platform.twitter.com', TrackerCategory.WIDGET, 'Twitter Platform'
        ),
        'linkedin.com/embed': TrackerRule(
            'linkedin.com/embed', TrackerCategory.WIDGET, 'LinkedIn Embed'
        ),
        'analytics.twitter.com': TrackerRule(
            'analytics.twitter.com', TrackerCategory.ANALYTICS, 'Twitter Analytics'
        ),
        # Fingerprinting
        'fingerprintjs.com': TrackerRule(
            'fingerprintjs.com', TrackerCategory.FINGERPRINT, 'FingerprintJS'
        ),
        'iovation.com': TrackerRule(
            'iovation.com', TrackerCategory.FINGERPRINT, 'iovation'
        ),
        'threatmetrix.com': TrackerRule(
            'threatmetrix.com', TrackerCategory.FINGERPRINT, 'ThreatMetrix'
        ),
        # Ad networks
        'adnxs.com': TrackerRule(
            'adnxs.com', TrackerCategory.AD, 'AppNexus'
        ),
        'criteo.com': TrackerRule(
            'criteo.com', TrackerCategory.AD, 'Criteo'
        ),
        'outbrain.com': TrackerRule(
            'outbrain.com', TrackerCategory.AD, 'Outbrain'
        ),
        'taboola.com': TrackerRule(
            'taboola.com', TrackerCategory.AD, 'Taboola'
        ),
        'moatads.com': TrackerRule(
            'moatads.com', TrackerCategory.AD, 'Moat'
        ),
        # Cryptomining
        'coinhive.com': TrackerRule(
            'coinhive.com', TrackerCategory.CRYPTOMINING, 'CoinHive'
        ),
        'coin-hive.com': TrackerRule(
            'coin-hive.com', TrackerCategory.CRYPTOMINING, 'CoinHive'
        ),
        'cryptoloot.pro': TrackerRule(
            'cryptoloot.pro', TrackerCategory.CRYPTOMINING, 'CryptoLoot'
        ),
        'jsecoin.com': TrackerRule(
            'jsecoin.com', TrackerCategory.CRYPTOMINING, 'JSEcoin'
        ),
        # Malicious
        'malware-domain.com': TrackerRule(
            'malware-domain.com', TrackerCategory.MALICIOUS, 'Known malware'
        ),
    }
    
    # Fingerprinting script patterns
    FINGERPRINT_PATTERNS = [
        r'canvas.*fingerprint',
        r'webgl.*fingerprint',
        r'audio.*fingerprint',
        r'font.*fingerprint',
        r'behavior.*fingerprint',
        r'fingerprint2?',
        r'clientjs',
        r'tracking.*id',
    ]
    
    def __init__(self):
        self._custom_rules: Dict[str, TrackerRule] = {}
        self._blocked_domains: Set[str] = set()
        self._allowed_domains: Set[str] = set()
        self._stats = BlockingStats()
        
        # Load built-in rules
        for domain, rule in self.BUILTIN_TRACKERS.items():
            self._blocked_domains.add(domain)
    
    def add_custom_rule(
        self, 
        pattern: str, 
        category: TrackerCategory,
        description: str = "",
        action: str = "block"
    ) -> TrackerRule:
        """Add a custom blocking rule"""
        rule = TrackerRule(
            pattern=pattern,
            category=category,
            description=description,
            action=action,
            source="custom"
        )
        self._custom_rules[pattern] = rule
        
        if action == "block":
            self._blocked_domains.add(pattern)
        elif action == "allow":
            self._allowed_domains.add(pattern)
        
        return rule
    
    def remove_rule(self, pattern: str) -> bool:
        """Remove a custom rule"""
        if pattern in self._custom_rules:
            del self._custom_rules[pattern]
            self._blocked_domains.discard(pattern)
            self._allowed_domains.discard(pattern)
            return True
        return False
    
    def check_domain(self, domain: str) -> Tuple[bool, Optional[TrackerRule], TrackerCategory]:
        """
        Check if a domain should be blocked
        
        Returns:
            Tuple of (should_block, rule, category)
        """
        domain_lower = domain.lower()
        
        # Check allowed list first
        if domain_lower in self._allowed_domains:
            return False, None, TrackerCategory.CUSTOM
        
        # Check custom rules
        for pattern, rule in self._custom_rules.items():
            if self._matches_pattern(domain_lower, pattern):
                self._update_stats(rule.category, domain_lower)
                return rule.action == "block", rule, rule.category
        
        # Check built-in rules
        for pattern, rule in self.BUILTIN_TRACKERS.items():
            if self._matches_pattern(domain_lower, pattern):
                self._update_stats(rule.category, domain_lower)
                return True, rule, rule.category
        
        return False, None, TrackerCategory.CUSTOM
    
    def check_url(self, url: str) -> Tuple[bool, Optional[TrackerRule], TrackerCategory]:
        """Check if a URL contains trackers"""
        import re
        from urllib.parse import urlparse
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            
            # Check domain
            block, rule, category = self.check_domain(domain)
            if block:
                return True, rule, category
            
            # Check path for tracking patterns
            path_lower = (parsed.path + parsed.query).lower()
            for pattern in self.TRACKACK_PATTERNS:
                if re.search(pattern, path_lower):
                    self._update_stats(TrackerCategory.ANALYTICS, url)
                    return True, None, TrackerCategory.ANALYTICS
            
        except Exception:
            pass
        
        return False, None, TrackerCategory.CUSTOM
    
    def check_script(self, script_content: str) -> Tuple[bool, List[str]]:
        """
        Check if script content contains fingerprinting code
        
        Returns:
            Tuple of (is_fingerprinting, detected_patterns)
        """
        detected = []
        
        for pattern in self.FINGERPRINT_PATTERNS:
            if re.search(pattern, script_content, re.IGNORECASE):
                detected.append(pattern)
        
        return len(detected) > 0, detected
    
    def remove_tracking_params(self, url: str) -> str:
        """Remove known tracking parameters from URL"""
        import re
        from urllib.parse import urlparse, parse_qs, urlencode
        
        try:
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)
            
            # Tracking parameters to remove
            tracking_params = [
                # UTM parameters
                r'^utm_', r'^utm-',
                # Google
                r'^gclid', r'^gclsrc', r'^dclid',
                # Facebook
                r'^fbclid',
                # Microsoft/Bing
                r'^msclkid',
                # Generic
                r'^ref$', r'^referrer',
                # Marketing
                r'^mc_', r'^mk_', r'^affiliate',
                # Click tracking
                r'^click_', r'^tracking',
            ]
            
            # Filter out tracking params
            clean_params = {
                k: v for k, v in query_params.items()
                if not any(re.match(p, k.lower()) for p in tracking_params)
            }
            
            # Reconstruct URL
            if clean_params:
                new_query = urlencode(clean_params, doseq=True)
                url = parsed._replace(query=new_query).geturl()
            else:
                url = parsed._replace(query='').geturl()
                
        except Exception:
            pass
        
        return url
    
    def _matches_pattern(self, text: str, pattern: str) -> bool:
        """Check if text matches pattern"""
        # Exact match
        if pattern in text:
            return True
        
        # Wildcard pattern
        if '*' in pattern:
            regex = pattern.replace('.', r'\.').replace('*', '.*')
            return bool(re.match(regex, text))
        
        # Domain match (example.com matches www.example.com)
        if text.endswith(pattern):
            return True
        
        return False
    
    def _update_stats(self, category: TrackerCategory, domain: str) -> None:
        """Update blocking statistics"""
        self._stats.trackers_blocked += 1
        self._stats.blocked_domains.add(domain)
        
        cat_name = category.value
        self._stats.by_category[cat_name] = self._stats.by_category.get(cat_name, 0) + 1
    
    def get_stats(self) -> BlockingStats:
        """Get blocking statistics"""
        return self._stats
    
    def reset_stats(self) -> None:
        """Reset statistics"""
        self._stats = BlockingStats()
    
    def export_rules(self) -> List[Dict]:
        """Export custom rules"""
        return [
            {
                'pattern': p,
                'category': r.category.value,
                'description': r.description,
                'action': r.action
            }
            for p, r in self._custom_rules.items()
        ]
    
    def import_rules(self, rules: List[Dict]) -> int:
        """Import custom rules"""
        count = 0
        for rule in rules:
            try:
                self.add_custom_rule(
                    pattern=rule['pattern'],
                    category=TrackerCategory(rule.get('category', 'custom')),
                    description=rule.get('description', ''),
                    action=rule.get('action', 'block')
                )
                count += 1
            except Exception:
                pass
        return count


# Missing import fix - add TRACKACK_PATTERNS
AdvancedTrackerBlocker.TRACKACK_PATTERNS = [
    r'tracking', r'analytics', r'pixel', r'beacon',
    r'\/t\.gif', r'\/track', r'\/collect',
]


# Global instance
_tracker_blocker = AdvancedTrackerBlocker()


def get_tracker_blocker() -> AdvancedTrackerBlocker:
    """Get the tracker blocker instance"""
    return _tracker_blocker


def is_tracker_blocked(domain: str) -> bool:
    """Check if domain is a known tracker"""
    return _tracker_blocker.check_domain(domain)[0]


def clean_url(url: str) -> str:
    """Remove tracking parameters from URL"""
    return _tracker_blocker.remove_tracking_params(url)
