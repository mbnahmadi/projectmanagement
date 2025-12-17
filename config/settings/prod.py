from .base import *
import os

DEBUG = False

ALLOWED_HOSTS = [] 

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

BASE_ADDRESS_OF_PDFS_ON_SERVER = os.getenv('BASE_ADDRESS_OF_PDFS_ON_SERVER')

# -------------------- DATABASE -----------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT')
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

STATIC_ROOT = BASE_DIR / 'staticfiles/'
