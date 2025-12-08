FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for Camoufox/Firefox
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libxshmfence1 \
    libxtst6 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY main.py ./
COPY webhook_server.py ./

# Install Python dependencies with geoip support
RUN pip install --no-cache-dir \
    "camoufox[geoip]>=0.4.8" \
    camoufox-captcha>=0.1.2 \
    fastapi>=0.115.5 \
    requests>=2.32.3 \
    uvicorn>=0.32.1

# Pre-install Camoufox browser to avoid runtime issues
RUN python -c "import asyncio; from camoufox import AsyncCamoufox; asyncio.run(AsyncCamoufox(headless=True).start())"

# Expose port
EXPOSE 6090

# Run the webhook server
CMD ["python", "webhook_server.py"]
