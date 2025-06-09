# Multi-stage build for Raspberry Pi
FROM node:18-alpine AS frontend-builder

# Build React frontend
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Python backend stage
FROM python:3.11-slim

# Install system dependencies for ARM
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    gnupg \
    unzip \
    xvfb \
    chromium \
    chromium-driver \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libdrm2 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libxss1 \
    libxtst6 \
    && rm -rf /var/lib/apt/lists/*

# Set environment for headless operation
ENV DISPLAY=:99
ENV PYTHONUNBUFFERED=1

# Create app directory
WORKDIR /app

# Copy Python requirements and install
COPY requirements-fastapi.txt .
RUN pip install --no-cache-dir -r requirements-fastapi.txt

# Install Playwright browsers
RUN playwright install chromium

# Copy React build from frontend stage
COPY --from=frontend-builder /frontend/build ./frontend/build

# Copy Python application
COPY main.py .
COPY amazon_price_monitor.py .
COPY config.json .

# Create directories
RUN mkdir -p /app/logs /app/data

# Create non-root user
RUN useradd -m -u 1000 pricebot && \
    chown -R pricebot:pricebot /app
USER pricebot

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=2m --timeout=30s --start-period=1m --retries=3 \
    CMD curl -f http://localhost:8000/api/status || exit 1

# Run FastAPI with network access
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]