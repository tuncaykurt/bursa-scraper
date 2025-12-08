FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY main.py ./
COPY webhook_server.py ./

# Install Python dependencies directly with pip
RUN pip install --no-cache-dir \
    camoufox[geoip]>=0.4.8 \
    camoufox-captcha>=0.1.2 \
    fastapi>=0.115.5 \
    requests>=2.32.3 \
    uvicorn>=0.32.1

# Expose port
EXPOSE 6090

# Run the webhook server
CMD ["python", "webhook_server.py"]
