#!/bin/bash

# Local Development Setup for Amazon Price Monitor
# This script sets up both frontend and backend for local testing

echo "🚀 Setting up Amazon Price Monitor for local development..."

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Create project structure
echo -e "${BLUE}📁 Creating project structure...${NC}"
mkdir -p frontend/src frontend/public
mkdir -p logs data

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}⚠️  Node.js not found. Please install Node.js from https://nodejs.org${NC}"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}⚠️  Python 3 not found. Please install Python 3${NC}"
    exit 1
fi

# Setup Python virtual environment
echo -e "${BLUE}🐍 Setting up Python virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo -e "${BLUE}📦 Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements-fastapi.txt
playwright install chromium

# Setup React frontend
echo -e "${BLUE}⚛️  Setting up React frontend...${NC}"
cd frontend

# Initialize React app if package.json doesn't exist
if [ ! -f "package.json" ]; then
    echo -e "${BLUE}🔧 Initializing React app...${NC}"
    npx create-react-app . --template minimal
    
    # Install additional dependencies
    npm install lucide-react
fi

# Copy our custom files
echo -e "${BLUE}📝 Copying React files...${NC}"

# Create the HTML file
cat > public/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="Amazon Price Monitor - Track product prices and get alerts" />
    <title>Amazon Price Monitor</title>
    <script src="https://cdn.tailwindcss.com"></script>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
EOF

# Update package.json to include proxy
npm pkg set proxy="http://localhost:8000"

cd ..

echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo -e "${BLUE}🎯 Next steps:${NC}"
echo ""
echo -e "${YELLOW}1. Copy the React App.js content:${NC}"
echo "   Copy the content from the 'src/App.js (Updated for Local Dev)' artifact"
echo "   Save it to: frontend/src/App.js"
echo ""
echo -e "${YELLOW}2. Copy the Python files:${NC}"
echo "   Copy main.py and amazon_price_monitor.py to the root directory"
echo ""
echo -e "${YELLOW}3. Start the backend:${NC}"
echo "   source venv/bin/activate"
echo "   python main.py"
echo ""
echo -e "${YELLOW}4. In a new terminal, start the frontend:${NC}"
echo "   cd frontend"
echo "   npm start"
echo ""
echo -e "${GREEN}🌐 Access URLs:${NC}"
echo "   Frontend (React): http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo -e "${BLUE}💡 Development Tips:${NC}"
echo "• React will auto-reload when you change files"
echo "• Backend will auto-reload with --reload flag"
echo "• API calls from React go through proxy to backend"
echo "• Check browser console for any errors"
echo "• Mock data will show if backend is not running"