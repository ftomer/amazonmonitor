# 🛒 Amazon Price Monitor

A Python application that monitors Amazon product prices and sends notifications when prices drop below your target thresholds. Built with Crawl4AI for reliable price extraction and supports multiple notification methods.

## ✨ Features

- **Smart Price Extraction**: Uses Crawl4AI with multiple fallback methods for reliable Amazon price scraping
- **Multiple Notification Types**: Desktop notifications, email alerts, and webhook support
- **Price History Tracking**: Maintains historical price data with timestamps
- **Continuous Monitoring**: Runs in background with configurable check intervals
- **Docker Support**: Ready-to-run Docker container for Raspberry Pi and other platforms
- **Cross-Platform**: Works on Windows, macOS, Linux, and Raspberry Pi

## 🚀 Quick Start

## On RasPi
```bash
hostname -I  # On the Pi
```
# Or check your router's device list

### Local Installation

1. **Clone and setup:**
```bash
git clone <your-repo-url>
cd amazon-price-monitor
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
playwright install
```

3. **Configure your products:**
```bash
cp config.example.json config.json
# Edit config.json with your product URLs and notification settings
```

4. **Run the monitor:**
```bash
python amazon_price_monitor.py
```

### Docker Installation (Recommended for Raspberry Pi)

1. **Setup:**
```bash
chmod +x setup.sh
./setup.sh
```

2. **Configure and run:**
```bash
# Edit config.json with your settings
docker-compose up -d
```

3. **Monitor logs:**
```bash
docker-compose logs -f
```

## ⚙️ Configuration

Edit `config.json` to customize your monitoring:

```json
{
    "products": [
        {
            "name": "Product Name",
            "url": "https://www.amazon.com/gp/product/B0XXXXXXXX/",
            "target_price": 50.00
        }
    ],
    "check_interval_minutes": 60,
    "email_notifications": {
        "enabled": true,
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "sender_email": "your_email@gmail.com",
        "sender_password": "your_app_password",
        "recipient_email": "recipient@gmail.com"
    },
    "desktop_notifications": {
        "enabled": true
    }
}
```

### 📧 Email Setup (Gmail)

For Gmail notifications:

1. Enable 2-Factor Authentication
2. Generate an [App Password](https://support.google.com/accounts/answer/185833)
3. Use the app password (not your regular password) in `config.json`

### 🔔 Notification Types

- **Desktop Notifications**: Native system notifications (requires `plyer`)
- **Email Alerts**: SMTP email notifications
- **Webhook Support**: Slack/Discord webhooks (Docker config)

## 📁 Project Structure

```
amazon-price-monitor/
├── amazon_price_monitor.py    # Main application
├── config.json               # Your configuration (not in git)
├── config.example.json       # Configuration template
├── requirements.txt          # Python dependencies
├── requirements-docker.txt   # Docker-specific requirements
├── Dockerfile               # Docker image definition
├── docker-compose.yml       # Docker Compose setup
├── setup.sh                # Raspberry Pi setup script
├── .gitignore              # Git ignore rules
├── price_monitor.log       # Application logs
├── price_history.json      # Historical price data
└── README.md              # This file
```

## 🐳 Docker Deployment

Perfect for running 24/7 on a Raspberry Pi or server:

### Build and Run
```bash
# Build image
docker-compose build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Raspberry Pi Considerations

- Use email notifications instead of desktop notifications
- Consider longer check intervals (2-4 hours) to reduce load
- Monitor resource usage: `docker stats`
- Logs are persistent in `./logs/` directory

## 📊 Monitoring & Logs

### Log Files
- **Application logs**: `price_monitor.log`
- **Price history**: `price_history.json`
- **Docker logs**: `docker-compose logs`

### Health Checks
```bash
# Check if container is healthy
docker-compose ps

# View resource usage
docker stats

# Follow live logs
docker-compose logs -f amazon-price-monitor
```

## 🔧 Advanced Usage

### Multiple Products
Add multiple products to monitor in `config.json`:
```json
"products": [
    {
        "name": "Echo Dot",
        "url": "https://amazon.com/dp/B0757911C2",
        "target_price": 30.00
    },
    {
        "name": "iPad",
        "url": "https://amazon.com/dp/B09G9FPHY6",
        "target_price": 300.00
    }
]
```

### Custom Check Intervals
```json
"check_interval_minutes": 120  // Check every 2 hours
```

### Webhook Notifications
Add webhook support for Slack/Discord:
```json
"webhook_notifications": {
    "enabled": true,
    "slack_webhook": "https://hooks.slack.com/services/...",
    "discord_webhook": "https://discord.com/api/webhooks/..."
}
```

## 🛠️ Troubleshooting

### Common Issues

**Playwright Browser Error:**
```bash
playwright install
```

**Permission Denied (Docker):**
```bash
sudo usermod -aG docker $USER
# Log out and back in
```

**Price Extraction Fails:**
- Check if Amazon URL is accessible
- Verify product page format hasn't changed
- Check logs for specific error messages

**Email Notifications Not Working:**
- Verify SMTP settings
- Use app passwords for Gmail
- Check firewall settings

### Debug Mode
Add verbose logging:
```python
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Performance Tips

- **Check Intervals**: Don't check too frequently (Amazon may block)
- **Resource Monitoring**: Use `docker stats` to monitor usage
- **Log Rotation**: Implement log rotation for long-running instances
- **Multiple Instances**: Run separate containers for different product categories

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for personal use only. Please respect Amazon's terms of service and robots.txt. Don't overload their servers with too frequent requests.

---

**Happy deal hunting! 🎯**