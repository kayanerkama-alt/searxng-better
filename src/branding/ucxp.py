# SPDX-License-Identifier: AGPL-3.0-or-later

"""
UCXP Branding Module for Atomic Search
Provides branding configuration and customization
"""

BRAND_CONFIG = {
    "name": "Atomic Search",
    "project": "UCXP",
    "tagline": "Privacy-First Metasearch Engine",
    "description": """
    Atomic Search is a privacy-first, open-source metasearch engine 
    based on SearXNG, rebranded and enhanced by the UCXP project.
    
    Features:
    - Zero tracking and logging
    - 40+ beautiful themes
    - Kagi-style UI elements
    - Built-in scam detection
    - Weather search
    - Anonymous proxy routing
    """,
    
    "features": {
        "privacy": [
            "Zero logging of search queries",
            "No IP address storage",
            "No cookies for tracking",
            "End-to-end encryption",
            "Anonymous proxy routing",
        ],
        "ui": [
            "40+ beautiful themes",
            "Kagi-style ranking badges",
            "Quality score indicators",
            "Trust badges for sources",
            "Quick actions toolbar",
        ],
        "security": [
            "Built-in scam detection",
            "URL safety checking",
            "Phishing protection",
            "HTTPS enforcement",
            "Bot limiting support",
        ],
    },
    
    "supported_themes": [
        "night", "mocha", "macchiato", "dracula", "nord", 
        "kagi", "cyberpunk", "matrix", "hacker", "cosmic", 
        "slate", "terminal", "crimson", "cobalt", "violet",
        "latte", "frappe", "light", "arctic", "sky",
        "mint", "lavender", "rose", "amber", "sakura",
        "ocean", "forest", "sunset", "pixel", "solarized",
        "brave", "moa", "gruvbox", "gruvboxmat", "everforest",
        "nord", "matcha", "evergarden",
    ],
    
    "default_theme": "macchiato",
    
    "links": {
        "website": "https://priv.au",
        "github": "https://github.com/privau/searxng",
        "privacy": "/privacy",
        "donate": "/donate",
    },
    
    "contact": {
        "email": "contact@priv.au",
        "github": "https://github.com/privau/searxng/issues",
    },
    
    "servers": [
        {"name": "Global", "url": "https://priv.au", "location": "Frankfurt, DE"},
        {"name": "North America", "url": "https://na.priv.au", "location": "Kansas City, US"},
        {"name": "Asia Pacific", "url": "https://as.priv.au", "location": "Singapore"},
        {"name": "Europe", "url": "https://eu.priv.au", "location": "Frankfurt, DE"},
        {"name": "Australia", "url": "https://au.priv.au", "location": "Melbourne, AU"},
    ],
}


def get_brand_info() -> dict:
    """Get brand configuration"""
    return BRAND_CONFIG


def get_featured_themes() -> list:
    """Get featured/popular themes"""
    return [
        {"id": "macchiato", "name": "Macchiato", "type": "dark", "featured": True},
        {"id": "kagi", "name": "Kagi", "type": "dark", "featured": True},
        {"id": "cyberpunk", "name": "Cyberpunk", "type": "dark", "featured": True},
        {"id": "ocean", "name": "Ocean", "type": "light", "featured": True},
        {"id": "nord", "name": "Nord", "type": "dark", "featured": False},
        {"id": "sakura", "name": "Sakura", "type": "light", "featured": False},
    ]


def format_welcome_message() -> str:
    """Format welcome message with brand info"""
    return f"""
🔮 {BRAND_CONFIG['name']}
{BRAND_CONFIG['tagline']}

Powered by SearXNG | Enhanced by UCXP Project
    """.strip()
