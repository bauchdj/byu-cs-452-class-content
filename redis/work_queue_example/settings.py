# load env
import os
from dotenv import load_dotenv
import redis

load_dotenv()


def enable_redis_notifications(host, port, password=None):
    """Enable Redis keyspace notifications for pub/sub functionality"""
    try:
        # Connect to Redis
        db = redis.StrictRedis(host=host, port=port, password=password, db=0)
        # Enable keyspace notifications for all events
        db.config_set("notify-keyspace-events", "KEA")
        print("Redis keyspace notifications enabled successfully.")
        return True
    except Exception as e:
        print(f"Failed to enable Redis keyspace notifications: {e}")
        return False


# initialize Redis connection settings
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
REDIS_DB = 0

# initialize constants used to control image spatial dimensions and
# data type
IMAGE_WIDTH = 224
IMAGE_HEIGHT = 224
IMAGE_CHANS = 3
IMAGE_DTYPE = "float32"

# initialize constants used for server queuing
IMAGE_QUEUE = "image_queue"
BATCH_SIZE = 32
SERVER_TIMEOUT = 30
SERVER_SLEEP = 0.25
CLIENT_SLEEP = 0.25
