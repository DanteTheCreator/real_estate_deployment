#!/bin/bash

# House Rental FastAPI Backend Setup and Run Script with Docker

echo "🏠 House Rental FastAPI Backend (Docker Setup)"
echo "=============================================="

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first:"
    echo "   - macOS: https://docs.docker.com/desktop/mac/"
    echo "   - Linux: https://docs.docker.com/engine/install/"
    echo "   - Windows: https://docs.docker.com/desktop/windows/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first:"
    echo "   - https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are available"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating sample .env file..."
    cat > .env << EOL
# Database Configuration (Docker setup)
DATABASE_URL=postgresql://real-estate-user:real-estate-password@localhost:5432/real-estate-rental

# Security Configuration
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:8080,http://127.0.0.1:3000

# App Configuration
APP_NAME=House Rental API
VERSION=1.0.0
DEBUG=true

# MinIO Configuration (Docker setup)
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=real-estate
MINIO_SECURE=false
EOL
    echo "✅ Sample .env file created. Please update with your settings."
fi

echo ""
echo "� Starting Docker services (PostgreSQL + MinIO)..."

# Start Docker Compose services
if docker compose up -d; then
    echo "✅ Docker services started successfully"
else
    echo "❌ Failed to start Docker services. Trying with docker-compose..."
    if docker-compose up -d; then
        echo "✅ Docker services started successfully"
    else
        echo "❌ Failed to start Docker services. Please check Docker installation."
        exit 1
    fi
fi

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 5

# Check if services are healthy
echo "🔍 Checking service health..."
for i in {1..30}; do
    if docker compose ps postgres | grep -q "healthy\|running"; then
        echo "✅ PostgreSQL is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ PostgreSQL failed to start properly"
        docker compose logs postgres
        exit 1
    fi
    sleep 2
done

# Test database connection
echo "🔍 Testing database connection..."
if python -c "
from config import settings
from sqlalchemy import create_engine, text
try:
    engine = create_engine(settings.database_url)
    with engine.connect() as conn:
        conn.execute(text('SELECT 1'))
    print('✅ Database connection successful!')
    exit(0)
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    exit(1)
" 2>/dev/null; then
    echo "✅ Database connection verified!"
else
    echo "❌ Database connection failed. Please check Docker services:"
    echo "   Run: docker compose logs postgres"
    echo ""
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Exiting..."
        exit 1
    fi
fi

echo ""

# Offer to run database setup
read -p "Do you want to run database setup now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python setup_database.py
fi

echo ""
echo "🚀 Starting the FastAPI server..."
echo "📡 Server will be available at: http://localhost:8000"
echo "📚 API documentation at: http://localhost:8000/docs"
echo "🔍 Alternative docs at: http://localhost:8000/redoc"
echo "🗄️  PostgreSQL admin: Use any PostgreSQL client with:"
echo "   Host: localhost, Port: 5432"
echo "   Database: real-estate-rental"
echo "   User: real-estate-user, Password: real-estate-password"
echo "📦 MinIO console: http://localhost:9001"
echo "   Username: minioadmin, Password: minioadmin"
echo ""

# Check if port 8000 is already in use
if lsof -ti:8000 >/dev/null 2>&1; then
    echo "⚠️  Port 8000 is already in use. Stopping existing processes..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    sleep 1
    echo "✅ Port 8000 is now available"
fi

echo "Press Ctrl+C to stop the server"
echo "To stop Docker services later, run: docker compose down"
echo ""

# Run the FastAPI application
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
