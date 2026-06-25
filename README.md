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
- **Dark Mode**: night, mocha, macchiato, dracula, nord, kagi, cyberpunk, matrix, hacker, cosmic, slate
- **Light Mode**: latte, frappe, light, arctic, sky, mint, sakura, lavender, rose, amber
- **Special**: terminal, solarized, pixel, ocean, forest, sunset, crimson, cobalt, violet
- And many more...

### ☁️ Cloud-Ready
- **Railway**: One-click deployment with `railway.toml`
- **Render**: Blueprint deployment with `render.yaml`
- **Docker**: Optimized multi-stage builds
- **Healthcheck**: Built-in `/healthz` endpoint

### ⚡ Performance Optimized
- **Pre-compiled Python**: Faster startup
- **Gzip/Brotli**: Compressed static assets
- **Multi-stage Build**: Smaller image size
- **Non-root User**: Enhanced security

---

## 🚀 Quick Start

### Docker (Recommended)
```bash
docker run -d --restart always -p 127.0.0.1:8080:8080 --name atomic-search ghcr.io/privau/searxng
```

### Docker Compose
```bash
# Without Redis (default)
docker-compose up -d

# With Redis for rate limiting
docker-compose --profile with-redis up -d
```

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
docker build -f ./Dockerfile -t atomic-search:latest .
```

5. Run:
```bash
docker run -p 8080:8080 atomic-search:latest
```

---

## ☁️ Cloud Deployment

### Railway (Recommended)

1. Fork this repository
2. Create a new project on [Railway](https://railway.app)
3. Connect your GitHub repo
4. Deploy automatically!

Or use the `railway.toml` for configuration:

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Deploy
railway up
```

**Environment Variables on Railway:**
- `NAME`: Your instance name
- `IMAGE_PROXY`: Set to `true` for image proxy
- `LIMITER`: Set to `true` to enable rate limiting
- `REDIS_URL`: Redis connection string (if using LIMITER)
- `SECRET_KEY`: Your secret key

### Render

1. Fork this repository
2. Create a new Web Service on [Render](https://render.com)
3. Connect your GitHub repo
4. Use `render.yaml` for automatic configuration

Or manual setup:
- **Build Command**: (empty)
- **Start Command**: `bash /usr/local/bin/run.sh`
- **Health Check Path**: `/healthz`

### Railway + Redis (Rate Limiting)

Enable bot protection with Redis:

```bash
# Using Docker Compose
REDIS_URL=redis://localhost:6379 docker-compose up -d

# Environment variable
REDIS_URL=redis://your-redis-url
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
| `GRANIAN_HOST` | Bind address | `0.0.0.0` |
| `GRANIAN_PORT` | Bind port | `8080` |

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

## 🏗️ Project Structure

```
atomic-search/
├── src/
│   ├── less/           # Theme LESS files
│   │   └── themes/     # Individual themes
│   ├── privacy-policy/
│   ├── captcha/
│   ├── auth/
│   └── search/
├── out/                # Compiled static files
├── Dockerfile          # Standard build
├── Dockerfile.optimized # Production optimized
├── docker-compose.yml  # Local development
├── railway.toml        # Railway deployment
├── render.yaml         # Render deployment
└── .env.example       # Environment template
```

---

## 📦 Tech Stack

- **Backend**: [SearXNG](https://github.com/searxng/searxng)
- **Styling**: LESS/CSS
- **Container**: Docker
- **Web Server**: Granian (Rust-based)

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
