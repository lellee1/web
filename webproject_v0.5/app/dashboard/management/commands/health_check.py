#!/usr/bin/env python
"""
Health check script for Django application
"""
import os
import sys
import requests
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Health check for the Django application'
    
    def handle(self, *args, **options):
        try:
            # Check if Django can start
            from django.core.management import execute_from_command_line
            
            # Check database connection
            from django.db import connection
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            
            # Check if static files are accessible
            static_root = getattr(settings, 'STATIC_ROOT', None)
            if static_root and os.path.exists(static_root):
                self.stdout.write(self.style.SUCCESS('✅ Static files directory exists'))
            
            # Check if media files directory exists
            media_root = getattr(settings, 'MEDIA_ROOT', None)
            if media_root and os.path.exists(media_root):
                self.stdout.write(self.style.SUCCESS('✅ Media files directory exists'))
            
            self.stdout.write(self.style.SUCCESS('✅ Django application is healthy'))
            return
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Health check failed: {e}'))
            sys.exit(1)


if __name__ == '__main__':
    # Simple health check when run directly
    try:
        import django
        from django.conf import settings
        
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homelab_homepage.settings')
        django.setup()
        
        # Check database
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        
        print("✅ Health check passed")
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        sys.exit(1)
