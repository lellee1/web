# Django Homelab Homepage - Docker Deployment

This Docker setup provides a production-ready deployment of your Django homelab homepage with Nginx reverse proxy for the blackfiber.se domain.

## Quick Start

1. **Navigate to the Docker directory:**
   ```bash
   cd Docker
   ```

2. **Build and start the services:**
   ```bash
   docker-compose up -d --build
   ```

3. **Access your application:**
   - HTTP: http://blackfiber.se or http://www.blackfiber.se
   - HTTPS: https://blackfiber.se or https://www.blackfiber.se (after SSL setup)

## Configuration

### Environment Variables

Update the following in `docker-compose.yml`:

- `SECRET_KEY`: Change to a secure random string
- `POSTGRES_PASSWORD`: Set a secure database password
- `DEBUG`: Set to `False` for production

### SSL Configuration (Recommended for Production)

1. **Obtain SSL certificates** for blackfiber.se and www.blackfiber.se
2. **Create SSL directory:**
   ```bash
   mkdir ssl
   ```
3. **Place your certificates:**
   - `ssl/blackfiber.se.crt` (certificate file)
   - `ssl/blackfiber.se.key` (private key file)
4. **Uncomment SSL lines** in `docker-compose.yml` and `nginx.conf`

### Database

The setup includes PostgreSQL for production use. If you prefer SQLite (current setup), the database file will be persisted via Docker volume.

To switch to PostgreSQL:
1. Uncomment the PostgreSQL configuration in `app/homelab_homepage/settings.py`
2. Comment out the SQLite configuration

## Services

- **app**: Django application running on Gunicorn
- **nginx**: Nginx reverse proxy handling static files and SSL termination
- **db**: PostgreSQL database (optional, currently using SQLite)

## Volumes

- `static_volume`: Django static files
- `media_volume`: User-uploaded files
- `postgres_data`: Database data (if using PostgreSQL)

## Commands

### Start services:
```bash
docker-compose up -d
```

### Stop services:
```bash
docker-compose down
```

### View logs:
```bash
docker-compose logs -f app
docker-compose logs -f nginx
```

### Django management commands:
```bash
# Create superuser
docker-compose exec app python manage.py createsuperuser

# Run migrations
docker-compose exec app python manage.py migrate

# Collect static files
docker-compose exec app python manage.py collectstatic --noinput
```

### Backup database:
```bash
# SQLite
docker-compose exec app cp /app/db.sqlite3 /tmp/backup.sqlite3
docker cp $(docker-compose ps -q app):/tmp/backup.sqlite3 ./backup.sqlite3

# PostgreSQL
docker-compose exec db pg_dump -U django_user homelab_homepage > backup.sql
```

## Domain Configuration

Ensure your domain (blackfiber.se and www.blackfiber.se) points to your server's IP address:

```
blackfiber.se      A    YOUR_SERVER_IP
www.blackfiber.se  A    YOUR_SERVER_IP
```

## Security Notes

1. **Change default passwords** in `docker-compose.yml`
2. **Use HTTPS** in production with valid SSL certificates
3. **Keep Docker images updated** regularly
4. **Backup your data** regularly
5. **Monitor logs** for security issues

## Troubleshooting

### Check if containers are running:
```bash
docker-compose ps
```

### Access Django shell:
```bash
docker-compose exec app python manage.py shell
```

### Reset database (destructive):
```bash
docker-compose down -v
docker-compose up -d --build
```

## File Structure

```
Docker/
├── app/                    # Django application
│   ├── Dockerfile
│   ├── requirements.txt
│   └── (all Django files)
├── docker-compose.yml      # Main orchestration file
├── nginx.conf             # Nginx configuration
├── ssl/                   # SSL certificates (create manually)
│   ├── blackfiber.se.crt
│   └── blackfiber.se.key
└── README.md              # This file
```
