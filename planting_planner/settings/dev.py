from .defaults import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

GDAL_LIBRARY_PATH = "/Applications/Postgres.app/Contents/Versions/13/lib/libgdal.dylib"
GEOS_LIBRARY_PATH = "/Applications/Postgres.app/Contents/Versions/13/lib/libgeos_c.dylib"

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'planting_planner_db',
        'USER': 'postgres',
        'PASSWORD': 'azerty',
        'HOST': '127.0.0.1',
        'PORT': '5432'
    }
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8080"
]

ALLOWED_HOSTS = [
    "10.0.2.2",
    "127.0.0.1",
    "localhost"
]
