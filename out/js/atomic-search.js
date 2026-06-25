// SPDX-License-Identifier: AGPL-3.0-or-later

/**
 * Atomic Search UI Enhancements
 * Kagi-style features for SearXNG
 */

(function() {
    'use strict';

    // Prevent multiple initialization
    if (window.AtomicSearch) return;
    window.AtomicSearch = {};

    // ============================================
    // Domain Ranking Controls
    // ============================================

    const DomainRanking = {
        storageKey: 'atomic_domain_rules',
        rules: {},

        init() {
            this.loadRules();
            this.attachEventListeners();
        },

        loadRules() {
            try {
                const stored = localStorage.getItem(this.storageKey);
                if (stored) {
                    this.rules = JSON.parse(stored);
                }
            } catch (e) {
                console.warn('Failed to load domain rules:', e);
            }
        },

        saveRules() {
            try {
                localStorage.setItem(this.storageKey, JSON.stringify(this.rules));
            } catch (e) {
                console.warn('Failed to save domain rules:', e);
            }
        },

        getDomain(url) {
            try {
                const parsed = new URL(url);
                let domain = parsed.hostname;
                if (domain.startsWith('www.')) {
                    domain = domain.substring(4);
                }
                return domain;
            } catch (e) {
                return url;
            }
        },

        setRule(domain, action, weight = 1) {
            this.rules[domain] = {
                action: action,
                weight: weight,
                updated: Date.now()
            };
            this.saveRules();
            this.updateUI();
        },

        getRule(domain) {
            return this.rules[domain] || null;
        },

        removeRule(domain) {
            delete this.rules[domain];
            this.saveRules();
            this.updateUI();
        },

        attachEventListeners() {
            document.addEventListener('click', (e) => {
                const btn = e.target.closest('[data-domain-action]');
                if (btn) {
                    const url = btn.dataset.url;
                    const action = btn.dataset.domainAction;
                    const domain = this.getDomain(url);
                    
                    if (action === 'block') {
                        this.setRule(domain, 'blocked', 0);
                        this.hideResult(btn);
                    } else if (action === 'pin') {
                        this.setRule(domain, 'pinned', 2);
                        this.showNotification(`${domain} pinned to top`);
                    } else if (action === 'boost') {
                        this.setRule(domain, 'boosted', 1.5);
                        this.showNotification(`${domain} boosted`);
                    } else if (action === 'demote') {
                        this.setRule(domain, 'demoted', 0.5);
                        this.showNotification(`${domain} demoted`);
                    } else if (action === 'unblock') {
                        this.removeRule(domain);
                        this.showNotification(`${domain} unblocked`);
                    }
                }
            });
        },

        hideResult(btn) {
            const result = btn.closest('.result');
            if (result) {
                result.style.opacity = '0.5';
                result.style.pointerEvents = 'none';
                setTimeout(() => {
                    result.style.display = 'none';
                }, 300);
            }
        },

        showNotification(message) {
            const notification = document.createElement('div');
            notification.className = 'atomic-notification';
            notification.textContent = message;
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.classList.add('show');
            }, 10);
            
            setTimeout(() => {
                notification.classList.remove('show');
                setTimeout(() => notification.remove(), 300);
            }, 2000);
        },

        updateUI() {
            // Update all result badges based on rules
            document.querySelectorAll('.result').forEach(result => {
                const link = result.querySelector('a');
                if (!link) return;
                
                const domain = this.getDomain(link.href);
                const rule = this.getRule(domain);
                const badge = result.querySelector('.domain-badge');
                
                if (badge) {
                    badge.remove();
                }
                
                if (rule) {
                    const newBadge = document.createElement('span');
                    newBadge.className = `domain-badge ${rule.action}`;
                    
                    if (rule.action === 'pinned') {
                        newBadge.textContent = '📌 Pinned';
                    } else if (rule.action === 'boosted') {
                        newBadge.textContent = '⬆️ Boosted';
                    } else if (rule.action === 'blocked') {
                        newBadge.textContent = '🚫 Blocked';
                    } else if (rule.action === 'demoted') {
                        newBadge.textContent = '⬇️ Demoted';
                    }
                    
                    const title = result.querySelector('.result-header h2, h3');
                    if (title) {
                        title.appendChild(newBadge);
                    }
                }
            });
        },

        getStats() {
            const stats = {
                total: Object.keys(this.rules).length,
                pinned: 0,
                blocked: 0,
                boosted: 0,
                demoted: 0
            };
            
            Object.values(this.rules).forEach(rule => {
                if (rule.action in stats) {
                    stats[rule.action]++;
                }
            });
            
            return stats;
        }
    };

    // ============================================
    // Scam Detection UI
    // ============================================

    const ScamDetector = {
        trustedDomains: {
            'wikipedia.org': { score: 95, reason: 'Established encyclopedia' },
            'github.com': { score: 90, reason: 'Code repository' },
            'stackoverflow.com': { score: 85, reason: 'Developer Q&A' },
            'reddit.com': { score: 60, reason: 'User-generated content' },
        },
        
        suspiciousPatterns: [
            /\.(tk|ml|ga|cf|gq)$/i,  // Free domains
            /click|subscribe|free|gift/i,
            /password|login|signin|account/i,
        ],

        init() {
            this.analyzeResults();
        },

        analyzeResults() {
            document.querySelectorAll('.result').forEach(result => {
                const link = result.querySelector('a');
                if (!link) return;
                
                const url = link.href;
                const domain = DomainRanking.getDomain(url);
                
                // Check trust score
                let trustScore = 50; // Default
                let trustLabel = 'neutral';
                let trustClass = '';
                
                if (this.trustedDomains[domain]) {
                    trustScore = this.trustedDomains[domain].score;
                }
                
                // Check custom rules
                const rule = DomainRanking.getRule(domain);
                if (rule) {
                    if (rule.action === 'blocked') {
                        trustScore = 0;
                        trustLabel = 'blocked';
                        trustClass = 'danger';
                    } else if (rule.action === 'pinned') {
                        trustScore = 95;
                        trustLabel = 'trusted';
                        trustClass = 'success';
                    }
                }
                
                // Check suspicious patterns
                this.suspiciousPatterns.forEach(pattern => {
                    if (pattern.test(domain)) {
                        trustScore = Math.max(0, trustScore - 20);
                        trustLabel = 'warning';
                        trustClass = 'warning';
                    }
                });
                
                // Add badge
                this.addBadge(result, trustScore, trustLabel, trustClass);
            });
        },

        addBadge(result, score, label, className) {
            const badge = document.createElement('span');
            badge.className = `trust-badge ${className}`;
            
            if (score >= 80) {
                badge.innerHTML = '✓ Verified';
                badge.className = 'trust-badge success';
            } else if (score >= 50) {
                badge.innerHTML = '○ Unknown';
                badge.className = 'trust-badge neutral';
            } else if (score > 0) {
                badge.innerHTML = '⚠ Caution';
                badge.className = 'trust-badge warning';
            } else {
                badge.innerHTML = '✗ Blocked';
                badge.className = 'trust-badge danger';
            }
            
            const content = result.querySelector('.result-content, .content');
            if (content) {
                content.insertBefore(badge, content.firstChild);
            }
        }
    };

    // ============================================
    // Search Enhancements
    // ============================================

    const SearchEnhancer = {
        init() {
            this.addKeyboardShortcuts();
            this.enhanceSearchBox();
        },

        addKeyboardShortcuts() {
            document.addEventListener('keydown', (e) => {
                // Focus search box: /
                if (e.key === '/' && !e.ctrlKey && !e.metaKey) {
                    const searchInput = document.querySelector('input[name="q"], #q, .search-input');
                    if (searchInput && document.activeElement !== searchInput) {
                        e.preventDefault();
                        searchInput.focus();
                    }
                }
                
                // Clear search: Escape
                if (e.key === 'Escape') {
                    const searchInput = document.querySelector('input[name="q"], #q, .search-input');
                    if (searchInput && document.activeElement === searchInput) {
                        searchInput.blur();
                    }
                }
                
                // Navigate results: j/k
                if (document.activeElement.tagName !== 'INPUT') {
                    if (e.key === 'j' || e.key === 'ArrowDown') {
                        e.preventDefault();
                        this.navigateResult(1);
                    }
                    if (e.key === 'k' || e.key === 'ArrowUp') {
                        e.preventDefault();
                        this.navigateResult(-1);
                    }
                    if (e.key === 'Enter') {
                        this.openSelectedResult();
                    }
                }
            });
        },

        enhanceSearchBox() {
            const searchInput = document.querySelector('input[name="q"], #q, .search-input');
            if (!searchInput) return;
            
            // Add clear button
            const clearBtn = document.createElement('button');
            clearBtn.className = 'search-clear-btn';
            clearBtn.innerHTML = '×';
            clearBtn.title = 'Clear search';
            clearBtn.style.display = 'none';
            
            searchInput.parentNode.appendChild(clearBtn);
            
            searchInput.addEventListener('input', () => {
                clearBtn.style.display = searchInput.value ? 'block' : 'none';
            });
            
            clearBtn.addEventListener('click', () => {
                searchInput.value = '';
                clearBtn.style.display = 'none';
                searchInput.focus();
            });
        },

        navigateResult(direction) {
            const results = Array.from(document.querySelectorAll('.result a'));
            const focused = document.activeElement;
            const currentIndex = results.indexOf(focused);
            
            let nextIndex;
            if (currentIndex === -1) {
                nextIndex = direction > 0 ? 0 : results.length - 1;
            } else {
                nextIndex = Math.max(0, Math.min(results.length - 1, currentIndex + direction));
            }
            
            results[nextIndex]?.focus();
        },

        openSelectedResult() {
            const focused = document.activeElement;
            if (focused && focused.tagName === 'A') {
                focused.click();
            }
        }
    };

    // ============================================
    // Theme Switcher
    // ============================================

    const ThemeSwitcher = {
        themes: [
            'macchiato', 'latte', 'frappe', 'mocha', 'kagi',
            'nord', 'dracula', 'cyberpunk', 'matrix', 'ocean',
            'forest', 'sunset', 'sakura', 'arctic', 'cosmic'
        ],

        init() {
            this.addThemeStyles();
            this.addThemeSelector();
        },

        addThemeStyles() {
            // Add notification styles
            const style = document.createElement('style');
            style.textContent = `
                .atomic-notification {
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    background: linear-gradient(135deg, #6366f1, #8b5cf6);
                    color: white;
                    padding: 12px 24px;
                    border-radius: 8px;
                    font-size: 14px;
                    z-index: 10000;
                    transform: translateY(100px);
                    opacity: 0;
                    transition: all 0.3s ease;
                    box-shadow: 0 4px 20px rgba(99, 102, 241, 0.4);
                }
                .atomic-notification.show {
                    transform: translateY(0);
                    opacity: 1;
                }
                
                .domain-badge {
                    display: inline-block;
                    padding: 2px 8px;
                    border-radius: 4px;
                    font-size: 11px;
                    margin-left: 8px;
                    vertical-align: middle;
                }
                .domain-badge.pinned { background: rgba(34, 197, 94, 0.2); color: #16a34a; }
                .domain-badge.boosted { background: rgba(59, 130, 246, 0.2); color: #2563eb; }
                .domain-badge.demoted { background: rgba(245, 158, 11, 0.2); color: #d97706; }
                .domain-badge.blocked { background: rgba(220, 38, 38, 0.2); color: #dc2626; }
                
                .trust-badge {
                    display: inline-block;
                    padding: 2px 6px;
                    border-radius: 3px;
                    font-size: 10px;
                    margin-right: 6px;
                    font-weight: 600;
                }
                .trust-badge.success { background: rgba(34, 197, 94, 0.15); color: #16a34a; }
                .trust-badge.neutral { background: rgba(156, 163, 175, 0.15); color: #6b7280; }
                .trust-badge.warning { background: rgba(245, 158, 11, 0.15); color: #d97706; }
                .trust-badge.danger { background: rgba(220, 38, 38, 0.15); color: #dc2626; }
                
                .search-clear-btn {
                    position: absolute;
                    right: 8px;
                    top: 50%;
                    transform: translateY(-50%);
                    background: none;
                    border: none;
                    font-size: 20px;
                    color: #999;
                    cursor: pointer;
                    padding: 4px 8px;
                }
                .search-clear-btn:hover { color: #333; }
                
                .result:focus {
                    outline: 2px solid #6366f1;
                    outline-offset: 2px;
                }
            `;
            document.head.appendChild(style);
        },

        addThemeSelector() {
            // Find theme selector in preferences
            const themeSelect = document.querySelector('select[name="simple_style"], #simple_style');
            if (!themeSelect) return;
            
            // Add quick-switch buttons
            const container = document.createElement('div');
            container.className = 'theme-quick-switch';
            container.innerHTML = `
                <button class="theme-btn" data-theme="light" title="Light">☀️</button>
                <button class="theme-btn" data-theme="dark" title="Dark">🌙</button>
                <button class="theme-btn" data-theme="auto" title="Auto">🌓</button>
            `;
            
            themeSelect.parentNode.appendChild(container);
            
            container.querySelectorAll('.theme-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    const theme = btn.dataset.theme;
                    window.location.href = window.location.pathname + '?preferences=1&simple_style=' + theme;
                });
            });
        }
    };

    // ============================================
    // Quick Actions Toolbar
    // ============================================

    const QuickActions = {
        init() {
            this.addStyles();
            this.enhanceResults();
        },

        addStyles() {
            const style = document.createElement('style');
            style.textContent = `
                .result-actions {
                    display: flex;
                    gap: 4px;
                    opacity: 0;
                    transition: opacity 0.2s;
                    margin-left: auto;
                }
                .result:hover .result-actions {
                    opacity: 1;
                }
                .result-action-btn {
                    background: rgba(0,0,0,0.05);
                    border: none;
                    padding: 4px 8px;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 12px;
                    transition: all 0.2s;
                }
                .result-action-btn:hover {
                    background: rgba(99, 102, 241, 0.2);
                }
                .result-action-btn[data-action="pin"]:hover { color: #16a34a; }
                .result-action-btn[data-action="block"]:hover { color: #dc2626; }
                .result-action-btn[data-action="boost"]:hover { color: #2563eb; }
                .result-action-btn[data-action="demote"]:hover { color: #d97706; }
            `;
            document.head.appendChild(style);
        },

        enhanceResults() {
            document.querySelectorAll('.result').forEach(result => {
                const link = result.querySelector('a');
                if (!link) return;
                
                const actions = document.createElement('div');
                actions.className = 'result-actions';
                actions.innerHTML = `
                    <button class="result-action-btn" data-action="pin" data-url="${link.href}" title="Pin to top">📌</button>
                    <button class="result-action-btn" data-action="boost" data-url="${link.href}" title="Boost">⬆️</button>
                    <button class="result-action-btn" data-action="demote" data-url="${link.href}" title="Demote">⬇️</button>
                    <button class="result-action-btn" data-action="block" data-url="${link.href}" title="Block">🚫</button>
                `;
                
                const header = result.querySelector('.result-header, h2, h3');
                if (header) {
                    header.style.display = 'flex';
                    header.style.alignItems = 'center';
                    header.appendChild(actions);
                }
            });
        }
    };

    // ============================================
    // Initialization
    // ============================================

    function init() {
        DomainRanking.init();
        ScamDetector.init();
        SearchEnhancer.init();
        ThemeSwitcher.init();
        QuickActions.init();
        
        console.log('🔮 Atomic Search initialized');
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Export for external access
    window.AtomicSearch = {
        DomainRanking,
        ScamDetector,
        SearchEnhancer,
        ThemeSwitcher,
        QuickActions
    };

})();
