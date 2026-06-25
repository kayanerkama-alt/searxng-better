// SPDX-License-Identifier: AGPL-3.0-or-later
/**
 * Atomic Search - Stats Widget
 * Show search statistics and privacy indicators
 */

(function() {
    'use strict';

    const StatsWidget = {
        storageKey: 'atomic_stats',
        
        init() {
            this.load();
            this.addWidget();
        },

        load() {
            try {
                const stored = localStorage.getItem(this.storageKey);
                if (stored) {
                    this.stats = JSON.parse(stored);
                } else {
                    this.stats = {
                        searches: 0,
                        blocked: 0,
                        timeSaved: 0, // in minutes
                        lastSearch: null
                    };
                }
            } catch (e) {
                this.stats = { searches: 0, blocked: 0, timeSaved: 0, lastSearch: null };
            }
        },

        save() {
            try {
                localStorage.setItem(this.storageKey, JSON.stringify(this.stats));
            } catch (e) {}
        },

        incrementSearch() {
            this.stats.searches++;
            this.stats.timeSaved += 0.5; // Estimate 30 seconds saved per search
            this.stats.lastSearch = new Date().toISOString();
            this.save();
            this.updateDisplay();
        },

        incrementBlocked() {
            this.stats.blocked++;
            this.save();
            this.updateDisplay();
        },

        addWidget() {
            const widget = document.createElement('div');
            widget.className = 'atomic-stats-widget';
            widget.innerHTML = `
                <div class="stats-header">
                    <span class="stats-icon">📊</span>
                    <span class="stats-title">Your Impact</span>
                </div>
                <div class="stats-grid">
                    <div class="stat-item">
                        <span class="stat-value" id="stat-searches">${this.stats.searches}</span>
                        <span class="stat-label">Searches</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-value" id="stat-blocked">${this.stats.blocked}</span>
                        <span class="stat-label">Trackers Blocked</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-value" id="stat-time">${this.stats.timeSaved}m</span>
                        <span class="stat-label">Time Saved</span>
                    </div>
                </div>
                <div class="stats-footer">
                    <button class="reset-btn">Reset Stats</button>
                </div>
            `;

            widget.querySelector('.reset-btn').onclick = () => this.reset();

            const container = document.querySelector('.footer, footer, .results_footer') || document.body;
            container.appendChild(widget);

            this.element = widget;
        },

        updateDisplay() {
            const searches = document.getElementById('stat-searches');
            const blocked = document.getElementById('stat-blocked');
            const time = document.getElementById('stat-time');
            
            if (searches) searches.textContent = this.stats.searches;
            if (blocked) blocked.textContent = this.stats.blocked;
            if (time) time.textContent = this.stats.timeSaved + 'm';
        },

        reset() {
            if (confirm('Reset all statistics?')) {
                this.stats = { searches: 0, blocked: 0, timeSaved: 0, lastSearch: null };
                this.save();
                this.updateDisplay();
            }
        }
    };

    // Privacy indicator
    const PrivacyIndicator = {
        init() {
            this.addIndicator();
            this.updateStatus();
        },

        addIndicator() {
            const indicator = document.createElement('div');
            indicator.className = 'atomic-privacy-indicator';
            indicator.innerHTML = `
                <span class="privacy-icon">🔒</span>
                <span class="privacy-text">Protected</span>
            `;
            
            document.querySelector('nav, header, .nav')?.appendChild(indicator);
            this.element = indicator;
        },

        updateStatus() {
            const icon = this.element?.querySelector('.privacy-icon');
            const text = this.element?.querySelector('.privacy-text');
            
            if (icon && text) {
                icon.textContent = '🔒';
                text.textContent = 'Protected';
                text.style.color = '#22c55e';
            }
        }
    };

    // Styles
    const style = document.createElement('style');
    style.textContent = `
        .atomic-stats-widget {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            color: #fff;
            border-radius: 16px;
            padding: 16px;
            min-width: 200px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            z-index: 9998;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }
        .stats-header {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 12px;
            padding-bottom: 12px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .stats-icon { font-size: 20px; }
        .stats-title { font-weight: 600; font-size: 14px; }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
            text-align: center;
        }
        .stat-item {
            display: flex;
            flex-direction: column;
        }
        .stat-value {
            font-size: 24px;
            font-weight: 700;
            color: #a78bfa;
        }
        .stat-label {
            font-size: 10px;
            color: #888;
            text-transform: uppercase;
        }
        .stats-footer {
            margin-top: 12px;
            padding-top: 12px;
            border-top: 1px solid rgba(255,255,255,0.1);
            text-align: center;
        }
        .reset-btn {
            background: none;
            border: 1px solid rgba(255,255,255,0.2);
            color: #888;
            padding: 6px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 11px;
        }
        .reset-btn:hover {
            background: rgba(255,255,255,0.1);
            color: #fff;
        }
        .atomic-privacy-indicator {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(34, 197, 94, 0.2);
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            margin-left: 12px;
        }
        .privacy-icon { font-size: 14px; }
        .privacy-text { color: #22c55e; font-weight: 500; }
    `;
    document.head.appendChild(style);

    // Init
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            StatsWidget.init();
            PrivacyIndicator.init();
        });
    } else {
        StatsWidget.init();
        PrivacyIndicator.init();
    }

    window.AtomicStats = StatsWidget;
    window.AtomicPrivacyIndicator = PrivacyIndicator;
})();
