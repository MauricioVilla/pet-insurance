import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('pet_insurance')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'activate-approved-pets-daily': {
        'task': 'apps.pets.tasks.activate_approved_pets',
        'schedule': crontab(hour=0, minute=5),
    },
}
