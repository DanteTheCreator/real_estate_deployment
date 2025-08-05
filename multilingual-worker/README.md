# Multilingual Worker Service

A standalone service for processing multilingual content (English and Russian translations) for real estate properties using the MyHome.ge API.

## Features

- Fetches English and Russian translations from MyHome.ge API
- Updates property records in the database with multilingual content
- Fallback translation system for basic Georgian terms
- Batch processing with configurable intervals
- Docker containerized deployment
- Comprehensive logging and error handling

## Project Structure

```
multilingual-worker/
├── main.py                           # Main worker application
├── src/
│   ├── core/
│   │   └── config.py                 # Configuration management
│   ├── models/
│   │   └── property_data.py          # Property data models
│   ├── processors/
│   │   └── multilingual_processor.py # API processing logic
│   └── services/
│       └── database_service.py       # Database operations
├── requirements.txt                  # Python dependencies
├── Dockerfile                        # Docker build configuration
├── docker-compose.yml               # Docker deployment
└── .env.example                     # Environment variables template
```

## Setup

### Local Development

1. **Clone and navigate to the directory:**
   ```bash
   cd multilingual-worker
   ```

2. **Create environment file:**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the worker:**
   ```bash
   python main.py
   ```

### Docker Deployment

1. **Build and run with Docker Compose:**
   ```bash
   # Build the service
   docker-compose build

   # Run in standalone mode (includes its own PostgreSQL)
   docker-compose --profile multilingual up -d

   # Or connect to existing network
   POSTGRES_PASSWORD=your_password docker-compose --profile multilingual up -d
   ```

2. **Connect to existing infrastructure:**
   ```bash
   # If you have the main real estate application running
   docker-compose -f ../docker-compose.yml -f docker-compose.yml up multilingual-worker
   ```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `API_TOKEN` | MyHome.ge API authorization token | Required |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | INFO |
| `BATCH_SIZE` | Number of properties to process per batch | 50 |
| `PROCESS_INTERVAL` | Seconds between processing cycles | 300 |
| `MAX_RETRIES` | Maximum retries for failed API requests | 3 |
| `DEBUG_MODE` | Enable debug mode for detailed logging | false |

### Database Requirements

The service expects a PostgreSQL database with a `properties` table containing the following columns:

- `id`: Primary key
- `external_id`: External property ID from MyHome.ge
- `title`: Georgian title
- `description`: Georgian description
- `title_en`: English title (updated by this service)
- `title_ru`: Russian title (updated by this service)
- `description_en`: English description (updated by this service)
- `description_ru`: Russian description (updated by this service)

## How It Works

1. **Property Discovery**: Queries the database for properties that don't have English or Russian translations
2. **API Processing**: Fetches property details from MyHome.ge API for each supported language
3. **Content Extraction**: Extracts titles and descriptions from API responses
4. **Database Update**: Updates the property records with the new multilingual content
5. **Fallback Translation**: Applies basic term translations if API fails
6. **Continuous Processing**: Repeats the cycle at configured intervals

## API Integration

The service integrates with the MyHome.ge API:
- **Endpoint**: `https://api-statements.tnet.ge/v1/statements/{property_id}`
- **Languages**: English (`en`) and Russian (`ru`)
- **Authentication**: Uses global authorization token
- **Rate Limiting**: Built-in delays between requests

## Logging

Logs are written to both console and files (if volume mounted):
- Application logs: `/app/logs/multilingual_worker.log`
- Error logs: Captured with full stack traces
- Progress tracking: Batch processing statistics

## Monitoring

The service logs key metrics:
- Properties processed per batch
- API success/failure rates
- Database update statistics
- Processing time per batch

## Error Handling

- **API Failures**: Automatic retries with exponential backoff
- **Database Errors**: Transaction rollback and error logging
- **Network Issues**: Graceful handling with fallback translations
- **Invalid Data**: Skips problematic records and continues

## Development

### Adding New Languages

1. Update `language_codes` in `MultilingualProcessor`
2. Add new fields to the `PropertyData` model
3. Update database schema accordingly
4. Extend the API processing logic

### Testing

```bash
# Test with a specific property ID
python -c "
import asyncio
from main import MultilingualWorker
from src.core.config import MultilingualConfig

async def test():
    config = MultilingualConfig()
    worker = MultilingualWorker(config)
    await worker.process_single_property('20246666')

asyncio.run(test())
"
```

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check `DATABASE_URL` format
   - Ensure PostgreSQL is running and accessible
   - Verify credentials and database name

2. **API Authorization Failed**
   - Check if `API_TOKEN` is valid and not expired
   - Verify network connectivity to api-statements.tnet.ge

3. **No Properties to Process**
   - Ensure properties table has records with `external_id`
   - Check if properties already have multilingual content

4. **Docker Issues**
   - Ensure Docker network exists: `docker network create real_estate_network`
   - Check environment variables are properly set
   - Verify volume mounts for logs

### Debug Mode

Enable debug mode for detailed logging:
```bash
DEBUG_MODE=true python main.py
```

This will show:
- Full API responses
- SQL queries
- Detailed processing steps
- Performance metrics
