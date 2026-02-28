from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mrcheeezz.settings')

app = Celery('mrcheeezz')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'check-current-game-status': {
        'task': 'mrcheeezz.tasks.check_current_game_status',
        'schedule': crontab(minute='*'),
    },
}
