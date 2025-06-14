FROM python:3.11-slim-bullseye

# Install Node.js for frontend build
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    libu2f-udev \
    libxss1 \
    libgconf-2-4 \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN python -m playwright install chromium

# Install Playwright browsers and dependencies
RUN python -m playwright install-deps chromium && \
    python -m playwright install chromium

# Verify Playwright installation
RUN python -m playwright install --help

# Copy application code
COPY . .

# Build React frontend if it exists
RUN if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then \
        cd frontend && \
        npm install && \
        npm run build; \
    fi

# Create necessary directories
RUN mkdir -p /app/data /app/logs

# Set Python path so 'app' module can be found
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Default command - run in production mode
CMD ["python", "-c", "import uvicorn; from app.main import app; uvicorn.run(app, host='0.0.0.0', port=8000, reload=False)"]