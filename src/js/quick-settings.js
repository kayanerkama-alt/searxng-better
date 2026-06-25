// SPDX-License-Identifier: AGPL-3.0-or-later
/**
 * Atomic Search - Quick Settings Panel
 * Instant theme switching, privacy controls, shortcuts
 */

(function() {
    'use strict';

    const QuickSettings = {
        themes: [
            { id: 'auto', name: 'Auto', icon: '🌓' },
            { id: 'light', name: 'Light', icon: '☀️' },
            { id: 'dark', name: 'Dark', icon: '🌙' },
            { id: 'macchiato', name: 'Macchiato', icon: '🎨' },
            { id: 'mocha', name: 'Mocha', icon: '☕' },
            { id: 'nord', name: 'Nord', icon: '❄️' },
            { id: 'dracula', name: 'Dracula', icon: '🧛' },
            { id: 'cyberpunk', name: 'Cyberpunk', icon: '🤖' },
            { id: 'matrix', name: 'Matrix', icon: '💚' },
            { id: 'kagi', name: 'Kagi', icon: '🔑' },
        ],

        init() {
            this.addPanel();
            this.addKeyboardShortcuts();
        },

        addPanel() {
            const btn = document.createElement('button');
            btn.className = 'quick-settings-btn';
            btn.innerHTML = '⚙️';
            btn.title = 'Quick Settings';
            btn.onclick = () => this.togglePanel();

            document.querySelector('.nav, header, #top').appendChild(btn);
        },

        togglePanel() {
            let panel = document.querySelector('.quick-settings-panel');
            if (!panel) {
                panel = this.createPanel();
                document.body.appendChild(panel);
            }
            panel.classList.toggle('open');
        },

        createPanel() {
            const panel = document.createElement('div');
            panel.className = 'quick-settings-panel';

            const themeButtons = this.themes.map(t => `
                <button class="theme-option" data-theme="${t.id}" title="${t.name}">
                    <span class="icon">${t.icon}</span>
                    <span class="name">${t.name}</span>
                </button>
            `).join('');

            panel.innerHTML = `
                <div class="qs-header">
                    <h3>⚙️ Quick Settings</h3>
                    <button class="qs-close">×</button>
                </div>
                <div class="qs-section">
                    <h4>Theme</h4>
                    <div class="theme-grid">${themeButtons}</div>
                </div>
                <div class="qs-section">
                    <h4>Privacy</h4>
                    <label class="toggle-option">
                        <input type="checkbox" id="qs-privacy-proxy" />
                        <span>Privacy Proxy</span>
                    </label>
                    <label class="toggle-option">
                        <input type="checkbox" id="qs-block-trackers" checked />
                        <span>Block Trackers</span>
                    </label>
                    <label class="toggle-option">
                        <input type="checkbox" id="qs-safesearch" checked />
                        <span>SafeSearch</span>
                    </label>
                </div>
                <div class="qs-section">
                    <h4>Shortcuts</h4>
                    <div class="shortcuts-list">
                        <div class="shortcut"><code>!g</code> Google</div>
                        <div class="shortcut"><code>!w</code> Wikipedia</div>
                        <div class="shortcut"><code>!gh</code> GitHub</div>
                        <div class="shortcut"><code>!yt</code> YouTube</div>
                        <div class="shortcut"><code>!so</code> StackOverflow</div>
                        <div class="shortcut"><code>!r</code> Reddit</div>
                    </div>
                </div>
                <div class="qs-section">
                    <h4>Keyboard</h4>
                    <div class="shortcuts-list">
                        <div class="shortcut"><code>/</code> Focus search</div>
                        <div class="shortcut"><code>j/k</code> Navigate results</div>
                        <div class="shortcut"><code>Enter</code> Open result</div>
                        <div class="shortcut"><code>Esc</code> Clear/blur</div>
                    </div>
                </div>
                <div class="qs-footer">
                    <a href="/preferences">Full Preferences →</a>
                </div>
            `;

            // Close button
            panel.querySelector('.qs-close').onclick = () => panel.classList.remove('open');

            // Theme switching
            panel.querySelectorAll('.theme-option').forEach(btn => {
                btn.onclick = () => {
                    const theme = btn.dataset.theme;
                    this.setTheme(theme);
                    panel.querySelectorAll('.theme-option').forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                };
            });

            // Privacy toggles
            panel.querySelectorAll('.toggle-option input').forEach(input => {
                input.addEventListener('change', () => {
                    const setting = input.id.replace('qs-', '');
                    localStorage.setItem('atomic_' + setting, input.checked);
                    this.applySettings();
                });
            });

            return panel;
        },

        setTheme(theme) {
            // Set in URL for SearXNG
            const url = new URL(window.location);
            url.searchParams.set('simple_style', theme);
            window.location.href = url.toString();
        },

        applySettings() {
            // Apply privacy settings
            const proxy = localStorage.getItem('atomic_privacy_proxy') === 'true';
            const blockTrackers = localStorage.getItem('atomic_block_trackers') !== 'false';

            console.log('Settings applied:', { proxy, blockTrackers });
        },

        addKeyboardShortcuts() {
            document.addEventListener('keydown', (e) => {
                // Ctrl/Cmd + , = settings
                if ((e.ctrlKey || e.metaKey) && e.key === ',') {
                    e.preventDefault();
                    this.togglePanel();
                }
            });
        }
    };

    // Styles
    const style = document.createElement('style');
    style.textContent = `
        .quick-settings-btn {
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.2);
            color: #fff;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            cursor: pointer;
            font-size: 18px;
            margin-left: 8px;
        }
        .quick-settings-btn:hover { background: rgba(255,255,255,0.2); }
        .quick-settings-panel {
            position: fixed;
            top: 0;
            left: -400px;
            width: 380px;
            height: 100vh;
            background: #1a1a2e;
            color: #fff;
            z-index: 10000;
            transition: left 0.3s ease;
            box-shadow: 5px 0 20px rgba(0,0,0,0.5);
            overflow-y: auto;
        }
        .quick-settings-panel.open { left: 0; }
        .qs-header {
            padding: 20px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            background: #1a1a2e;
        }
        .qs-header h3 { margin: 0; }
        .qs-close {
            background: none;
            border: none;
            color: #fff;
            font-size: 28px;
            cursor: pointer;
        }
        .qs-section {
            padding: 20px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .qs-section h4 {
            margin: 0 0 16px 0;
            color: #a78bfa;
            font-size: 14px;
            text-transform: uppercase;
        }
        .theme-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 8px;
        }
        .theme-option {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 10px;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 8px;
            color: #fff;
            cursor: pointer;
            transition: all 0.2s;
        }
        .theme-option:hover { background: rgba(255,255,255,0.1); }
        .theme-option.active { border-color: #6366f1; background: rgba(99,102,241,0.2); }
        .theme-option .icon { font-size: 20px; }
        .theme-option .name { font-size: 13px; }
        .toggle-option {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 0;
            cursor: pointer;
        }
        .toggle-option input[type="checkbox"] {
            width: 20px;
            height: 20px;
            accent-color: #6366f1;
        }
        .shortcuts-list {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        .shortcut {
            display: flex;
            justify-content: space-between;
            padding: 8px 12px;
            background: rgba(255,255,255,0.05);
            border-radius: 6px;
        }
        .shortcut code {
            background: rgba(99,102,241,0.3);
            padding: 2px 8px;
            border-radius: 4px;
            font-family: monospace;
        }
        .qs-footer {
            padding: 20px;
            text-align: center;
        }
        .qs-footer a {
            color: #6366f1;
            text-decoration: none;
        }
        .qs-footer a:hover { text-decoration: underline; }
    `;
    document.head.appendChild(style);

    // Init
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => QuickSettings.init());
    } else {
        QuickSettings.init();
    }

    window.AtomicQuickSettings = QuickSettings;
})();
