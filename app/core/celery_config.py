import os
from celery import Celery
from dotenv import load_dotenv
import tensorflow as tf
# Load environment variables from a .env file if present
load_dotenv()

broker = os.getenv("REDIS_BROKER_URL", "redis://localhost:6379/0")
backend = os.getenv("REDIS_BACKEND_URL", "redis://localhost:6379/0")
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow logs
os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'
tf.config.set_soft_device_placement(True)

celery_app = Celery(
    "tasks",
    broker=broker,
    backend=backend,
)

celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
)


celery_app.autodiscover_tasks(['app.pipeline.smiles_prediction'])