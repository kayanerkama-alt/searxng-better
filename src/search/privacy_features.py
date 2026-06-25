"""Privacy enhancements for Atomic Search"""

def get_privacy_score(url):
    """Calculate privacy score for a URL (Kagi-style)"""
    suspicious_patterns = [
        'tracking', 'analytics', 'ads', 'doubleclick',
        'facebook.com/plugins', 'twitter.com/widgets',
        'googlesyndication', 'googleadservices'
    ]
    score = 100
    url_lower = url.lower()
    for pattern in suspicious_patterns:
        if pattern in url_lower:
            score -= 20
    return max(0, score)

def get_trust_badge(score):
    """Get trust badge based on score"""
    if score >= 80:
        return "🟢 Trusted"
    elif score >= 60:
        return "🟡 Moderate"
    elif score >= 40:
        return "🟠 Low Risk"
    else:
        return "🔴 High Tracking"

def is_safe_url(url):
    """Check if URL is safe"""
    dangerous = ['phishing', 'malware', 'spam']
    return not any(d in url.lower() for d in dangerous)

# Ranking weights (Kagi-style)
RANKING_WEIGHTS = {
    'quality': 0.4,      # Content quality
    'privacy': 0.3,      # Privacy score
    'speed': 0.2,        # Page speed
    'relevance': 0.1     # Search relevance
}

def calculate_result_score(result, query):
    """Calculate enhanced score for search result"""
    base_score = result.get('score', 50)
    
    # Privacy boost/penalty
    url = result.get('url', '')
    privacy_score = get_privacy_score(url)
    privacy_factor = privacy_score / 100
    
    # Quality factor (placeholder)
    quality_factor = 0.8
    
    # Final weighted score
    final_score = (
        base_score * RANKING_WEIGHTS['quality'] * quality_factor +
        privacy_score * RANKING_WEIGHTS['privacy'] +
        80 * RANKING_WEIGHTS['speed'] +  # Assume good speed
        base_score * RANKING_WEIGHTS['relevance']
    )
    
    return {
        'score': round(final_score, 1),
        'privacy_score': privacy_score,
        'trust_badge': get_trust_badge(privacy_score),
        'is_safe': is_safe_url(url)
    }
