"""
WSGI config for movies project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

APPLICATION_ENVIRONMENT = os.environ.get('APPLICATION_ENVIRONMENT')

if APPLICATION_ENVIRONMENT == 'prod':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movies.settings.settings_prod')
elif APPLICATION_ENVIRONMENT == 'test':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movies.settings.settings_test')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movies.settings.settings_dev')

application = get_wsgi_application()
