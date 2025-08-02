# Use Python 3.13 slim image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=homelab_homepage.settings

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        gettext \
        build-essential \
        libpq-dev \
	python3-dev \
	gcc\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip \
	&& pip install --no-cache-dir psycopg2-binary \
	&& pip install --no-cache-dir -r requirements.txt \
	&& python -c "import psycopg2; print('✅ psycopg2 installed successfully')"


# Copy project
COPY . /app/

# Create static and media directories
RUN mkdir -p /app/staticfiles /app/media

# Create a script to handle startup tasks
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "Waiting for database..."\n\
sleep 10\n\
\n\
echo "Running migrations..."\n\
python manage.py migrate --noinput\n\
\n\
echo "Collecting static files..."\n\
python manage.py collectstatic --noinput\n\
\n\
echo "Creating superuser if it doesn'\''t exist..."\n\
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='\''admin'\'').exists() or User.objects.create_superuser('\''admin'\'', '\''admin@blackfiber.se'\'', '\''admin123'\'')"\n\
\n\
echo "Starting Gunicorn..."\n\
exec gunicorn --bind 0.0.0.0:8000 --workers 3 --timeout 120 homelab_homepage.wsgi:application' > /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

# Expose port
EXPOSE 8000

# Use the entrypoint script
CMD ["/app/entrypoint.sh"]
