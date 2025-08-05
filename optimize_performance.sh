#!/bin/bash

echo "🔧 ComfyRent Backend Performance Optimization"
echo "============================================"

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Run database optimization
echo "📊 Optimizing database performance..."
docker exec -it comfyrent-backend python /app/optimize_db.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Database optimization completed!"
    echo ""
    echo "🔄 Restarting backend container to apply all changes..."
    docker restart comfyrent-backend
    
    echo ""
    echo "⏳ Waiting for backend to be ready..."
    sleep 10
    
    # Check if backend is healthy
    echo "🏥 Checking backend health..."
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
    
    if [ "$response" = "200" ]; then
        echo "✅ Backend is healthy and ready!"
        echo ""
        echo "🎉 Performance optimization completed successfully!"
        echo "📈 Your API should now respond much faster!"
        echo ""
        echo "Key improvements applied:"
        echo "  ✓ Database connection pooling"
        echo "  ✓ Critical search indexes added"
        echo "  ✓ Redis caching enabled"
        echo "  ✓ Query optimizations"
        echo ""
        echo "Test your frontend now - it should be significantly faster! 🚀"
    else
        echo "⚠️  Backend may need a moment to fully start"
        echo "   Check with: docker logs comfyrent-backend"
    fi
else
    echo "❌ Database optimization failed!"
    echo "   Check the logs above for details"
fi
