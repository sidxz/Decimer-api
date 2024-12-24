import os
from celery import Celery
from dotenv import load_dotenv
import tensorflow as tf
from app.core.logging_config import logger
from app.hooks.registry import load_hooks_from_directory
import redis

# Load environment variables from a .env file if present
load_dotenv()

# Fetch broker and backend URLs
broker = os.getenv("REDIS_BROKER_URL", "redis://localhost:6379/0")
backend = os.getenv("REDIS_BACKEND_URL", "redis://localhost:6379/0")

# Validate Redis connection
try:
    redis_connection = redis.Redis.from_url(broker)
    redis_connection.ping()
    logger.info("Redis broker is reachable.")
except Exception as e:
    logger.error(f"Could not connect to Redis broker: {e}")
    raise ValueError("Invalid Redis configuration or Redis is unreachable.")

# Log broker and backend URLs
logger.info(f"Broker URL: {broker}")
logger.info(f"Backend URL: {backend}")

# TensorFlow configuration
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow logs
os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'
tf.config.set_soft_device_placement(True)

# Log TensorFlow GPU availability
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    logger.info(f"Available GPUs: {[gpu.name for gpu in gpus]}")
else:
    logger.warning("No GPUs detected. TensorFlow will use CPU.")

# Initialize Celery app
celery_app = Celery(
    "tasks",
    broker=broker,
    backend=backend,
)

# Update Celery configuration
celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
)

# Autodiscover tasks
try:
    celery_app.autodiscover_tasks(['app.pipeline.smiles_prediction'])
    logger.info("Tasks discovered successfully.")
except Exception as e:
    logger.error(f"Error discovering tasks: {e}")
    raise

# Load hooks for Celery workers
hooks_directory = os.path.join(os.path.dirname(__file__), "..", "hooks")
try:
    logger.info("Loading hooks for Celery workers...")
    load_hooks_from_directory(hooks_directory)
    logger.info("Hooks loaded successfully.")
except Exception as e:
    logger.error(f"Error loading hooks: {e}")
    raise
