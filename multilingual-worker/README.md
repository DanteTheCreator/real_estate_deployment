# Multilingual Content Worker

A dedicated service for processing multilingual content for properties. Fetches English and Russian translations from MyHome.ge API and updates the database with multilingual content.

## Integration

This service is now integrated into the main `docker-compose.yml` file in the root directory. 

## Running the Service

To start the multilingual worker along with all other services:

```bash
# From the root directory (/real_estate_deployment)
docker compose up -d multilingual_worker

# Or start all services
docker compose up -d
```

## Configuration

The worker is configured through environment variables in the main docker-compose.yml:

- `BATCH_SIZE`: Number of properties to process at once (default: 50)
- `PROCESS_INTERVAL`: Seconds between processing cycles (default: 300)
- `MAX_RETRIES`: Maximum retry attempts for failed requests (default: 3)
- `LOG_LEVEL`: Logging level (default: INFO)
- `DEBUG_MODE`: Enable debug mode (default: false)

## Logs

Logs are available in the `./logs/` directory and are also accessible via Docker:

```bash
docker compose logs multilingual_worker
```

## Database Connection

The service connects to the main PostgreSQL database using Docker secrets for secure authentication.

## Architecture

- **Language**: Python 3.11
- **Database**: PostgreSQL (shared with main application)
- **API Integration**: MyHome.ge API for translations
- **Container**: Runs as non-root user for security
- **Health Checks**: Built-in health monitoring
