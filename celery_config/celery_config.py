from celery import Celery

app = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

app.conf.update(
    result_expires=3600,
    beat_schedule={
        'save-daily-report': {
            'task': 'tasks.save_report_to_csv',
            'schedule': 86400.0,  # every 24 hours
        },
    }
)

