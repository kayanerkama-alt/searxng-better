// SPDX-License-Identifier: AGPL-3.0-or-later
/**
 * Atomic Search - Theme Toggle Component
 * Smooth dark/light mode switching
 */

(function() {
    'use strict';

    const ThemeToggle = {
        themes: [
            { id: 'auto', name: 'Auto', icon: '🌓' },
            { id: 'light', name: 'Light', icon: '☀️' },
            { id: 'dark', name: 'Dark', icon: '🌙' },
            { id: 'macchiato', name: 'Macchiato', icon: '🎨' },
            { id: 'mocha', name: 'Mocha', icon: '☕' },
            { id: 'latte', name: 'Latte', icon: '🥛' },
            { id: 'frappe', name: 'Frappe', icon: '🥤' },
            { id: 'nord', name: 'Nord', icon: '❄️' },
            { id: 'dracula', name: 'Dracula', icon: '🧛' },
            { id: 'cyberpunk', name: 'Cyberpunk', icon: '🤖' },
            { id: 'matrix', name: 'Matrix', icon: '💚' },
            { id: 'neon', name: 'Neon', icon: '💜' },
            { id: 'galaxy', name: 'Galaxy', icon: '🌌' },
            { id: 'sunset', name: 'Sunset', icon: '🌅' },
            { id: 'ocean', name: 'Ocean', icon: '🌊' },
        ],

        init() {
            this.createToggle();
            this.addStyles();
        },

        createToggle() {
            const toggle = document.createElement('div');
            toggle.className = 'atomic-theme-toggle';
            toggle.innerHTML = `
                <button class="theme-btn" title="Change theme">
                    <span class="icon">🎨</span>
                </button>
                <div class="theme-dropdown">
                    <div class="dropdown-header">Theme</div>
                    <div class="theme-list"></div>
                </div>
            `;

            const themeList = toggle.querySelector('.theme-list');
            this.themes.forEach(theme => {
                const btn = document.createElement('button');
                btn.className = 'theme-item';
                btn.dataset.theme = theme.id;
                btn.innerHTML = `<span class="icon">${theme.icon}</span><span class="name">${theme.name}</span>`;
                btn.onclick = () => this.setTheme(theme.id);
                themeList.appendChild(btn);
            });

            toggle.querySelector('.theme-btn').onclick = (e) => {
                e.stopPropagation();
                toggle.classList.toggle('open');
            };

            document.addEventListener('click', () => toggle.classList.remove('open'));

            const nav = document.querySelector('nav, .nav, header');
            if (nav) {
                nav.appendChild(toggle);
            } else {
                document.body.appendChild(toggle);
            }

            this.element = toggle;
        },

        setTheme(themeId) {
            // Save preference
            localStorage.setItem('atomic_theme', themeId);

            // Update URL for SearXNG
            const url = new URL(window.location);
            url.searchParams.set('simple_style', themeId);
            window.location.href = url.toString();
        },

        addStyles() {
            const style = document.createElement('style');
            style.textContent = `
                .atomic-theme-toggle {
                    position: relative;
                    display: inline-block;
                }
                .theme-btn {
                    background: rgba(255,255,255,0.1);
                    border: 1px solid rgba(255,255,255,0.2);
                    color: #fff;
                    width: 40px;
                    height: 40px;
                    border-radius: 50%;
                    cursor: pointer;
                    font-size: 18px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: all 0.2s;
                }
                .theme-btn:hover {
                    background: rgba(255,255,255,0.2);
                    transform: scale(1.1);
                }
                .theme-dropdown {
                    position: absolute;
                    top: 50px;
                    right: 0;
                    background: #1a1a2e;
                    border: 1px solid rgba(255,255,255,0.1);
                    border-radius: 12px;
                    padding: 12px;
                    min-width: 200px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.5);
                    opacity: 0;
                    visibility: hidden;
                    transform: translateY(-10px);
                    transition: all 0.2s;
                    z-index: 10000;
                }
                .atomic-theme-toggle.open .theme-dropdown {
                    opacity: 1;
                    visibility: visible;
                    transform: translateY(0);
                }
                .dropdown-header {
                    color: #888;
                    font-size: 12px;
                    text-transform: uppercase;
                    padding: 0 8px 12px;
                    border-bottom: 1px solid rgba(255,255,255,0.1);
                    margin-bottom: 8px;
                }
                .theme-list {
                    max-height: 300px;
                    overflow-y: auto;
                }
                .theme-item {
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    width: 100%;
                    padding: 10px 12px;
                    background: none;
                    border: none;
                    color: #fff;
                    cursor: pointer;
                    border-radius: 8px;
                    transition: background 0.2s;
                    text-align: left;
                }
                .theme-item:hover {
                    background: rgba(255,255,255,0.1);
                }
                .theme-item .icon {
                    font-size: 18px;
                }
                .theme-item .name {
                    font-size: 14px;
                }
            `;
            document.head.appendChild(style);
        }
    };

    // Init
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => ThemeToggle.init());
    } else {
        ThemeToggle.init();
    }

    window.AtomicThemeToggle = ThemeToggle;
})();
