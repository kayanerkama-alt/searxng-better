# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Privacy Filters for Atomic Search
Cleans URLs and removes tracking parameters
"""

import re
import urllib.parse
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass


@dataclass
class CleanedURL:
    """A cleaned URL with tracking removed"""
    url: str
    original: str
    tracking_removed: int
    parameters_removed: List[str]


class PrivacyFilter:
    """
    Privacy filter that removes tracking parameters and cleans URLs
    
    Removes:
    - UTM parameters
    - Facebook tracking
    - Google tracking
    - Amazon tracking
    - Microsoft tracking
    - Generic click tracking
    - Referrer leakage
    """
    
    # Known tracking parameters by service
    TRACKING_PARAMS: Dict[str, List[str]] = {
        # Analytics & Marketing
        'utm': ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'utm_id', 'utm_source_platform', 'utm_creative_format', 'utm_marketing_tactic'],
        'fb': ['fbclid', 'fb_action_ids', 'fb_action_types', 'fb_source', 'fb_ref'],
        'google': ['gclid', 'gclsrc', 'dclid', 'aclid', 'ztautos'],
        'msn': ['msclkid'],
        'bing': ['msqrid'],
        'yahoo': ['ysmvcid', 'vcamp', 'ved', 'ei', 'sig'],
        'yandex': ['_openstat', 'from', 'lr'],
        'mail': ['mc_cid', 'mc_eid'],
        
        # Social Media
        'twitter': ['twclid', 'tweet_picture'],
        'linkedin': ['li_fat_id'],
        'pinterest': ['pp'],
        
        # E-commerce
        'amazon': ['pd_rd_w', 'pd_rd_r', 'pf_rd_p', 'pf_rd_r', 'linkCode', 'tag'],
        'ebay': ['aff_param', 'affiliateId', 'campid', 'mkevt', 'mkrid'],
        
        # Generic click tracking
        'click': ['click_id', 'clickid', 'clickref', 'ref', 'ref_'],
        'track': ['trk', 'tracking', 'tracking_id'],
        'source': ['source', 'src'],
        'campaign': ['cmp', 'campaign_id'],
        
        # Other known trackers
        'hubspot': ['hsa_acc', 'hsa_cam', 'hsa_grp', 'hsa_ad', 'hsa_src', 'hsa_tgt', 'hsa_kw', 'hsa_mt', 'hsa_net', 'hsa_ver'],
        'mailchimp': ['mc_eid', 'mc_cid'],
        'segment': ['ajs_event', 'ajs_user_id', 'ajs_anonymous_id'],
        'mixpanel': ['mp_key', 'mp_event'],
        'intercom': ['intercom_new_user'],
        'crisp': ['crisp_event'],
    }
    
    # Flatten for quick lookup
    ALL_TRACKING_PARAMS: Set[str] = set()
    for params in TRACKING_PARAMS.values():
        ALL_TRACKING_PARAMS.update(p.lower() for p in params)
    
    # Patterns that indicate tracking
    TRACKING_PATTERNS = [
        r'&?ref=[^&]+',
        r'&?referrer=[^&]+',
        r'&?_ga=[^&]+',
        r'&?__s=[^&]+',
        r'&?trk=[^&]+',
        r'&?igshid=[^&]+',
        r'&?oly_enc_id=[^&]+',
        r'&?oly_anon_id=[^&]+',
    ]
    
    # Domains to block (known malware/tracking)
    BLOCKED_DOMAINS: Set[str] = {
        'doubleclick.net',
        'googlesyndication.com',
        'googleadservices.com',
        'facebook.com/tr',
        'pixel.facebook.com',
        'analytics.twitter.com',
        'ads.linkedin.com',
    }
    
    # URL shorteners to expand
    URL_SHORTENERS: Set[str] = {
        't.co',
        'bit.ly',
        'goo.gl',
        'tinyurl.com',
        'ow.ly',
        'is.gd',
        'buff.ly',
        'fb.com',
        'lnkd.in',
        'db.tt',
        'qr.ae',
        'adf.ly',
        'bit.do',
        'mcaf.ee',
        'su.pr',
        'tiny.cc',
        'short.to',
        'url.ie',
        'shorl.com',
        'x.co',
        'v.gd',
        'tr.im',
        'cli.gs',
    }
    
    def __init__(self):
        self._custom_blocked: Set[str] = set()
        self._custom_allowed: Set[str] = set()
    
    def add_blocked_domain(self, domain: str) -> None:
        """Add a domain to the blocked list"""
        self._custom_blocked.add(domain.lower())
    
    def add_allowed_domain(self, domain: str) -> None:
        """Add a domain to the allowed list (overrides blocked)"""
        self._custom_allowed.add(domain.lower())
    
    def is_blocked_domain(self, url: str) -> bool:
        """Check if domain is blocked"""
        parsed = urllib.parse.urlparse(url)
        domain = parsed.netloc.lower()
        
        # Check custom allowed first
        if domain in self._custom_allowed:
            return False
        
        # Check custom blocked
        if domain in self._custom_blocked:
            return True
        
        # Check known blocked
        for blocked in self.BLOCKED_DOMAINS:
            if blocked in domain:
                return True
        
        return False
    
    def clean_url(self, url: str) -> CleanedURL:
        """
        Clean a URL by removing tracking parameters
        
        Args:
            url: Original URL
        
        Returns:
            CleanedURL with cleaned URL and metadata
        """
        original = url
        removed_params: List[str] = []
        
        try:
            parsed = urllib.parse.urlparse(url)
            
            # Parse query parameters
            if parsed.query:
                params = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
                cleaned_params = []
                
                for key, value in params:
                    key_lower = key.lower()
                    
                    # Check if parameter should be removed
                    if self._should_remove_param(key_lower, value):
                        removed_params.append(f"{key}={value}")
                    else:
                        cleaned_params.append((key, value))
                
                # Rebuild URL
                if cleaned_params:
                    new_query = urllib.parse.urlencode(cleaned_params)
                else:
                    new_query = ''
                
                # Remove fragments (often used for tracking)
                url = urllib.parse.urlunparse((
                    parsed.scheme,
                    parsed.netloc,
                    parsed.path,
                    parsed.params,
                    new_query,
                    ''  # Remove fragment
                ))
            else:
                # Apply pattern-based removal
                for pattern in self.TRACKING_PATTERNS:
                    if re.search(pattern, url, re.IGNORECASE):
                        match = re.search(pattern, url, re.IGNORECASE)
                        if match:
                            removed_params.append(match.group(0))
                            url = url[:match.start()] + url[match.end():]
            
            # Clean up multiple ampersands
            url = re.sub(r'&+', '&', url)
            url = re.sub(r'\?&', '?', url)
            url = url.rstrip('&')
            
            # Remove trailing ?
            if url.endswith('?'):
                url = url[:-1]
        
        except Exception:
            # If parsing fails, return original
            return CleanedURL(url=original, original=original, tracking_removed=0, parameters_removed=[])
        
        return CleanedURL(
            url=url,
            original=original,
            tracking_removed=len(removed_params),
            parameters_removed=removed_params
        )
    
    def _should_remove_param(self, key: str, value: str) -> bool:
        """Determine if a parameter should be removed"""
        # Check if it's a known tracking parameter
        if key in self.ALL_TRACKING_PARAMS:
            return True
        
        # Check for common tracking patterns in value
        tracking_patterns = [
            r'utm_',
            r'fbclid',
            r'gclid',
            r'ref=',
            r'track',
            r'click',
            r'mc_',
            r'_ga=',
        ]
        
        value_lower = value.lower()
        for pattern in tracking_patterns:
            if pattern in value_lower:
                return True
        
        return False
    
    def extract_clean_domain(self, url: str) -> str:
        """Extract clean domain from URL"""
        try:
            parsed = urllib.parse.urlparse(url)
            domain = parsed.netloc.lower()
            
            # Remove www
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # Remove port
            if ':' in domain:
                domain = domain.split(':')[0]
            
            return domain
        except:
            return ''
    
    def should_proxy_image(self, url: str) -> bool:
        """
        Determine if an image should be proxied
        
        Reasons to proxy:
        - Contains tracking parameters
        - From known tracker domains
        - Contains user-specific data
        """
        # Always proxy images with tracking
        cleaned = self.clean_url(url)
        if cleaned.tracking_removed > 0:
            return True
        
        # Check domain
        domain = self.extract_clean_domain(url)
        tracker_domains = {
            'doubleclick.net',
            'googleadservices.com',
            'googlesyndication.com',
            'amazon-adsystem.com',
            'facebook.com/tr',
        }
        
        for tracker in tracker_domains:
            if tracker in domain:
                return True
        
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get filter statistics"""
        return {
            'blocked_domains': len(self._custom_blocked),
            'allowed_domains': len(self._custom_allowed),
            'tracking_params_known': len(self.ALL_TRACKING_PARAMS),
            'blocked_domain_patterns': len(self.BLOCKED_DOMAINS),
        }


# Global instance
_privacy_filter = PrivacyFilter()


def clean_url(url: str) -> CleanedURL:
    """Clean a URL"""
    return _privacy_filter.clean_url(url)


def is_blocked_domain(url: str) -> bool:
    """Check if domain is blocked"""
    return _privacy_filter.is_blocked_domain(url)


def get_privacy_filter() -> PrivacyFilter:
    """Get the privacy filter"""
    return _privacy_filter
