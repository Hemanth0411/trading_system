# try:
#     import eventlet
#     eventlet.monkey_patch()
# except ImportError:
#     pass

import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
# This must come before creating the Celery application instance.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_system.settings')

# Create a Celery application instance
# 'trading_system' is the name of your Django project
app = Celery('trading_system')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix in settings.py.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
# Celery will look for a 'tasks.py' file in each app.
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')