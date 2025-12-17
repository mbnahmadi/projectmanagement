from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
# from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
# app.conf.update(
#     task_default_queue='celery',
# )

app.conf.beat_schedule = {
    'update_pdfs_every_12_hours': {
        'task': 'projectapp.tasks.update_active_projects_pdfs',
        # 'schedule': crontab(minute='*/2'),
        'schedule': crontab(minute=0, hour='5,17'),
        'args': ()
    }
}