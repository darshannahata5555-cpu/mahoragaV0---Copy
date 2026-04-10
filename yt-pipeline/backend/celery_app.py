import os

from celery import Celery
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

celery_app = Celery(
    "yt_pipeline",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery_app.conf.task_serializer = "json"
celery_app.conf.result_serializer = "json"
celery_app.conf.accept_content = ["json"]

# Import task modules so Celery registers them on worker startup
import app.workers.pipeline_worker  # noqa: E402, F401
