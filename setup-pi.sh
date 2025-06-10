#!/bin/bash

# Complete setup script for Amazon Price Monitor on Raspberry Pi
# Run with: curl -sSL https://amazonmonitor/setup-pi.sh | bash

set -e

echo "🍓 Setting up Amazon Price Monitor on Raspberry Pi..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get Pi IP address
PI_IP=$(hostname -I | awk '{print $1}')

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Warning: This doesn't appear to be a Raspberry Pi${NC}"
fi

# Update system
echo -e "${BLUE}📦 Updating system packages...${NC}"
sudo apt-get update -qq

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo -e "${BLUE}🐳 Installing Docker...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo -e "${YELLOW}⚠️  Please log out and back in for Docker permissions${NC}"
fi

# Install Docker Compose if not present
if ! command -v docker-compose &> /dev/null; then
    echo -e "${BLUE}📦 Installing Docker Compose...${NC}"
    sudo apt-get install -y docker-compose
fi

# Create project directory
PROJECT_DIR="$HOME/amazon-price-monitor"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# Create necessary directories
mkdir -p logs data frontend/src frontend/public

echo -e "${BLUE}📁 Creating project structure...${NC}"

# Create basic React frontend structure
cat > frontend/package.json << 'EOF'
{
  "name": "price-monitor-frontend",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "lucide-react": "^0.263.1"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": ["react-app"]
  },
  "browserslist": {
    "production": [">0.2%", "not dead", "not op_mini all"],
    "development": ["last 1 chrome version", "last 1 firefox version", "last 1 safari version"]
  }
}
EOF

cat > frontend/public/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Amazon Price Monitor</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
    <div id="root"></div>
</body>
</html>
EOF

cat > frontend/src/index.js << 'EOF'
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
EOF

# Note: The App.js content would be copied from the React artifact above

# Create nginx config for optional reverse proxy
cat > nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server amazon-price-monitor:8000;
    }

    server {
        listen 80;
        server_name _;

        # Serve static files
        location /static/ {
            proxy_pass http://backend;
        }

        # API routes
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        # Frontend routes
        location / {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }
}
EOF

# Create default config if it doesn't exist
if [ ! -f "config.json" ]; then
    echo -e "${BLUE}⚙️  Creating default configuration...${NC}"
    cat > config.json << 'EOF'
{
    "products": [
        {
            "name": "Echo Dot (3rd Gen) - Example",
            "url": "https://www.amazon.com/gp/product/B0757911C2/",
            "target_price": 30.00
        }
    ],
    "check_interval_minutes": 120,
    "email_notifications": {
        "enabled": false,
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "sender_email": "your_email@gmail.com",
        "sender_password": "your_app_password",
        "recipient_email": "recipient@gmail.com"
    },
    "desktop_notifications": {
        "enabled": false
    }
}
EOF
fi

# Set proper permissions
chmod 644 config.json
chmod +x setup-pi.sh

echo -e "${GREEN}✅ Project structure created!${NC}"
echo ""
echo -e "${BLUE}📝 Next steps:${NC}"
echo "1. Copy your Python files (main.py, amazon_price_monitor.py, requirements-fastapi.txt)"
echo "2. Copy the React App.js content to frontend/src/App.js"
echo "3. Edit config.json with your products and email settings"
echo "4. Build and run:"
echo "   docker-compose up -d"
echo ""
echo -e "${GREEN}🌐 Access URLs:${NC}"
echo "📱 Web Interface: http://$PI_IP:8000"
echo "📖 API Docs: http://$PI_IP:8000/docs"
echo "🔧 Direct API: http://$PI_IP:8000/api/v1/status"
echo ""
echo -e "${BLUE}💡 Pro Tips:${NC}"
echo "• Set longer check intervals (2-4 hours) to be gentle on resources"
echo "• Use email notifications since desktop notifications don't work headless"
echo "• Monitor resource usage: docker stats"
echo "• View logs: docker-compose logs -f"
echo "• Access from any device on your network using the Pi's IP"
echo ""
echo -e "${GREEN}🎉 Setup complete! Happy price monitoring!${NC}"