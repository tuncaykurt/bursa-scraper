# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python web scraping project that uses Camoufox (a stealth Firefox browser) with integrated captcha solving capabilities. The project specifically targets sahibinden.com and includes Cloudflare captcha bypass functionality.

## Dependencies & Package Management

- **Package Manager**: Uses `uv` for dependency management (evidenced by `uv.lock`)
- **Python Version**: Requires Python >=3.13 (specified in pyproject.toml)
- **Main Dependencies**:
  - `camoufox[geoip]>=0.4.11` - Stealth browser automation
  - `camoufox-captcha>=0.1.3` - Automated captcha solving

## Development Commands

```bash
# Install dependencies
uv sync

# Run the scraper (CLI)
python main.py

# Run webhook server
python webhook_server.py
# or
./run_webhook.sh

# Activate virtual environment (if needed)
source .venv/bin/activate
```

## Docker/Coolify Deployment

The project includes Docker support for easy deployment on platforms like Coolify:

```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build manually
docker build -t scraperpy .
docker run -p 6090:6090 scraperpy
```

### Environment Variables

- `PORT`: Server port (default: 6090)
- `DEFAULT_LIMIT`: Default number of listings to scrape (default: 5)
- `MAX_LIMIT`: Maximum allowed limit (default: 20)

### Coolify Setup

1. Import this repository in Coolify
2. Set the port to `6090`
3. Optionally configure environment variables
4. Deploy

## Code Architecture

The project follows a simple single-file structure:

- **main.py**: Contains the main scraping logic with async browser automation
- Browser configuration includes:
  - Headless mode disabled for debugging
  - GeoIP enabled for location masking
  - COOP disabled and scope access forced for compatibility
  - Humanization disabled for speed

## Key Implementation Details

- Uses async/await pattern with AsyncCamoufox context manager
- Implements Cloudflare interstitial captcha solving
- Includes 10-second timeout after captcha solving for page stabilization
- Browser instance configured with stealth and compatibility settings
