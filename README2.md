
## 🚀 Setup Steps

### 1. Clone Your Repository
```bash
git clone https://github.com/ftomer/amazonmonitor.git
cd amazonmonitor
```

### 2. Copy Docker Files
Place the provided Docker files in your project root:
- `Dockerfile`
- `docker-compose.yml`
- `.env` (template)
- `setup-pi.sh`

### 3. Configure Your Application

#### Edit `.env` file:
```bash
nano .env
```

#### Edit `data/config.json`:
```bash
nano data/config.json
```

### 4. Build and Run
```bash
# Make setup script executable
chmod +x setup-pi.sh

# Build the Docker image
docker-compose build

# Run the container
docker-compose up -d

# View logs
docker-compose logs -f amazon-price-monitor
```

## 🔧 Application Entry Point

The Docker container will run your application using:
```bash
python app/main.py
```

Make sure your `app/main.py` file:
1. Contains the main application logic
2. Handles configuration loading
3. Implements the price monitoring loop
4. Manages email notifications
