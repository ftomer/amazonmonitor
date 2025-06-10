#!/bin/bash

# Raspberry Pi Docker Setup Script for Amazon Price Monitor
# Run this script on your Raspberry Pi to set up the environment

set -e

echo "🚀 Setting up Amazon Price Monitor on Raspberry Pi..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    print_warning "This script is designed for Raspberry Pi. Proceeding anyway..."
fi

# Update system
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    print_status "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    print_status "Docker installed successfully!"
else
    print_status "Docker is already installed"
fi

# Install Docker Compose if not present
if ! command -v docker-compose &> /dev/null; then
    print_status "Installing Docker Compose..."
    sudo apt install -y docker-compose
    print_status "Docker Compose installed successfully!"
else
    print_status "Docker Compose is already installed"
fi

# Create application directory
APP_DIR="$HOME/amazon-price-monitor"
if [ ! -d "$APP_DIR" ]; then
    print_status "Creating application directory at $APP_DIR"
    mkdir -p "$APP_DIR"
fi

cd "$APP_DIR"

# Create necessary directories
mkdir -p data logs

# Create sample configuration files if they don't exist
if [ ! -f "config.json" ]; then
    print_status "Creating sample config.json..."
    cat > config.json << 'EOF'
{
  "products": [
    {
      "name": "Example Product",
      "url": "https://www.amazon.com/dp/B0XXXXXXXX",
      "target_price": 50.00
    }
  ],
  "check_interval_minutes": 120,
  "email_notifications": {
    "enabled": true
  }
}
EOF
fi

if [ ! -f ".env" ]; then
    print_status "Creating .env template..."
    cat > .env << 'EOF'
# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_SENDER_EMAIL=your-email@gmail.com
SMTP_SENDER_PASSWORD=your-app-password
SMTP_RECIPIENT_EMAIL=recipient@gmail.com

# Application Configuration
LOG_LEVEL=INFO
EOF
fi

# Set proper permissions
chmod 600 .env
chmod 644 config.json

print_status "Setup completed successfully! 🎉"
echo
print_status "Next steps:"
echo "1. Edit the .env file with your email configuration"
echo "2. Edit config.json with your products to monitor"
echo "3. Run: docker-compose up -d"
echo "4. Monitor logs: docker-compose logs -f"
echo
print_warning "Don't forget to:"
echo "• Set up Gmail app password if using Gmail"
echo "• Add your actual product URLs to config.json"
echo "• Test with longer check intervals (2+ hours) to avoid being blocked"
echo
print_status "Application directory: $APP_DIR"