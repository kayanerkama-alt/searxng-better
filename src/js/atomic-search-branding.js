/**
 * Atomic Search Branding and Enhancements
 * Adds Kagi-style UI features and privacy enhancements
 */

(function() {
    'use strict';
    
    // Branding Configuration
    const BRANDING = {
        name: 'Atomic Search',
        tagline: 'Privacy-First Metasearch',
        version: '2.0.0',
        features: {
            privacy: true,
            domainRanking: true,
            instantAnswers: true,
            darkMode: true
        }
    };
    
    // Initialize on DOM ready
    document.addEventListener('DOMContentLoaded', function() {
        initBranding();
        initPrivacyFeatures();
        initDomainRanking();
        initKeyboardShortcuts();
        initSearchEnhancements();
    });
    
    function initBranding() {
        // Update page title
        const title = document.querySelector('title');
        if (title && title.textContent.includes('SearXNG')) {
            title.textContent = title.textContent.replace('SearXNG', BRANDING.name);
        }
        
        // Update footer
        const poweredBy = document.querySelector('.powered_by');
        if (poweredBy) {
            poweredBy.innerHTML = poweredBy.innerHTML.replace(/SearXNG/g, BRANDING.name);
        }
        
        // Update about link
        document.querySelectorAll('a[href*="about"]').forEach(link => {
            if (link.textContent.includes('SearXNG')) {
                link.textContent = link.textContent.replace('SearXNG', BRANDING.name);
            }
        });
    }
    
    function initPrivacyFeatures() {
        // Add privacy badge
        const privacyBadge = document.createElement('div');
        privacyBadge.className = 'atomic-privacy-badge';
        privacyBadge.innerHTML = '<span class="icon">🔒</span> Private Search';
        privacyBadge.title = 'Your searches are not tracked or logged';
        document.body.appendChild(privacyBadge);
        
        // Style the badge
        addStyles('.atomic-privacy-badge', {
            position: 'fixed',
            bottom: '20px',
            right: '20px',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            padding: '8px 16px',
            borderRadius: '20px',
            fontSize: '12px',
            fontWeight: 'bold',
            boxShadow: '0 4px 15px rgba(0,0,0,0.2)',
            zIndex: '9999',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
        });
    }
    
    function initDomainRanking() {
        // Add ranking controls to results
        const results = document.querySelectorAll('.result');
        results.forEach(result => {
            const url = result.querySelector('a.url');
            if (url) {
                const domain = new URL(url.href).hostname;
                addDomainIndicator(result, domain);
            }
        });
    }
    
    function addDomainIndicator(result, domain) {
        const indicator = document.createElement('span');
        indicator.className = 'domain-indicator';
        indicator.textContent = getDomainIcon(domain) + ' ' + truncateDomain(domain);
        indicator.title = 'Domain: ' + domain;
        
        // Add styles
        addStyles('.domain-indicator', {
            fontSize: '11px',
            color: '#888',
            marginLeft: '8px',
            opacity: '0.8'
        });
        
        const title = result.querySelector('.result-title');
        if (title) {
            title.appendChild(indicator);
        }
    }
    
    function getDomainIcon(domain) {
        const icons = {
            'google.com': '🔍',
            'youtube.com': '📺',
            'github.com': '💻',
            'stackoverflow.com': '💬',
            'reddit.com': '📮',
            'twitter.com': '🐦',
            'amazon.com': '🛒',
            'wikipedia.org': '📚'
        };
        return icons[domain] || '🌐';
    }
    
    function truncateDomain(domain) {
        if (domain.length > 25) {
            return domain.substring(0, 22) + '...';
        }
        return domain;
    }
    
    function initKeyboardShortcuts() {
        document.addEventListener('keydown', function(e) {
            // Focus search on /
            if (e.key === '/' && !isInputFocused()) {
                e.preventDefault();
                const searchInput = document.querySelector('input[name="q"]');
                if (searchInput) searchInput.focus();
            }
            
            // Navigate results with j/k
            if (e.key === 'j' || e.key === 'k') {
                navigateResults(e.key);
            }
        });
    }
    
    function isInputFocused() {
        const active = document.activeElement;
        return active && (active.tagName === 'INPUT' || active.tagName === 'TEXTAREA');
    }
    
    function navigateResults(key) {
        const results = Array.from(document.querySelectorAll('.result'));
        const focused = document.querySelector('.result.focused');
        
        if (results.length === 0) return;
        
        let index = focused ? results.indexOf(focused) : -1;
        
        if (key === 'j') {
            index = Math.min(index + 1, results.length - 1);
        } else {
            index = Math.max(index - 1, 0);
        }
        
        if (focused) focused.classList.remove('focused');
        results[index].classList.add('focused');
        results[index].scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    
    function initSearchEnhancements() {
        const searchInput = document.querySelector('input[name="q"]');
        if (!searchInput) return;
        
        // Add search shortcuts hint
        const hint = document.createElement('div');
        hint.className = 'search-shortcuts-hint';
        hint.innerHTML = '<small>Try: !g python, !w react, !yt music</small>';
        
        searchInput.parentElement.appendChild(hint);
        
        addStyles('.search-shortcuts-hint', {
            fontSize: '11px',
            color: '#888',
            marginTop: '4px'
        });
    }
    
    function addStyles(selector, styles) {
        const style = document.createElement('style');
        let css = selector + ' { ';
        for (const [key, value] of Object.entries(styles)) {
            css += key + ': ' + value + '; ';
        }
        css += ' }';
        style.textContent = css;
        document.head.appendChild(style);
    }
    
    // Expose branding to window for other scripts
    window.AtomicSearch = BRANDING;
    
})();
