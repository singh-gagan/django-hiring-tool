import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hirebot.settings.local_settings")

app = Celery("hirebot")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
