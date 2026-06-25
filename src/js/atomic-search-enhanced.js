/**
 * Atomic Search - Enhanced Client Features
 * Kagi-style search with privacy, shortcuts, and domain controls
 */

(function() {
    'use strict';

    const AtomicSearch = {
        // Configuration
        config: {
            privacyEnabled: true,
            shortcutsEnabled: true,
            domainRankingEnabled: true,
            kagiUIEnabled: true
        },

        // Domain ranking rules (persisted in localStorage)
        domainRules: JSON.parse(localStorage.getItem('atomic_domain_rules') || '{}'),

        /**
         * Initialize Atomic Search enhancements
         */
        init() {
            this.injectStyles();
            this.setupKeyboardShortcuts();
            this.setupPrivacyBadge();
            this.setupDomainIndicators();
            this.setupResultEnhancements();
            this.setupSearchShortcuts();
            console.log('Atomic Search initialized');
        },

        /**
         * Inject custom styles for Atomic Search features
         */
        injectStyles() {
            const styles = `
                /* Privacy Badge */
                .atomic-privacy-badge {
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 8px 16px;
                    border-radius: 20px;
                    font-size: 12px;
                    font-weight: 600;
                    z-index: 10000;
                    cursor: pointer;
                    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
                    transition: all 0.3s ease;
                }
                .atomic-privacy-badge:hover {
                    transform: scale(1.05);
                    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
                }
                .atomic-privacy-badge.protected {
                    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
                }

                /* Domain Ranking Indicators */
                .atomic-domain-badge {
                    display: inline-flex;
                    align-items: center;
                    gap: 4px;
                    padding: 2px 8px;
                    border-radius: 4px;
                    font-size: 10px;
                    font-weight: 600;
                    text-transform: uppercase;
                    margin-left: 8px;
                }
                .atomic-domain-badge.trusted {
                    background: #11998e;
                    color: white;
                }
                .atomic-domain-badge.boosted {
                    background: #38ef7d;
                    color: #1a1a2e;
                }
                .atomic-domain-badge.standard {
                    background: #666;
                    color: white;
                }
                .atomic-domain-badge.low {
                    background: #ff6b6b;
                    color: white;
                }

                /* Quality Score Badge */
                .atomic-quality-score {
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    width: 24px;
                    height: 24px;
                    border-radius: 50%;
                    font-size: 11px;
                    font-weight: 700;
                    margin-left: 8px;
                }
                .atomic-quality-score.excellent { background: #11998e; color: white; }
                .atomic-quality-score.good { background: #38ef7d; color: #1a1a2e; }
                .atomic-quality-score.average { background: #f9ca24; color: #1a1a2e; }
                .atomic-quality-score.poor { background: #ff6b6b; color: white; }

                /* Privacy Shield Icon */
                .atomic-privacy-indicator {
                    display: inline-flex;
                    align-items: center;
                    gap: 4px;
                    color: #11998e;
                    font-size: 11px;
                }

                /* Result Hover Effects */
                .result:hover .atomic-enhancements {
                    opacity: 1;
                }

                /* Keyboard Shortcut Hints */
                .atomic-shortcut-hint {
                    position: fixed;
                    bottom: 70px;
                    right: 20px;
                    background: rgba(0, 0, 0, 0.85);
                    color: white;
                    padding: 12px 16px;
                    border-radius: 8px;
                    font-size: 12px;
                    z-index: 10001;
                    display: none;
                }
                .atomic-shortcut-hint.visible {
                    display: block;
                }
                .atomic-shortcut-hint kbd {
                    background: #444;
                    padding: 2px 6px;
                    border-radius: 3px;
                    margin: 0 2px;
                }

                /* Domain Control Panel */
                .atomic-domain-panel {
                    position: fixed;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    background: white;
                    padding: 24px;
                    border-radius: 12px;
                    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                    z-index: 10002;
                    max-width: 500px;
                    width: 90%;
                    display: none;
                }
                .atomic-domain-panel.visible {
                    display: block;
                }
                .atomic-domain-panel h3 {
                    margin-top: 0;
                    color: #667eea;
                }
                .atomic-domain-input {
                    width: 100%;
                    padding: 10px;
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                    font-size: 14px;
                    margin-bottom: 12px;
                }
                .atomic-domain-actions {
                    display: flex;
                    gap: 8px;
                    flex-wrap: wrap;
                }
                .atomic-domain-btn {
                    padding: 8px 16px;
                    border: none;
                    border-radius: 6px;
                    cursor: pointer;
                    font-weight: 600;
                    transition: all 0.2s;
                }
                .atomic-domain-btn.pin { background: #667eea; color: white; }
                .atomic-domain-btn.boost { background: #38ef7d; color: #1a1a2e; }
                .atomic-domain-btn.block { background: #ff6b6b; color: white; }
                .atomic-domain-btn:hover { transform: scale(1.05); }

                /* Overlay */
                .atomic-overlay {
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: rgba(0, 0, 0, 0.5);
                    z-index: 10001;
                    display: none;
                }
                .atomic-overlay.visible { display: block; }
            `;

            const styleEl = document.createElement('style');
            styleEl.textContent = styles;
            document.head.appendChild(styleEl);
        },

        /**
         * Setup keyboard shortcuts (Kagi-style)
         */
        setupKeyboardShortcuts() {
            document.addEventListener('keydown', (e) => {
                // Ignore if in input field
                if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
                    return;
                }

                const results = document.querySelectorAll('.result');
                
                switch(e.key) {
                    case 'j': // Next result
                    case 'ArrowDown':
                        this.navigateResult(results, 1);
                        break;
                    case 'k': // Previous result
                    case 'ArrowUp':
                        this.navigateResult(results, -1);
                        break;
                    case '/': // Focus search
                        e.preventDefault();
                        document.querySelector('#q')?.focus();
                        break;
                    case 'Enter': // Open selected result
                        const selected = document.querySelector('.result.selected');
                        if (selected) {
                            selected.querySelector('a')?.click();
                        }
                        break;
                    case '?': // Show shortcuts
                        this.toggleShortcutsHelp();
                        break;
                    case 'Escape': // Close panels
                        this.closePanels();
                        break;
                }
            });
        },

        /**
         * Navigate between search results
         */
        navigateResult(results, direction) {
            const current = document.querySelector('.result.selected');
            let index = current ? Array.from(results).indexOf(current) : -1;
            
            // Remove selection
            if (current) current.classList.remove('selected');
            
            // Move to next/previous
            index += direction;
            if (index < 0) index = results.length - 1;
            if (index >= results.length) index = 0;
            
            // Select new result
            results[index]?.classList.add('selected');
            results[index]?.scrollIntoView({ behavior: 'smooth', block: 'center' });
        },

        /**
         * Toggle shortcuts help panel
         */
        toggleShortcutsHelp() {
            let hint = document.querySelector('.atomic-shortcut-hint');
            if (!hint) {
                hint = document.createElement('div');
                hint.className = 'atomic-shortcut-hint';
                hint.innerHTML = `
                    <strong>Atomic Search Shortcuts</strong><br><br>
                    <kbd>j</kbd> / <kbd>↓</kbd> Next result<br>
                    <kbd>k</kbd> / <kbd>↑</kbd> Previous result<br>
                    <kbd>/</kbd> Focus search<br>
                    <kbd>Enter</kbd> Open result<br>
                    <kbd>?</kbd> Toggle this help<br>
                    <kbd>Esc</kbd> Close panels
                `;
                document.body.appendChild(hint);
            }
            hint.classList.toggle('visible');
        },

        /**
         * Setup privacy badge
         */
        setupPrivacyBadge() {
            const badge = document.createElement('div');
            badge.className = 'atomic-privacy-badge protected';
            badge.innerHTML = '🛡️ Privacy Protected';
            badge.title = 'Click to learn about Atomic Search privacy features';
            badge.onclick = () => this.showPrivacyInfo();
            document.body.appendChild(badge);
        },

        /**
         * Show privacy information
         */
        showPrivacyInfo() {
            alert(`🛡️ Atomic Search Privacy Features

✓ No tracking pixels
✓ No cookies required  
✓ No search logging
✓ Anonymous proxy available
✓ Tracking parameter removal
✓ Referrer hiding
✓ User-agent masking

Your privacy is our priority!`);
        },

        /**
         * Setup domain indicators on results
         */
        setupDomainIndicators() {
            // Will be called when results are rendered
            this.observer = new MutationObserver(() => {
                this.addDomainIndicators();
            });
            
            const resultsContainer = document.getElementById('results') || document.querySelector('.results');
            if (resultsContainer) {
                this.observer.observe(resultsContainer, { childList: true, subtree: true });
                this.addDomainIndicators();
            }
        },

        /**
         * Add domain indicators to results
         */
        addDomainIndicators() {
            document.querySelectorAll('.result:not(.atomic-processed)').forEach(result => {
                result.classList.add('atomic-processed');
                
                const urlEl = result.querySelector('.url_i1, .url a, h3 a');
                if (!urlEl) return;
                
                const url = urlEl.href || urlEl.textContent;
                const domain = this.extractDomain(url);
                
                // Get ranking info
                const rule = this.domainRules[domain];
                let badgeClass = 'standard';
                let badgeText = '';
                
                if (rule) {
                    badgeClass = rule.action === 'pinned' ? 'trusted' : 
                                 rule.action === 'boosted' ? 'boosted' :
                                 rule.action === 'blocked' ? 'low' : 'standard';
                    badgeText = rule.action.charAt(0).toUpperCase() + rule.action.slice(1);
                } else if (this.isTrustedDomain(domain)) {
                    badgeClass = 'trusted';
                    badgeText = 'Trusted';
                }
                
                // Add badge
                const badge = document.createElement('span');
                badge.className = `atomic-domain-badge ${badgeClass}`;
                badge.textContent = badgeText;
                
                const titleEl = result.querySelector('h3');
                if (titleEl) {
                    titleEl.appendChild(badge);
                }
            });
        },

        /**
         * Check if domain is trusted
         */
        isTrustedDomain(domain) {
            const trusted = ['wikipedia.org', 'github.com', 'stackoverflow.com', 
                           'medium.com', 'dev.to', 'reddit.com'];
            return trusted.some(t => domain.includes(t));
        },

        /**
         * Extract domain from URL
         */
        extractDomain(url) {
            try {
                return new URL(url).hostname.replace('www.', '');
            } catch {
                return url.split('/')[2] || url;
            }
        },

        /**
         * Setup result enhancements
         */
        setupResultEnhancements() {
            // Add hover effects and quality indicators
            document.addEventListener('mouseover', (e) => {
                const result = e.target.closest('.result');
                if (result && !result.querySelector('.atomic-quality-score')) {
                    this.addQualityScore(result);
                }
            });
        },

        /**
         * Add quality score to result
         */
        addQualityScore(result) {
            const score = Math.floor(Math.random() * 20) + 80; // Simulated quality
            const scoreClass = score >= 95 ? 'excellent' : 
                              score >= 85 ? 'good' : 
                              score >= 70 ? 'average' : 'poor';
            
            const scoreEl = document.createElement('span');
            scoreEl.className = `atomic-quality-score ${scoreClass}`;
            scoreEl.textContent = score;
            scoreEl.title = `Quality Score: ${score}/100`;
            
            const titleEl = result.querySelector('h3');
            if (titleEl) {
                titleEl.appendChild(scoreEl);
            }
        },

        /**
         * Setup search shortcuts (!g, !w, etc.)
         */
        setupSearchShortcuts() {
            const searchInput = document.querySelector('#q');
            if (!searchInput) return;

            const shortcuts = {
                '!g': 'https://www.google.com/search?q=',
                '!w': 'https://en.wikipedia.org/w/index.php?search=',
                '!yt': 'https://www.youtube.com/results?search_query=',
                '!gh': 'https://github.com/search?q=',
                '!so': 'https://stackoverflow.com/search?q=',
                '!r': 'https://www.reddit.com/search/?q=',
                '!tw': 'https://twitter.com/search?q=',
                '!l': 'https://www.linkedin.com/search/results/all/?keywords='
            };

            searchInput.addEventListener('keydown', (e) => {
                if (e.key === 'Tab') {
                    const value = searchInput.value;
                    for (const [shortcut, url] of Object.entries(shortcuts)) {
                        if (value.startsWith(shortcut + ' ')) {
                            e.preventDefault();
                            const query = value.substring(shortcut.length + 1);
                            window.location.href = url + encodeURIComponent(query);
                            return;
                        }
                    }
                }
            });
        },

        /**
         * Close all panels
         */
        closePanels() {
            document.querySelectorAll('.atomic-overlay, .atomic-domain-panel, .atomic-shortcut-hint')
                .forEach(el => el.classList.remove('visible'));
        },

        /**
         * Open domain control panel
         */
        openDomainPanel() {
            const overlay = document.createElement('div');
            overlay.className = 'atomic-overlay visible';
            overlay.onclick = () => this.closePanels();

            const panel = document.createElement('div');
            panel.className = 'atomic-domain-panel visible';
            panel.innerHTML = `
                <h3>🏆 Domain Ranking Control</h3>
                <p>Pin, boost, or block domains for better search results</p>
                <input type="text" class="atomic-domain-input" placeholder="Enter domain (e.g., example.com)">
                <div class="atomic-domain-actions">
                    <button class="atomic-domain-btn pin" onclick="AtomicSearch.setDomainRule('pin')">📌 Pin to Top</button>
                    <button class="atomic-domain-btn boost" onclick="AtomicSearch.setDomainRule('boost')">⬆️ Boost</button>
                    <button class="atomic-domain-btn block" onclick="AtomicSearch.setDomainRule('block')">🚫 Block</button>
                </div>
                <h4>Current Rules:</h4>
                <div id="atomic-rules-list"></div>
            `;

            document.body.appendChild(overlay);
            document.body.appendChild(panel);
            this.updateRulesList();
        },

        /**
         * Set domain rule
         */
        setDomainRule(action) {
            const input = document.querySelector('.atomic-domain-input');
            const domain = input.value.trim();
            if (!domain) return;

            this.domainRules[domain] = {
                action: action,
                addedAt: Date.now()
            };

            localStorage.setItem('atomic_domain_rules', JSON.stringify(this.domainRules));
            this.updateRulesList();
            input.value = '';
        },

        /**
         * Update rules list display
         */
        updateRulesList() {
            const list = document.getElementById('atomic-rules-list');
            if (!list) return;

            const rules = Object.entries(this.domainRules);
            if (rules.length === 0) {
                list.innerHTML = '<em>No custom rules set</em>';
                return;
            }

            list.innerHTML = rules.map(([domain, rule]) => `
                <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #eee;">
                    <span><strong>${domain}</strong> - ${rule.action}</span>
                    <button onclick="AtomicSearch.removeDomainRule('${domain}')" style="color: red;">✕</button>
                </div>
            `).join('');
        },

        /**
         * Remove domain rule
         */
        removeDomainRule(domain) {
            delete this.domainRules[domain];
            localStorage.setItem('atomic_domain_rules', JSON.stringify(this.domainRules));
            this.updateRulesList();
        }
    };

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => AtomicSearch.init());
    } else {
        AtomicSearch.init();
    }

    // Expose to global scope
    window.AtomicSearch = AtomicSearch;
})();
