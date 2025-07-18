#!/bin/bash

# Docker Services Management Script for Real Estate Backend

COMPOSE_FILE="docker-compose.yml"

case "$1" in
    "start")
        echo "🐳 Starting Docker services..."
        if docker compose -f $COMPOSE_FILE up -d; then
            echo "✅ Services started successfully"
        else
            echo "Trying with docker-compose..."
            docker-compose -f $COMPOSE_FILE up -d
        fi
        echo ""
        echo "📋 Service status:"
        docker compose -f $COMPOSE_FILE ps
        echo ""
        echo "🔗 Service URLs:"
        echo "   PostgreSQL: localhost:5432"
        echo "   MinIO API: http://localhost:9000"
        echo "   MinIO Console: http://localhost:9001"
        ;;
    
    "stop")
        echo "🛑 Stopping Docker services..."
        if docker compose -f $COMPOSE_FILE down; then
            echo "✅ Services stopped successfully"
        else
            echo "Trying with docker-compose..."
            docker-compose -f $COMPOSE_FILE down
        fi
        ;;
    
    "restart")
        echo "🔄 Restarting Docker services..."
        if docker compose -f $COMPOSE_FILE restart; then
            echo "✅ Services restarted successfully"
        else
            echo "Trying with docker-compose..."
            docker-compose -f $COMPOSE_FILE restart
        fi
        ;;
    
    "logs")
        service=${2:-""}
        if [ -z "$service" ]; then
            echo "📋 Showing logs for all services..."
            docker compose -f $COMPOSE_FILE logs -f
        else
            echo "📋 Showing logs for $service..."
            docker compose -f $COMPOSE_FILE logs -f $service
        fi
        ;;
    
    "status")
        echo "📋 Service status:"
        if docker compose -f $COMPOSE_FILE ps; then
            echo ""
            echo "🔗 Service URLs:"
            echo "   PostgreSQL: localhost:5432"
            echo "   MinIO API: http://localhost:9000"
            echo "   MinIO Console: http://localhost:9001"
        else
            echo "Trying with docker-compose..."
            docker-compose -f $COMPOSE_FILE ps
        fi
        ;;
    
    "clean")
        echo "🧹 Cleaning up Docker services and volumes..."
        echo "⚠️  This will remove all data in PostgreSQL and MinIO!"
        read -p "Are you sure? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if docker compose -f $COMPOSE_FILE down -v; then
                echo "✅ Services and volumes removed successfully"
            else
                echo "Trying with docker-compose..."
                docker-compose -f $COMPOSE_FILE down -v
            fi
        else
            echo "Cancelled"
        fi
        ;;
    
    "setup")
        echo "🔧 Setting up MinIO bucket..."
        # Wait for MinIO to be ready
        sleep 5
        # Create bucket using mc (MinIO client) if available
        if command -v mc &> /dev/null; then
            mc alias set local http://localhost:9000 minioadmin minioadmin
            mc mb local/real-estate --ignore-existing
            mc policy set public local/real-estate
            echo "✅ MinIO bucket 'real-estate' created and set to public"
        else
            echo "⚠️  MinIO client (mc) not found. Please create bucket manually:"
            echo "   1. Go to http://localhost:9001"
            echo "   2. Login with minioadmin/minioadmin"
            echo "   3. Create bucket 'real-estate'"
            echo "   4. Set bucket policy to public"
        fi
        ;;
    
    *)
        echo "🏠 Real Estate Docker Services Management"
        echo "========================================"
        echo ""
        echo "Usage: $0 {start|stop|restart|status|logs|clean|setup}"
        echo ""
        echo "Commands:"
        echo "  start    - Start all services (PostgreSQL + MinIO)"
        echo "  stop     - Stop all services"
        echo "  restart  - Restart all services"
        echo "  status   - Show service status and URLs"
        echo "  logs     - Show logs (add service name for specific service)"
        echo "  clean    - Stop services and remove volumes (DESTRUCTIVE)"
        echo "  setup    - Setup MinIO bucket after first start"
        echo ""
        echo "Examples:"
        echo "  $0 start"
        echo "  $0 logs postgres"
        echo "  $0 logs minio"
        echo ""
        exit 1
        ;;
esac
