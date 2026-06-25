// SPDX-License-Identifier: AGPL-3.0-or-later
/**
 * Atomic Search - Search Tips & Tricks
 * Help users get better results
 */

(function() {
    'use strict';

    const SearchTips = {
        tips: [
            { category: 'Shortcuts', items: [
                { trigger: '!g ', example: '!g python tutorial', desc: 'Search Google directly' },
                { trigger: '!w ', example: '!w javascript', desc: 'Search Wikipedia' },
                { trigger: '!gh ', example: '!gh react hooks', desc: 'Search GitHub' },
                { trigger: '!yt ', example: '!yt coding tutorial', desc: 'Search YouTube' },
                { trigger: '!so ', example: '!so async await', desc: 'Search StackOverflow' },
                { trigger: '!r ', example: '!r webdev', desc: 'Search Reddit' },
            ]},
            { category: 'Operators', items: [
                { trigger: '"exact phrase"', example: '"artificial intelligence"', desc: 'Exact match' },
                { trigger: 'site:', example: 'site:github.com python', desc: 'Specific website' },
                { trigger: '-exclude', example: 'python -java', desc: 'Exclude term' },
                { trigger: 'OR', example: 'python OR ruby', desc: 'Either term' },
                { trigger: 'filetype:', example: 'filetype:pdf python', desc: 'File type' },
            ]},
            { category: 'Instant Answers', items: [
                { trigger: 'calc', example: 'calc 2+2*3', desc: 'Calculator' },
                { trigger: '100 USD to EUR', example: '100 USD to EUR', desc: 'Currency conversion' },
                { trigger: 'weather', example: 'weather in London', desc: 'Weather info' },
            ]},
            { category: 'Tips', items: [
                { trigger: 'Keyboard /', example: 'Press /', desc: 'Focus search box' },
                { trigger: 'j/k', example: 'Press j or k', desc: 'Navigate results' },
                { trigger: 'Enter', example: 'Press Enter', desc: 'Open result' },
                { trigger: 'Esc', example: 'Press Esc', desc: 'Clear search' },
            ]},
        ],

        init() {
            this.addTipsButton();
        },

        addTipsButton() {
            const btn = document.createElement('button');
            btn.className = 'tips-btn';
            btn.innerHTML = '💡 Tips';
            btn.onclick = () => this.showTips();
            document.body.appendChild(btn);
        },

        showTips() {
            // Remove existing modal
            const existing = document.querySelector('.tips-modal');
            if (existing) {
                existing.remove();
                return;
            }

            const modal = document.createElement('div');
            modal.className = 'tips-modal';

            let html = `
                <div class="tips-content">
                    <div class="tips-header">
                        <h2>💡 Search Tips</h2>
                        <button class="close-btn">×</button>
                    </div>
                    <div class="tips-body">
            `;

            this.tips.forEach(section => {
                html += `<div class="tips-section">
                    <h3>${section.category}</h3>
                    <div class="tips-grid">`;
                
                section.items.forEach(tip => {
                    html += `
                        <div class="tip-item">
                            <code>${tip.trigger}</code>
                            <p>${tip.desc}</p>
                        </div>
                    `;
                });

                html += `</div></div>`;
            });

            html += `</div></div>`;
            modal.innerHTML = html;

            modal.querySelector('.close-btn').onclick = () => modal.remove();
            modal.onclick = (e) => {
                if (e.target === modal) modal.remove();
            };

            document.body.appendChild(modal);

            // Add styles
            if (!document.querySelector('#tips-styles')) {
                const style = document.createElement('style');
                style.id = 'tips-styles';
                style.textContent = `
                    .tips-btn {
                        position: fixed;
                        bottom: 20px;
                        left: 20px;
                        background: linear-gradient(135deg, #6366f1, #8b5cf6);
                        color: #fff;
                        border: none;
                        padding: 12px 20px;
                        border-radius: 25px;
                        cursor: pointer;
                        font-size: 14px;
                        box-shadow: 0 4px 20px rgba(99,102,241,0.4);
                        z-index: 9998;
                        transition: transform 0.2s;
                    }
                    .tips-btn:hover { transform: scale(1.05); }
                    .tips-modal {
                        position: fixed;
                        top: 0;
                        left: 0;
                        width: 100%;
                        height: 100%;
                        background: rgba(0,0,0,0.7);
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        z-index: 9999;
                    }
                    .tips-content {
                        background: #1a1a2e;
                        border-radius: 16px;
                        max-width: 700px;
                        max-height: 80vh;
                        overflow-y: auto;
                        color: #fff;
                    }
                    .tips-header {
                        padding: 20px;
                        border-bottom: 1px solid rgba(255,255,255,0.1);
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        position: sticky;
                        top: 0;
                        background: #1a1a2e;
                    }
                    .tips-header h2 { margin: 0; }
                    .tips-header .close-btn {
                        background: none;
                        border: none;
                        color: #fff;
                        font-size: 28px;
                        cursor: pointer;
                    }
                    .tips-body { padding: 20px; }
                    .tips-section { margin-bottom: 24px; }
                    .tips-section h3 {
                        color: #a78bfa;
                        margin: 0 0 12px;
                        font-size: 14px;
                        text-transform: uppercase;
                    }
                    .tips-grid {
                        display: grid;
                        grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
                        gap: 12px;
                    }
                    .tip-item {
                        background: rgba(255,255,255,0.05);
                        padding: 12px;
                        border-radius: 8px;
                    }
                    .tip-item code {
                        display: block;
                        background: rgba(99,102,241,0.3);
                        padding: 4px 8px;
                        border-radius: 4px;
                        margin-bottom: 8px;
                        font-family: monospace;
                        color: #a78bfa;
                    }
                    .tip-item p {
                        margin: 0;
                        font-size: 12px;
                        color: #aaa;
                    }
                `;
                document.head.appendChild(style);
            }
        }
    };

    // Init
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => SearchTips.init());
    } else {
        SearchTips.init();
    }

    window.AtomicSearchTips = SearchTips;
})();
