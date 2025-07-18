# Real Estate Application - Docker Compose Setup

This Docker Compose configuration allows you to run the entire Real Estate application stack with a single command.

## Architecture

The application consists of 5 services:

1. **PostgreSQL Database** - Stores application data
2. **MinIO** - Object storage for property images
3. **Backend API** - FastAPI application serving the REST API
4. **Frontend** - React/Vite application for the user interface
5. **Scraper** - Python script that scrapes property data and populates the database

## Prerequisites

- Docker
- Docker Compose V2

## Quick Start

1. Clone the repository and navigate to the project root:
```bash
cd /path/to/real-estate
```

2. Start all services:
```bash
docker compose up --build
```

This command will:
- Build Docker images for backend, frontend, and scraper
- Start PostgreSQL and MinIO
- Initialize the database with the schema
- Start the backend API server
- Start the frontend development server
- Run the scraper to populate the database with property data

## Service URLs

Once all services are running, you can access:

- **Frontend Application**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **MinIO Console**: http://localhost:9001 (admin/minioadmin)
- **PostgreSQL**: localhost:5432

## Environment Variables

Each service uses environment variables for configuration:

### Backend
- `DATABASE_URL`: PostgreSQL connection string
- `MINIO_ENDPOINT`: MinIO server endpoint
- `MINIO_ACCESS_KEY` / `MINIO_SECRET_KEY`: MinIO credentials
- `CORS_ORIGINS`: Allowed frontend origins
- `SECRET_KEY`: JWT secret key

### Frontend
- `VITE_API_URL`: Backend API endpoint
- `VITE_API_BASE_URL`: Base URL for API calls

### Scraper
- `DATABASE_URL`: PostgreSQL connection string
- `PYTHONUNBUFFERED`: Python output buffering

## Development Mode

The Docker Compose setup is configured for development:

- **Backend**: Runs with `--reload` flag for hot reloading
- **Frontend**: Runs Vite dev server with hot module replacement
- **Volume mounts**: Source code is mounted for live editing

## Production Deployment

For production deployment, you should:

1. Change default passwords and secrets
2. Use production-optimized Dockerfiles
3. Set up proper SSL/TLS certificates
4. Configure production environment variables
5. Set up proper backup strategies for data volumes

## Commands

### Start all services
```bash
docker compose up --build
```

### Start in background
```bash
docker compose up -d --build
```

### Stop all services
```bash
docker compose down
```

### View logs
```bash
docker compose logs -f [service-name]
```

### Rebuild specific service
```bash
docker compose build [service-name]
docker compose up [service-name]
```

### Run scraper manually
```bash
docker compose run --rm scraper python enhanced_scraper.py
```

## Data Persistence

The following volumes are created for data persistence:

- `postgres_data`: PostgreSQL database files
- `minio_data`: MinIO object storage files

## Troubleshooting

### Services won't start
1. Check if ports 3000, 5432, 8000, 9000, 9001 are available
2. Ensure Docker daemon is running
3. Check service logs: `docker compose logs [service-name]`

### Database connection issues
1. Wait for PostgreSQL to fully initialize (check health status)
2. Verify environment variables are correct
3. Check if init-db.sql runs successfully

### Frontend can't connect to backend
1. Verify backend is running on port 8000
2. Check CORS configuration in backend
3. Ensure API URL environment variables are set correctly

### Build failures
1. Ensure all Dockerfiles are present
2. Check for missing requirements.txt files
3. Verify network connectivity for downloading dependencies

## Scaling

To run multiple instances of a service:

```bash
docker compose up --scale backend=3 --scale frontend=2
```

Note: You'll need to configure a load balancer for multiple instances.

## Monitoring

Check service health:
```bash
docker compose ps
```

Monitor resource usage:
```bash
docker stats
```

## Cleanup

Remove all containers, networks, and volumes:
```bash
docker compose down -v --rmi all
```
