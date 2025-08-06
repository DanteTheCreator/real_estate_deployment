# Multilingual Worker Logs

This directory is mounted as a volume in the Docker container to store multilingual worker logs.

The multilingual worker itself runs from the backend Docker image and executes:
- `/app/scraper/multilingual_worker.py`

## Log Files
- `multilingual_worker.log` - Main worker processing logs
- Docker container logs are also available via `docker compose logs multilingual_worker`

## Configuration
The worker is configured through environment variables in docker-compose.yml:
- `BATCH_SIZE` - Number of properties to process per batch
- `CHECK_INTERVAL` - Time between processing runs (seconds)
- `MODE` - Processing mode
- `SCRAPER_CONCURRENT_LANGUAGES` - Enable concurrent language processing
