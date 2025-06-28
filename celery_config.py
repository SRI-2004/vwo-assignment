from celery import Celery

# Configure Celery
celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=["worker"]  # Point to the file where tasks are defined
)

celery_app.conf.update(
    task_track_started=True,
) 