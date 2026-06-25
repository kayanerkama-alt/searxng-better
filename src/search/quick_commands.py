"""
Quick Search Commands for Atomic Search
Keyboard shortcuts and bang commands
"""

from typing import Dict, List, Optional, Tuple

class QuickCommands:
    """Handler for quick search commands"""
    
    # Bang commands (!command query)
    BANG_COMMANDS = {
        # Search engines
        '!g': ('google', 'https://google.com/search?q={q}'),
        '!google': ('google', 'https://google.com/search?q={q}'),
        '!duck': ('duckduckgo', 'https://duckduckgo.com/?q={q}'),
        '!ddg': ('duckduckgo', 'https://duckduckgo.com/?q={q}'),
        '!bing': ('bing', 'https://bing.com/search?q={q}'),
        '!yahoo': ('yahoo', 'https://search.yahoo.com/search?p={q}'),
        '!baidu': ('baidu', 'https://www.baidu.com/s?wd={q}'),
        
        # Knowledge
        '!w': ('wikipedia', 'https://en.wikipedia.org/w/index.php?search={q}'),
        '!wiki': ('wikipedia', 'https://en.wikipedia.org/w/index.php?search={q}'),
        '!wikt': ('wiktionary', 'https://en.wiktionary.org/w/index.php?search={q}'),
        
        # Social/News
        '!yt': ('youtube', 'https://www.youtube.com/results?search_query={q}'),
        '!youtube': ('youtube', 'https://www.youtube.com/results?search_query={q}'),
        '!twitter': ('twitter', 'https://twitter.com/search?q={q}'),
        '!reddit': ('reddit', 'https://www.reddit.com/search/?q={q}'),
        '!hn': ('hackernews', 'https://hn.algolia.com/?q={q}'),
        '!lobsters': ('lobsters', 'https://lobste.rs/search?q={q}'),
        
        # Dev
        '!gh': ('github', 'https://github.com/search?q={q}'),
        '!github': ('github', 'https://github.com/search?q={q}'),
        '!so': ('stackoverflow', 'https://stackoverflow.com/search?q={q}'),
        '!stack': ('stackoverflow', 'https://stackoverflow.com/search?q={q}'),
        '!dev': ('devto', 'https://dev.to/search?q={q}'),
        '!npm': ('npm', 'https://www.npmjs.com/search?q={q}'),
        '!pypi': ('pypi', 'https://pypi.org/search/?q={q}'),
        '!crates': ('crates', 'https://crates.io/search?q={q}'),
        
        # Research
        '!arxiv': ('arxiv', 'https://arxiv.org/search/?search-type=all&query={q}'),
        '!scholar': ('scholar', 'https://scholar.google.com/scholar?q={q}'),
        
        # Media
        '!imdb': ('imdb', 'https://www.imdb.com/find?q={q}'),
        '!spotify': ('spotify', 'https://open.spotify.com/search/{q}'),
        '!soundcloud': ('soundcloud', 'https://soundcloud.com/search?q={q}'),
        
        # Shopping
        '!amz': ('amazon', 'https://www.amazon.com/s?k={q}'),
        '!amazon': ('amazon', 'https://www.amazon.com/s?k={q}'),
        '!ebay': ('ebay', 'https://www.ebay.com/sch/i.html?_nkw={q}'),
        
        # Privacy tools
        '!privacy': ('privacy', None),  # Internal - shows privacy guide
        '!tracker': ('tracker', None),  # Internal - explains trackers
    }
    
    @classmethod
    def parse_query(cls, query: str) -> Tuple[str, Optional[Dict]]:
        """
        Parse a query for bang commands
        Returns (processed_query, command_info)
        """
        query = query.strip()
        
        for cmd, (name, url) in cls.BANG_COMMANDS.items():
            if query.startswith(cmd):
                search_term = query[len(cmd):].strip()
                if search_term:
                    return search_term, {'name': name, 'url': url, 'command': cmd}
                    
        return query, None
        
    @classmethod
    def get_command_url(cls, command: Dict, query: str) -> Optional[str]:
        """Get the URL for a command"""
        if command and command.get('url'):
            return command['url'].replace('{q}', query.replace(' ', '+'))
        return None
        
    @classmethod
    def get_autocomplete_suggestions(cls, partial: str) -> List[str]:
        """Get autocomplete suggestions for commands"""
        suggestions = []
        partial_lower = partial.lower()
        
        for cmd in cls.BANG_COMMANDS.keys():
            if cmd.startswith(partial_lower):
                suggestions.append(cmd + ' ')
                
        return suggestions[:5]  # Limit to 5 suggestions
        
    @classmethod
    def get_all_commands(cls) -> List[Dict]:
        """Get all available commands for help page"""
        return [
            {'command': cmd, 'engine': name}
            for cmd, (name, _) in cls.BANG_COMMANDS.items()
        ]


# Privacy-focused search enhancements
class PrivacyEnhancer:
    """Enhances search with privacy features"""
    
    TRACKER_PATTERNS = [
        'utm_', 'fbclid', 'gclid', 'msclkid',
        '_ga', '_gid', 'ref=', 'source=',
        'mc_cid', 'mc_eid', 'oly_enc_id',
    ]
    
    @classmethod
    def clean_url(cls, url: str) -> str:
        """Remove tracking parameters from URL"""
        from urllib.parse import urlparse, parse_qs, urlencode
        
        try:
            parsed = urlparse(url)
            qs = parse_qs(parsed.query)
            
            # Filter out tracking params
            cleaned_qs = {
                k: v for k, v in qs.items()
                if not any(pattern in k.lower() for pattern in cls.TRACKER_PATTERNS)
            }
            
            if cleaned_qs:
                new_query = urlencode(cleaned_qs, doseq=True)
            else:
                new_query = ''
                
            return parsed._replace(query=new_query).geturl()
        except:
            return url
            
    @classmethod
    def get_privacy_grade(cls, url: str) -> str:
        """Grade the privacy of a URL"""
        url_lower = url.lower()
        
        if not url.startswith('https'):
            return '⚠️ HTTP'
            
        trackers = sum(1 for p in cls.TRACKER_PATTERNS if p in url_lower)
        if trackers > 3:
            return f'🔴 {trackers} trackers'
        elif trackers > 0:
            return f'🟡 {trackers} trackers'
        else:
            return '🟢 Clean'


# Export for use in search
quick_commands = QuickCommands()
privacy_enhancer = PrivacyEnhancer()
