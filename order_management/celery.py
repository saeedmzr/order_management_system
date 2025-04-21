import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'order_management.settings.local')

app = Celery('order_management')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
