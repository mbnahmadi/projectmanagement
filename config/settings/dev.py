import os
from .base import *
from decouple import config, Csv

DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = config('SECRET_KEY')
SECRET_KEY = config('SECRET_KEY')


ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv()) 

# BASE_ADDRESS_OF_PDFS_ON_SERVER = config('BASE_ADDRESS_OF_PDFS_ON_SERVER')
BASE_ADDRESS_OF_PDFS_ON_SERVER = config('BASE_ADDRESS_OF_PDFS_ON_SERVER')

# -------------------- DATABASE -----------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT')
    }
}
# -----------------------------------------------------

# ------------ celery ---------------------------------
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_RESULT_BACKEND = 'django-db'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Tehran'
CELERY_ENABLE_UTC = False
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_IMPORTS = (
    'projectapp.tasks',
)
# -------------------------------------------------------

# --------------------- cache --------------------------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
    }
}

# ----------------------------- LOGGING ---------------------------

STATICFILES_DIRS = [
    BASE_DIR / "static/",
]
