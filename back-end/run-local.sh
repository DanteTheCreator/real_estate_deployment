#!/bin/bash

# House Rental FastAPI Backend Setup and Run Script (Local PostgreSQL)

echo "🏠 House Rental FastAPI Backend (Local Setup)"
echo "============================================="

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

# Check if PostgreSQL is installed and running
if ! command -v psql &> /dev/null; then
    echo "⚠️  PostgreSQL is not installed. Please install PostgreSQL first:"
    echo "   - macOS: brew install postgresql@14"
    echo "   - Ubuntu: sudo apt-get install postgresql"
    echo ""
    echo "📝 Or use Docker setup: ./run.sh"
    echo ""
    exit 1
else
    # Check if PostgreSQL service is running
    if brew services list | grep -q "postgresql.*started"; then
        echo "✅ PostgreSQL is installed and running"
    else
        echo "⚠️  PostgreSQL is installed but not running. Starting it..."
        brew services start postgresql@14
        sleep 2
        if brew services list | grep -q "postgresql.*started"; then
            echo "✅ PostgreSQL started successfully"
        else
            echo "❌ Failed to start PostgreSQL. Please start it manually:"
            echo "   brew services start postgresql@14"
            exit 1
        fi
    fi
fi

# Check if .env file exists and set it up for local PostgreSQL
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating sample .env file for local setup..."
    cat > .env << EOL
# Database Configuration (Local PostgreSQL)
DATABASE_URL=postgresql://\$USER:@localhost:5432/real-estate-rental

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

# MinIO Configuration (requires separate MinIO installation)
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=real-estate
MINIO_SECURE=false
EOL
    echo "✅ Sample .env file created for local PostgreSQL setup."
fi

# Create database if it doesn't exist
echo "🗄️  Setting up local database..."
if ! psql -lqt | cut -d \| -f 1 | grep -qw real-estate-rental; then
    echo "📝 Creating database 'real-estate-rental'..."
    createdb real-estate-rental
    echo "✅ Database created successfully"
else
    echo "✅ Database 'real-estate-rental' already exists"
fi

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
    echo "❌ Database connection failed. Please check your local PostgreSQL setup."
    exit 1
fi

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
echo ""
echo "⚠️  Note: For full functionality, you may need to install and configure MinIO separately"
echo "   Or use Docker setup: ./run.sh"
echo ""

# Check if port 8000 is already in use
if lsof -ti:8000 >/dev/null 2>&1; then
    echo "⚠️  Port 8000 is already in use. Stopping existing processes..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    sleep 1
    echo "✅ Port 8000 is now available"
fi

echo "Press Ctrl+C to stop the server"
echo ""

# Run the FastAPI application
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
