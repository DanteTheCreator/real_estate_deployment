#!/bin/bash

# Real Estate Backend - Streamlined Startup Script

echo "🏠 Real Estate Backend"
echo "===================="

# Check if virtual environment exists and create if needed
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

echo "🔄 Activating virtual environment..."
source .venv/bin/activate

echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Start MinIO if not running
if ! lsof -ti:9000 >/dev/null 2>&1; then
    echo "🗄️  Starting MinIO server..."
    mkdir -p minio-data
    nohup minio server minio-data --console-address ":9001" > minio.log 2>&1 &
    sleep 3
    
    # Setup MinIO bucket and images
    echo "🔧 Setting up MinIO bucket..."
    python3 setup_complete_minio.py
else
    echo "✅ MinIO already running"
fi

# Test database connection
echo "🔍 Testing database connection..."
if python3 -c "
from config import settings
from sqlalchemy import create_engine, text
try:
    engine = create_engine(settings.database_url)
    with engine.connect() as conn:
        conn.execute(text('SELECT 1'))
    print('✅ Database ready!')
except Exception as e:
    print(f'❌ Database error: {e}')
    exit(1)
"; then
    echo "✅ Database connection verified!"
else
    echo "❌ Database connection failed. Check your PostgreSQL setup."
    exit 1
fi

# Kill any existing server on port 8000
if lsof -ti:8000 >/dev/null 2>&1; then
    echo "⚠️  Stopping existing server..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    sleep 1
fi

echo ""
echo "🚀 Starting FastAPI server..."
echo "📡 API: http://localhost:8000"
echo "📚 Docs: http://localhost:8000/docs"
echo "🗄️  MinIO: http://localhost:9001 (minioadmin/minioadmin)"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start the FastAPI server
python3 -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
