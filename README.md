# ComfyRent Real Estate Scraper - Automated Docker Deployment

## Overview

This is a production-ready real estate scraping system with separated multilingual processing for optimal performance. Everything runs automatically through Docker Compose with no additional scripts needed.

### Architecture

- **Main Scraper**: Fast property data extraction (every 15 seconds)
- **Multilingual Worker**: Background translation processing (every 5 minutes)
- **PostgreSQL**: Database storage
- **Redis**: Caching and session management
- **Nginx**: Reverse proxy and static file serving

## Quick Start

### 1. Start Everything

```bash
# Start all services (builds images automatically)
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

### 2. Management Commands

```bash
# Stop all services
docker-compose down

# Restart services
docker-compose restart

# Rebuild from scratch (no cache)
docker-compose build --no-cache
docker-compose up -d

# View specific service logs
docker-compose logs -f scraper
docker-compose logs -f multilingual_worker

# Scale multilingual workers if needed
docker-compose up -d --scale multilingual_worker=2
```

## Development Mode

For development with live code mounting:

```bash
# Use override file for development settings
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d
```

## Services

### Main Scraper (`comfyrent-scraper`)
- **Purpose**: Fast property data extraction from MyHome.ge
- **Schedule**: Continuous operation (15-second intervals)
- **Resources**: 2GB RAM, 1 CPU core
- **Container Size**: 316MB (optimized)
- **Features**: No multilingual processing overhead

### Multilingual Worker (`comfyrent-multilingual-worker`)
- **Purpose**: Background translation processing
- **Schedule**: Continuous background processing (5-minute intervals)
- **Resources**: 1GB RAM, 0.5 CPU core
- **Container Size**: 535MB (includes translation libraries)
- **Languages**: Georgian, English, Russian

## Configuration

### Environment Variables

The system uses `.env.production` for configuration:

```bash
# Database
POSTGRES_HOST=postgres
POSTGRES_DB=comfyrent_production
POSTGRES_USER=comfyrent_user

# Scraper Settings
SCRAPER_CONCURRENT_LANGUAGES=false  # Disabled for main scraper
MAX_PROPERTIES=50000
BATCH_SIZE=50
SCRAPE_INTERVAL=15
```

### Secrets

Required secret files in `./secrets/`:
- `postgres_password.txt` - PostgreSQL password
- `minio_root_user.txt` - MinIO username
- `minio_root_password.txt` - MinIO password
- `jwt_secret_key.txt` - JWT secret key

## Monitoring

### Service Status
```bash
./deploy.sh status
```

### Real-time Logs
```bash
# All services
./deploy.sh logs

# Specific service
./deploy.sh logs scraper
./deploy.sh logs multilingual_worker
```

### Docker Stats
```bash
docker stats comfyrent-scraper comfyrent-multilingual-worker
```

## Performance

### Optimizations Applied
- ✅ Separated multilingual processing from main scraper
- ✅ Optimized container sizes (316MB vs 535MB)
- ✅ Independent resource allocation
- ✅ Fault isolation between services
- ✅ Automatic restart policies

### Expected Performance
- **Main Scraper**: ~1000+ properties/hour (without multilingual delays)
- **Multilingual Worker**: ~10 properties/batch every 5 minutes
- **Memory Usage**: Main scraper uses ~40% less memory without multilingual libraries

## Troubleshooting

### Common Issues

1. **Services won't start**
   ```bash
   # Check Docker is running
   docker info
   
   # Check secrets exist
   ls -la ./secrets/
   
   # Rebuild images
   docker-compose build --no-cache
   docker-compose up -d
   ```

2. **Database connection errors**
   ```bash
   # Check PostgreSQL is healthy
   docker-compose ps postgres
   
   # View PostgreSQL logs
   docker-compose logs postgres
   ```

3. **High resource usage**
   ```bash
   # Check container stats
   docker stats
   
   # Adjust resource limits in docker-compose.yml
   ```

### Container Health Checks

Both containers include built-in health checks:
- **Main Scraper**: Checks every 30 seconds if scraper process is running
- **Multilingual Worker**: Checks every 60 seconds if worker process is running

### Logs Location

- **Container logs**: `docker-compose logs [service]`
- **Persistent logs**: Docker volumes `scraper_logs` and `multilingual_logs`

## File Structure

```
real_estate_deployment/
├── deploy.sh                 # Main deployment script
├── docker-compose.yml        # Service orchestration
├── .env.production          # Environment configuration
├── secrets/                 # Secret files
├── back-end/
│   ├── scraper/
│   │   ├── myhome_scraper.py          # Main scraper (optimized)
│   │   ├── multilingual_worker.py     # Multilingual processor
│   │   ├── Dockerfile.production      # Main scraper container
│   │   └── Dockerfile.multilingual    # Multilingual worker container
│   └── [other backend files]
└── [other project files]
```

## Development

### Building Images Manually

```bash
# Main scraper
docker build -f back-end/scraper/Dockerfile.production -t comfyrent-scraper ./back-end

# Multilingual worker
docker build -f back-end/scraper/Dockerfile.multilingual -t comfyrent-multilingual-worker ./back-end
```

### Testing Individual Services

```bash
# Test main scraper
docker run --rm comfyrent-scraper python /app/scraper/myhome_scraper.py --help

# Test multilingual worker
docker run --rm comfyrent-multilingual-worker python /app/scraper/multilingual_worker.py --help
```

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `docker-compose up -d` | Start all services |
| `docker-compose down` | Stop all services |
| `docker-compose restart` | Restart all services |
| `docker-compose ps` | Show service status |
| `docker-compose logs -f` | Show all logs |
| `docker-compose build --no-cache` | Rebuild containers |

🚀 **Everything runs automatically - no scripts needed!**
