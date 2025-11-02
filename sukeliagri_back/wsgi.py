"""
WSGI config for sukeliagri_back project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from pathlib import Path
from django.core.wsgi import get_wsgi_application
from dotenv import load_dotenv

# Add the project directory to the Python path
path = Path(__file__).resolve().parent.parent
sys.path.append(str(path))

# Load environment variables from .env
env_path = path / '.env'
load_dotenv(dotenv_path=env_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sukeliagri_back.settings')

application = get_wsgi_application()
