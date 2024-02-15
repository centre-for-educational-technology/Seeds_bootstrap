"""
WSGI config for seeds_bootstrap project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
import sys

sys.path.append('/home/Seeds_bootstrap')
sys.path.append('/home/Seeds_bootstrap/seeds_bootstrap')


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'seeds_bootstrap.settings')

application = get_wsgi_application()
