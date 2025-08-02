#!/bin/bash

# Django Homelab Homepage Deployment Script

set -e

echo "=== Django Homelab Homepage Deployment ==="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install it and try again."
    exit 1
fi

echo "✅ Docker is running"
echo "✅ docker-compose is available"
echo ""

# Function to show usage
show_usage() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start     - Start all services"
    echo "  stop      - Stop all services"
    echo "  restart   - Restart all services"
    echo "  build     - Build and start services"
    echo "  logs      - Show logs"
    echo "  status    - Show service status"
    echo "  backup    - Backup database"
    echo "  shell     - Access Django shell"
    echo "  superuser - Create Django superuser"
    echo ""
}

# Handle commands
case "${1:-build}" in
    "start")
        echo "🚀 Starting services..."
        docker-compose up -d
        echo "✅ Services started!"
        ;;
    "stop")
        echo "🛑 Stopping services..."
        docker-compose down
        echo "✅ Services stopped!"
        ;;
    "restart")
        echo "🔄 Restarting services..."
        docker-compose down
        docker-compose up -d
        echo "✅ Services restarted!"
        ;;
    "build")
        echo "🔨 Building and starting services..."
        docker-compose down
        docker-compose up -d --build
        echo ""
        echo "✅ Deployment complete!"
        echo ""
        echo "🌐 Your website should be available at:"
        echo "   - http://blackfiber.se"
        echo "   - http://www.blackfiber.se"
        echo ""
        echo "🔐 Default admin credentials:"
        echo "   Username: admin"
        echo "   Password: admin123"
        echo "   (Please change these in production!)"
        ;;
    "logs")
        echo "📋 Showing logs..."
        docker-compose logs -f
        ;;
    "status")
        echo "📊 Service status:"
        docker-compose ps
        ;;
    "backup")
        echo "💾 Creating database backup..."
        mkdir -p backups
        timestamp=$(date +%Y%m%d_%H%M%S)
        docker-compose exec app cp /app/db.sqlite3 /tmp/backup_${timestamp}.sqlite3
        docker cp $(docker-compose ps -q app):/tmp/backup_${timestamp}.sqlite3 ./backups/
        echo "✅ Backup created: backups/backup_${timestamp}.sqlite3"
        ;;
    "shell")
        echo "🐍 Accessing Django shell..."
        docker-compose exec app python manage.py shell
        ;;
    "superuser")
        echo "👤 Creating Django superuser..."
        docker-compose exec app python manage.py createsuperuser
        ;;
    "help"|"-h"|"--help")
        show_usage
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo ""
        show_usage
        exit 1
        ;;
esac
