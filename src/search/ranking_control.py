"""Website Ranking Control - Choose what sites rank higher"""

# User's preferred domains (can be set via preferences)
USER_PREFERRED_DOMAINS = []

# Domain boost/penalty settings
DOMAIN_SETTINGS = {}

def boost_domain(domain, boost=50):
    """Boost a domain's ranking"""
    DOMAIN_SETTINGS[domain] = {'boost': boost}

def block_domain(domain, block=True):
    """Block a domain completely"""
    DOMAIN_SETTINGS[domain] = {'blocked': block}

def get_domain_score(domain):
    """Get score modifier for domain"""
    if domain in DOMAIN_SETTINGS:
        settings = DOMAIN_SETTINGS[domain]
        if settings.get('blocked'):
            return -1000
        return settings.get('boost', 0)
    return 0

def should_block_domain(domain):
    """Check if domain should be blocked"""
    return get_domain_score(domain) < -100

# Common domains users might want to boost
POPULAR_DOMAINS = {
    'wikipedia.org': 'Knowledge',
    'github.com': 'Code',
    'stackoverflow.com': 'Q&A',
    'reddit.com': 'Discussion',
    'youtube.com': 'Video',
    'medium.com': 'Articles',
    'dev.to': 'Dev Blog',
    'news.ycombinator.com': 'Tech News',
}

def get_recommended_boosts():
    """Get recommended domain boosts for UI"""
    return POPULAR_DOMAINS
