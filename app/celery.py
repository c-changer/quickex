import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

app = Celery('app')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_schedule = {
    'crypto': {
        'task': 'crypto.tasks.kukoin_price',
        'schedule': 60.0,  # Run every 5 minutes
    },
}

app.autodiscover_tasks()

if __name__ == '__main__':
    app.start()