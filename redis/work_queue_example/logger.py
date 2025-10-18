import redis
import settings
import time
import json
import os

# Connect to Redis server for logging
log_db = redis.StrictRedis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    db=settings.REDIS_DB,
)

# Define the Redis key for the log list
LOG_QUEUE = "app_logs"
MAX_LOGS = 1000  # Keep only the most recent 1000 logs


def log_action(server_name, action):
    """
    Log an action with consistent formatting to Redis.

    Args:
        server_name (str): Name of the server (e.g., "web_server", "model_server")
        action (str): Description of the action being logged
    """
    # Get the main running Python script name
    script_name = os.path.basename(os.sys.argv[0])

    # Create log entry with consistent format
    log_entry = {
        "server_name": server_name,
        "script_name": script_name,
        "timestamp": time.time(),
        "timestamp_formatted": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        "action": action,
    }

    # Store the log entry in Redis as a list
    # Use LPUSH to add to the beginning of the list
    log_db.lpush(LOG_QUEUE, json.dumps(log_entry))

    # Trim the list to keep only the most recent MAX_LOGS entries
    log_db.ltrim(LOG_QUEUE, 0, MAX_LOGS - 1)

    # Also print to console for immediate visibility
    print(
        f"[{log_entry['timestamp_formatted']}] {server_name} ({script_name}): {action}"
    )


def get_recent_logs(count=10):
    """
    Retrieve recent log entries from Redis.

    Args:
        count (int): Number of recent logs to retrieve

    Returns:
        list: List of recent log entries
    """
    logs = log_db.lrange(LOG_QUEUE, 0, count - 1)
    return [json.loads(log.decode("utf-8")) for log in logs]
