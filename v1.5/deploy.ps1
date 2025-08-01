# Django Homelab Homepage Deployment Script for Windows PowerShell

param(
    [Parameter(Position=0)]
    [string]$Command = "build"
)

Write-Host "=== Django Homelab Homepage Deployment ===" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
try {
    docker info | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker and try again." -ForegroundColor Red
    exit 1
}

# Check if docker-compose is available
try {
    docker-compose --version | Out-Null
    Write-Host "✅ docker-compose is available" -ForegroundColor Green
} catch {
    Write-Host "❌ docker-compose is not installed. Please install it and try again." -ForegroundColor Red
    exit 1
}

Write-Host ""

function Show-Usage {
    Write-Host "Usage: .\deploy.ps1 [COMMAND]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Commands:" -ForegroundColor Yellow
    Write-Host "  start     - Start all services"
    Write-Host "  stop      - Stop all services"
    Write-Host "  restart   - Restart all services"
    Write-Host "  build     - Build and start services"
    Write-Host "  logs      - Show logs"
    Write-Host "  status    - Show service status"
    Write-Host "  backup    - Backup database"
    Write-Host "  shell     - Access Django shell"
    Write-Host "  superuser - Create Django superuser"
    Write-Host ""
}

switch ($Command.ToLower()) {
    "start" {
        Write-Host "🚀 Starting services..." -ForegroundColor Blue
        docker-compose up -d
        Write-Host "✅ Services started!" -ForegroundColor Green
    }
    "stop" {
        Write-Host "🛑 Stopping services..." -ForegroundColor Blue
        docker-compose down
        Write-Host "✅ Services stopped!" -ForegroundColor Green
    }
    "restart" {
        Write-Host "🔄 Restarting services..." -ForegroundColor Blue
        docker-compose down
        docker-compose up -d
        Write-Host "✅ Services restarted!" -ForegroundColor Green
    }
    "build" {
        Write-Host "🔨 Building and starting services..." -ForegroundColor Blue
        docker-compose down
        docker-compose up -d --build
        Write-Host ""
        Write-Host "✅ Deployment complete!" -ForegroundColor Green
        Write-Host ""
        Write-Host "🌐 Your website should be available at:" -ForegroundColor Cyan
        Write-Host "   - http://blackfiber.se"
        Write-Host "   - http://www.blackfiber.se"
        Write-Host ""
        Write-Host "🔐 Default admin credentials:" -ForegroundColor Yellow
        Write-Host "   Username: admin"
        Write-Host "   Password: admin123"
        Write-Host "   (Please change these in production!)" -ForegroundColor Red
    }
    "logs" {
        Write-Host "📋 Showing logs..." -ForegroundColor Blue
        docker-compose logs -f
    }
    "status" {
        Write-Host "📊 Service status:" -ForegroundColor Blue
        docker-compose ps
    }
    "backup" {
        Write-Host "💾 Creating database backup..." -ForegroundColor Blue
        if (!(Test-Path "backups")) {
            New-Item -ItemType Directory -Path "backups"
        }
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $containerId = (docker-compose ps -q app)
        docker-compose exec app cp /app/db.sqlite3 "/tmp/backup_$timestamp.sqlite3"
        docker cp "${containerId}:/tmp/backup_$timestamp.sqlite3" "./backups/"
        Write-Host "✅ Backup created: backups/backup_$timestamp.sqlite3" -ForegroundColor Green
    }
    "shell" {
        Write-Host "🐍 Accessing Django shell..." -ForegroundColor Blue
        docker-compose exec app python manage.py shell
    }
    "superuser" {
        Write-Host "👤 Creating Django superuser..." -ForegroundColor Blue
        docker-compose exec app python manage.py createsuperuser
    }
    { $_ -in "help", "-h", "--help" } {
        Show-Usage
    }
    default {
        Write-Host "❌ Unknown command: $Command" -ForegroundColor Red
        Write-Host ""
        Show-Usage
        exit 1
    }
}
