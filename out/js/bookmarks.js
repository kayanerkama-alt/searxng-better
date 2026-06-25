// SPDX-License-Identifier: AGPL-3.0-or-later
/**
 * Atomic Search - Bookmarks & History
 * Save searches and results locally
 */

(function() {
    'use strict';

    const STORAGE_KEY = 'atomic_bookmarks';
    const MAX_BOOKMARKS = 100;

    const Bookmarks = {
        items: [],

        init() {
            this.load();
            this.setupUI();
        },

        load() {
            try {
                const stored = localStorage.getItem(STORAGE_KEY);
                this.items = stored ? JSON.parse(stored) : [];
            } catch (e) {
                this.items = [];
            }
        },

        save() {
            try {
                localStorage.setItem(STORAGE_KEY, JSON.stringify(this.items));
            } catch (e) {
                console.warn('Failed to save bookmarks');
            }
        },

        add(url, title, description) {
            // Check for duplicates
            if (this.items.find(b => b.url === url)) {
                return false;
            }

            // Limit size
            if (this.items.length >= MAX_BOOKMARKS) {
                this.items.shift();
            }

            this.items.unshift({
                id: Date.now(),
                url,
                title: title || url,
                description: description || '',
                created: new Date().toISOString()
            });

            this.save();
            this.updateUI();
            return true;
        },

        remove(id) {
            this.items = this.items.filter(b => b.id !== id);
            this.save();
            this.updateUI();
        },

        search(query) {
            if (!query) return this.items;
            const q = query.toLowerCase();
            return this.items.filter(b => 
                b.url.toLowerCase().includes(q) ||
                b.title.toLowerCase().includes(q)
            );
        },

        setupUI() {
            // Add bookmark buttons to results
            document.querySelectorAll('.result').forEach(result => {
                const link = result.querySelector('a');
                if (!link) return;

                const btn = document.createElement('button');
                btn.className = 'bookmark-btn';
                btn.innerHTML = '★';
                btn.title = 'Bookmark';
                btn.onclick = (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    if (this.add(link.href, result.querySelector('h2,h3')?.textContent)) {
                        btn.innerHTML = '★';
                        btn.classList.add('saved');
                        showToast('Bookmarked!');
                    }
                };

                const header = result.querySelector('.result-header, h2, h3');
                if (header) {
                    header.appendChild(btn);
                }
            });

            // Add bookmark panel toggle
            this.addPanelToggle();
        },

        addPanelToggle() {
            const toggle = document.createElement('button');
            toggle.className = 'bookmarks-toggle';
            toggle.innerHTML = '★ Bookmarks';
            toggle.onclick = () => this.togglePanel();

            const nav = document.querySelector('.nav') || document.querySelector('header');
            if (nav) {
                nav.appendChild(toggle);
            }
        },

        togglePanel() {
            let panel = document.querySelector('.bookmarks-panel');
            if (!panel) {
                panel = this.createPanel();
                document.body.appendChild(panel);
            }
            panel.classList.toggle('open');
        },

        createPanel() {
            const panel = document.createElement('div');
            panel.className = 'bookmarks-panel';
            panel.innerHTML = `
                <div class="bookmarks-header">
                    <h3>★ Bookmarks</h3>
                    <button class="close-btn">×</button>
                </div>
                <div class="bookmarks-list"></div>
                <div class="bookmarks-search">
                    <input type="text" placeholder="Search bookmarks..." />
                </div>
            `;

            panel.querySelector('.close-btn').onclick = () => panel.classList.remove('open');

            panel.querySelector('input').addEventListener('input', (e) => {
                const results = this.search(e.target.value);
                this.renderList(panel.querySelector('.bookmarks-list'), results);
            });

            this.renderList(panel.querySelector('.bookmarks-list'), this.items);
            return panel;
        },

        renderList(container, items) {
            if (items.length === 0) {
                container.innerHTML = '<p class="empty">No bookmarks yet</p>';
                return;
            }

            container.innerHTML = items.map(b => `
                <div class="bookmark-item" data-id="${b.id}">
                    <a href="${b.url}" target="_blank">${b.title}</a>
                    <button class="delete-btn" title="Remove">×</button>
                </div>
            `).join('');

            container.querySelectorAll('.delete-btn').forEach(btn => {
                btn.onclick = (e) => {
                    e.preventDefault();
                    const id = parseInt(btn.closest('.bookmark-item').dataset.id);
                    this.remove(id);
                };
            });
        },

        updateUI() {
            const panel = document.querySelector('.bookmarks-panel');
            if (panel) {
                this.renderList(panel.querySelector('.bookmarks-list'), this.items);
            }
        }
    };

    // Toast notifications
    function showToast(message) {
        const toast = document.createElement('div');
        toast.className = 'atomic-toast';
        toast.textContent = message;
        document.body.appendChild(toast);
        setTimeout(() => toast.classList.add('show'), 10);
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 2000);
    }

    // Initialize
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => Bookmarks.init());
    } else {
        Bookmarks.init();
    }

    // Add styles
    const style = document.createElement('style');
    style.textContent = `
        .bookmark-btn {
            background: none;
            border: none;
            font-size: 18px;
            cursor: pointer;
            opacity: 0.5;
            margin-left: 8px;
            color: #f59e0b;
        }
        .bookmark-btn:hover { opacity: 1; }
        .bookmark-btn.saved { color: #fbbf24; }
        .bookmarks-toggle {
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.2);
            color: #fff;
            padding: 8px 16px;
            border-radius: 20px;
            cursor: pointer;
            margin-left: 16px;
        }
        .bookmarks-toggle:hover { background: rgba(255,255,255,0.2); }
        .bookmarks-panel {
            position: fixed;
            top: 0;
            right: -350px;
            width: 350px;
            height: 100vh;
            background: #1a1a2e;
            color: #fff;
            z-index: 10000;
            transition: right 0.3s ease;
            box-shadow: -5px 0 20px rgba(0,0,0,0.5);
            display: flex;
            flex-direction: column;
        }
        .bookmarks-panel.open { right: 0; }
        .bookmarks-header {
            padding: 16px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .bookmarks-header .close-btn {
            background: none;
            border: none;
            color: #fff;
            font-size: 24px;
            cursor: pointer;
        }
        .bookmarks-list {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
        }
        .bookmark-item {
            padding: 12px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .bookmark-item a { color: #60a5fa; text-decoration: none; }
        .bookmark-item a:hover { text-decoration: underline; }
        .bookmark-item .delete-btn {
            background: none;
            border: none;
            color: #ef4444;
            cursor: pointer;
            font-size: 18px;
        }
        .bookmarks-search {
            padding: 16px;
            border-top: 1px solid rgba(255,255,255,0.1);
        }
        .bookmarks-search input {
            width: 100%;
            padding: 10px;
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 8px;
            background: rgba(255,255,255,0.1);
            color: #fff;
        }
        .atomic-toast {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            color: #fff;
            padding: 12px 24px;
            border-radius: 8px;
            z-index: 10001;
            transform: translateY(100px);
            opacity: 0;
            transition: all 0.3s ease;
        }
        .atomic-toast.show {
            transform: translateY(0);
            opacity: 1;
        }
    `;
    document.head.appendChild(style);

    window.AtomicBookmarks = Bookmarks;
})();
