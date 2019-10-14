import dj_database_url
from django.core.exceptions import ImproperlyConfigured

from movies.settings import *

# general prod config
SECRET_KEY = os.environ.get('SECRET_KEY')

if SECRET_KEY is None:
    raise ImproperlyConfigured('SECRET_KEY setting must be set in environment variable for production.')

DEBUG = False

HOSTNAME = os.environ.get('HOSTNAME')
if HOSTNAME is None:
    raise ImproperlyConfigured('HOSTNAME environment variable must be set for production.')
else:
    ALLOWED_HOSTS = [HOSTNAME]


# DB Config
if "DATABASE_URL" not in os.environ:
    raise ImproperlyConfigured('DATABASE_URL environment variable needs to be set for production.')

DATABASES = {
    'default': dj_database_url.config(conn_max_age=600, ssl_require=True)
}
