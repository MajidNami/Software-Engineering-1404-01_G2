"""
WSGI config for Team 8 backend

This is a standalone WSGI configuration that can run independently
or integrate with the main project.
"""
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
