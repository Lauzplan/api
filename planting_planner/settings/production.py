from .defaults import *
# Read SECRET_KEY from an environment variable

import os

# SECRET_KEY = os.environ['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'planting_planner_db',
        'USER': 'student',
        'PASSWORD': 'azerty',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    },
}

CORS_ALLOWED_ORIGINS = [
    "https://tfe-moffarts.info.ucl.ac.be",
    "http://localhost:3000",
]

ALLOWED_HOSTS = ['tfe-moffarts.info.ucl.ac.be', 'localhost:3000']

