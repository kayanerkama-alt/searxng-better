# Atomic Search 🔮

<div align="center">

![Atomic Search Logo](out/img/atomic.svg)

**The privacy-first, feature-rich metasearch engine with 40+ stunning themes**

*[Formerly SearXNG Better]* • *[Live Demo](https://priv.au)*

</div>

---

## ✨ Features

### 🔐 Privacy First
- **Zero Tracking**: No cookies, no logs, no fingerprinting
- **Decentralized Search**: Queries multiple engines simultaneously
- **Encrypted Connections**: HTTPS everywhere
- **No User Profiling**: Your searches stay private

### 🎨 40+ Beautiful Themes
Choose from an extensive collection of hand-crafted themes:
- **Dark Mode**: night, mocha, macchiato, dracula, nord, kagi
- **Light Mode**: latte, frappe, light, arctic, sky, mint
- **Special**: cyberpunk, matrix, hacker, terminal, cosmic, sakura, pixel
- **Nature**: forest, ocean, sunset
- **Elegant**: violet, lavender, cobalt, crimson, rose, amber
- And many more...

### 🏆 Kagi-Inspired Quality
- **Smart Ranking**: Quality-based result prioritization
- **Clean UI**: Distraction-free search experience
- **Instant Answers**: Direct answers without clicking
- **Related Searches**: Discover relevant queries

### ⚡ Performance
- **Fast Results**: Parallel engine queries
- **Lightweight**: Minimal resource usage
- **Docker Ready**: One-command deployment

---

## 🚀 Quick Start

### Docker (Recommended)
```bash
docker run -d --restart always -p 127.0.0.1:8080:8080 --name atomic-search ghcr.io/privau/searxng
```

Visit `http://127.0.0.1:8080` in your browser.

### Build from Source

1. Clone the repository:
```bash
git clone https://github.com/privau/searxng.git
cd searxng
```

2. Make changes to themes in `src/less`

3. Build static files:
```bash
./update.sh
```

4. Build Docker image:
```bash
docker build --pull -f ./Dockerfile -t atomic-search:latest .
```

5. Run:
```bash
docker run -it --rm -p 8080:8080 atomic-search:latest
```

Or use the development script:
```bash
./development.sh
```

---

## 🌍 Live Instances

🌐 **Global**: https://priv.au

🇺🇸 **Kansas City, US**: https://na.priv.au

🇸🇬 **Singapore**: https://as.priv.au

🇩🇪 **Frankfurt, DE**: https://eu.priv.au

🇦🇺 **Melbourne, AU**: https://au.priv.au

Use the [Looking Glass](https://lg.as44354.net/) to find the closest instance.

---

## ⚙️ Environment Variables

All variables are optional. If not set, defaults are used.

### General
| Variable | Description | Default |
|----------|-------------|---------|
| `IMAGE_PROXY` | Enable image proxy | `false` |
| `REDIS_URL` | Redis/Valkey URL | - |
| `LIMITER` | Enable bot limiting | - |
| `PROXY` | Comma-separated proxies | - |
| `BASE_URL` | Instance base URL | - |
| `NAME` | Instance name | `Atomic Search` |

### Privacy & Security
| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Session secret key | Auto-generated |
| `PUBLIC_INSTANCE` | Enable public instance features | - |

### Search Engines (Default Enabled)
| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_DEFAULT` | Google search | `true` |
| `BING_DEFAULT` | Bing search | `false` |
| `BRAVE_DEFAULT` | Brave search | `false` |
| `DUCKDUCKGO_DEFAULT` | DuckDuckGo | `false` |
| `WIKIPEDIA_DEFAULT` | Wikipedia | `false` |
| `WIKIDATA_DEFAULT` | Wikidata | `false` |

### Localization
| Variable | Description | Default |
|----------|-------------|---------|
| `SEARCH_DEFAULT_LANG` | Default language | `auto` |

### Branding & Contact
| Variable | Description |
|----------|-------------|
| `PRIVACYPOLICY` | Privacy policy URL |
| `CONTACT` | Contact URL |
| `ISSUE_URL` | Issue tracker URL |
| `FOOTER_MESSAGE` | Custom footer text |

### Donations
| Variable | Description |
|----------|-------------|
| `DONATE` | Enable donation page |
| `DONATION_URL` | Donation link (Ko-fi, etc.) |
| `MONERO_ADDRESS` | XMR address |

### API
| Variable | Description |
|----------|-------------|
| `AUTHORIZED_API` | Authorized API password |
| `OPENMETRICS` | OpenMetrics password |

---

## 🎨 Theme Development

Themes are defined in `src/less/themes/`. Each theme is a `.less` file that sets CSS variables.

### Creating a New Theme

1. Create `src/less/themes/mytheme.less`:

```less
.mynewtheme-themes() {
  --color-base-font: #ffffff;
  --color-base-background: #1a1a1a;
  --color-btn-background: #6366f1;
  // ... all other variables
}

:root.theme-mynewtheme {
  .mynewtheme-themes();
}
```

2. Add to `definitions.less`:
```less
@import "themes/mynewtheme.less";
```

3. Update `Dockerfile` theme lists

4. Rebuild:
```bash
./update.sh
```

---

## 🔒 Privacy Features

### Built-in Protections
- ✅ No tracking cookies
- ✅ No search logging  
- ✅ No referrer tracking
- ✅ HTTPS-only connections
- ✅ Optional image proxy
- ✅ Bot limiting (with Redis)

### Privacy Policy
Each instance can have a custom privacy policy. Visit `/privacy` on your instance.

---

## 📦 Tech Stack

- **Backend**: [SearXNG](https://github.com/searxng/searxng)
- **Styling**: LESS/CSS
- **Container**: Docker
- **Web Server**: Granian

---

## 🤝 Contributing

Contributions welcome! Please read the existing code style and submit PRs.

---

## 📄 License

AGPL-3.0-or-later

---

<div align="center">

**Made with ❤️ for privacy-conscious users**

</div>
