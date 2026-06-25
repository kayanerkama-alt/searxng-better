# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Search Shortcuts for Atomic Search
Quick commands for power users
"""

import re
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass


@dataclass
class Shortcut:
    """A search shortcut"""
    trigger: str
    name: str
    description: str
    query: str
    icon: str = "🔍"
    category: str = "general"


class ShortcutEngine:
    """
    Search shortcuts for quick access
    Examples:
    - !g python tutorial -> search Google
    - !w github -> search Wikipedia
    - !yt music -> search YouTube
    - !gh repo -> search GitHub
    """
    
    BUILTIN_SHORTCUTS = [
        # Search engines
        Shortcut("!g", "Google", "Search Google", "https://google.com/search?q=", "🔍", "search"),
        Shortcut("!duck", "DuckDuckGo", "Search DuckDuckGo", "https://duckduckgo.com/?q=", "🦆", "search"),
        Shortcut("!bing", "Bing", "Search Bing", "https://bing.com/search?q=", "🔎", "search"),
        Shortcut("!brave", "Brave Search", "Search Brave", "https://search.brave.com/search?q=", "🦁", "search"),
        
        # Wikipedia & Wiki
        Shortcut("!w", "Wikipedia", "Search Wikipedia", "https://en.wikipedia.org/wiki/", "📚", "wiki"),
        Shortcut("!wt", "WikiTongo", "Search WikiTongo", "https://wikiless.rawbit.it/wiki/", "📖", "wiki"),
        Shortcut("!wikidata", "WikiData", "Search WikiData", "https://www.wikidata.org/wiki/", "🗃️", "wiki"),
        
        # Code & Dev
        Shortcut("!gh", "GitHub", "Search GitHub", "https://github.com/search?q=", "🐙", "code"),
        Shortcut("!so", "StackOverflow", "Search StackOverflow", "https://stackoverflow.com/search?q=", "📚", "code"),
        Shortcut("!dev", "Dev.to", "Search Dev.to", "https://dev.to/search?q=", "👩‍💻", "code"),
        Shortcut("!npm", "NPM", "Search NPM", "https://www.npmjs.com/search?q=", "📦", "code"),
        Shortcut("!pypi", "PyPI", "Search Python packages", "https://pypi.org/search/?q=", "🐍", "code"),
        Shortcut("!crates", "Crates.io", "Search Rust crates", "https://crates.io/search?q=", "🦀", "code"),
        
        # Video & Media
        Shortcut("!yt", "YouTube", "Search YouTube", "https://youtube.com/results?search_query=", "▶️", "video"),
        Shortcut("!lbry", "LBRY", "Search LBRY", "https://lbry.tv/search?q=", "🎬", "video"),
        Shortcut("!peertube", "PeerTube", "Search PeerTube", "https://sepiasearch.org/search?search=", "📹", "video"),
        Shortcut("!invidious", "Invidious", "Search Invidious", "https://yewtu.be/search?q=", "🎥", "video"),
        
        # Social
        Shortcut("!r", "Reddit", "Search Reddit", "https://reddit.com/search/?q=", "🤖", "social"),
        Shortcut("!hn", "Hacker News", "Search Hacker News", "https://hn.algolia.com/?q=", "📰", "social"),
        Shortcut("!lobsters", "Lobsters", "Search Lobsters", "https://lobste.rs/search?q=", "🦞", "social"),
        
        # Maps & Travel
        Shortcut("!maps", "OpenStreetMap", "Search Maps", "https://www.openstreetmap.org/search?query=", "🗺️", "maps"),
        Shortcut("!maps2", "Google Maps", "Search Google Maps", "https://www.google.com/maps/search/", "📍", "maps"),
        
        # Shopping
        Shortcut("!amz", "Amazon", "Search Amazon", "https://www.amazon.com/s?k=", "📦", "shopping"),
        Shortcut("!ebay", "eBay", "Search eBay", "https://www.ebay.com/sch/i.html?_nkw=", "🏷️", "shopping"),
        
        # News
        Shortcut("!news", "News", "Search News", "https://news.google.com/search?q=", "📰", "news"),
        Shortcut("!arxiv", "arXiv", "Search arXiv papers", "https://arxiv.org/search/?searchtype=all&query=", "📄", "academic"),
        Shortcut("!scholar", "Google Scholar", "Search Google Scholar", "https://scholar.google.com/scholar?q=", "🎓", "academic"),
        
        # Utilities
        Shortcut("!translate", "Google Translate", "Translate", "https://translate.google.com/?sl=auto&tl=en&text=", "🌐", "util"),
        Shortcut("!image", "Google Images", "Search Images", "https://www.google.com/search?tbm=isch&q=", "🖼️", "util"),
        Shortcut("!calc", "Calculator", "Open Calculator", "https://www.google.com/search?q=", "🔢", "util"),
        
        # Private alternatives
        Shortcut("!startpage", "Startpage", "Private Google", "https://www.startpage.com/do/search?query=", "🔒", "privacy"),
        Shortcut("!searx", "SearX", "Search SearX", "https://searx.org/search?q=", "🔍", "privacy"),
        Shortcut("!mojeek", "Mojeek", "Independent search", "https://www.mojeek.com/search?q=", "🔎", "privacy"),
    ]
    
    def __init__(self):
        self._shortcuts: Dict[str, Shortcut] = {}
        self._categories: Dict[str, List[Shortcut]] = {}
        self._load_builtin()
    
    def _load_builtin(self):
        """Load built-in shortcuts"""
        for shortcut in self.BUILTIN_SHORTCUTS:
            self._shortcuts[shortcut.trigger] = shortcut
            
            if shortcut.category not in self._categories:
                self._categories[shortcut.category] = []
            self._categories[shortcut.category].append(shortcut)
    
    def add_shortcut(self, trigger: str, name: str, query: str, description: str = "", icon: str = "🔍", category: str = "custom") -> bool:
        """Add a custom shortcut"""
        if trigger in self._shortcuts:
            return False
        
        shortcut = Shortcut(
            trigger=trigger,
            name=name,
            description=description or name,
            query=query,
            icon=icon,
            category=category
        )
        
        self._shortcuts[trigger] = shortcut
        
        if category not in self._categories:
            self._categories[category] = []
        self._categories[category].append(shortcut)
        
        return True
    
    def remove_shortcut(self, trigger: str) -> bool:
        """Remove a custom shortcut"""
        if trigger not in self._shortcuts:
            return False
        
        shortcut = self._shortcuts[trigger]
        del self._shortcuts[trigger]
        self._categories[shortcut.category].remove(shortcut)
        
        return True
    
    def get_shortcut(self, trigger: str) -> Optional[Shortcut]:
        """Get a shortcut by trigger"""
        return self._shortcuts.get(trigger)
    
    def expand(self, query: str) -> tuple[str, bool]:
        """
        Expand a shortcut in a query
        
        Returns:
            Tuple of (expanded_query, was_expanded)
        """
        query = query.strip()
        
        # Check if query starts with a shortcut
        for trigger, shortcut in self._shortcuts.items():
            if query.startswith(trigger):
                remainder = query[len(trigger):].strip()
                if remainder:
                    expanded = shortcut.query + remainder.replace(" ", "+")
                else:
                    expanded = shortcut.query
                return expanded, True
        
        return query, False
    
    def get_all_shortcuts(self) -> List[Shortcut]:
        """Get all shortcuts"""
        return list(self._shortcuts.values())
    
    def get_by_category(self, category: str) -> List[Shortcut]:
        """Get shortcuts by category"""
        return self._categories.get(category, [])
    
    def get_categories(self) -> List[str]:
        """Get all categories"""
        return list(self._categories.keys())
    
    def get_popular(self, limit: int = 10) -> List[Shortcut]:
        """Get popular shortcuts"""
        return self.BUILTIN_SHORTCUTS[:limit]


_shortcut_engine = ShortcutEngine()


def expand_shortcut(query: str) -> tuple:
    """Expand a shortcut in query"""
    return _shortcut_engine.expand(query)


def get_shortcut(trigger: str) -> Optional[Shortcut]:
    """Get a shortcut"""
    return _shortcut_engine.get_shortcut(trigger)


def get_all_shortcuts() -> List[Shortcut]:
    """Get all shortcuts"""
    return _shortcut_engine.get_all_shortcuts()


def get_shortcut_engine() -> ShortcutEngine:
    """Get the shortcut engine"""
    return _shortcut_engine
