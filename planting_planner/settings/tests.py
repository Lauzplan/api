from .dev import *

# Speed up tests by using sqlite engine
DATABASES['default']['ENGINE'] = 'django.db.backends.postgis'

