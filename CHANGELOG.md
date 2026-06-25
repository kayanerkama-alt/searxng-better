# Changelog

All notable changes to Atomic Search will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [2.0.0] - 2024-XX-XX

### 🎉 Major Changes

#### Rebranding
- Complete rebrand from SearXNG to **Atomic Search**
- New animated atomic logo with orbiting electrons
- Updated branding throughout codebase

#### New Themes (20 added, 40+ total)
- `cyberpunk` - Neon dreams with pink/cyan accents
- `ocean` - Deep sea serenity
- `forest` - Nature's calm greens
- `sunset` - Warm evening glow
- `matrix` - Classic green digital rain
- `sakura` - Cherry blossom pinks
- `pixel` - Retro gaming aesthetic
- `solarized` - Carefully crafted colors
- `hacker` - Classic green terminal
- `arctic` - Cool and clean blues
- `crimson` - Dark elegance with red
- `cobalt` - Deep blue luxury
- `amber` - Warm golden tones
- `violet` - Royal purple elegance
- `mint` - Fresh and clean green
- `lavender` - Soft purple tones
- `slate` - Professional dark
- `rose` - Elegant pink
- `sky` - Bright and airy
- `terminal` - Classic white on black
- `cosmic` - Space exploration purple

#### Deployment
- Added `railway.toml` for Railway deployment
- Added `render.yaml` for Render deployment
- Added optimized `Dockerfile.optimized`
- Added `docker-compose.yml` for local development
- Added `.dockerignore` for smaller images
- Added GitHub Actions CI/CD workflow

#### Performance
- Pre-compiled Python files for faster startup
- Optimized Docker multi-stage build
- Healthcheck endpoint at `/healthz`
- Non-root user for security

#### Privacy
- Enhanced privacy policy with detailed explanations
- Clear documentation of zero-logging policy
- Added sections on data portability and user control
- Search engine privacy explanations

### Infrastructure
- Railway deployment configuration
- Render deployment blueprint
- Docker Compose with Redis support
- GitHub Actions for CI/CD

## [1.0.0] - 2024-10-18

### Initial Release
- Base SearXNG build with custom themes
- 20 original themes (Catppuccin-inspired + Kagi)
- Privacy policy page
- Donation page
- Captcha support
- Authorized API
- Multiple search engine defaults
