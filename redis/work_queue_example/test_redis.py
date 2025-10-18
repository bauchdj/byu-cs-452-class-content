import settings
import redis


def test_redis_connection():
    try:
        # Connect to Redis server
        db = redis.StrictRedis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB,
        )

        # Test connection
        db.ping()
        print("Redis connection successful!")

        # Test setting and getting a value
        db.set("test_key", "test_value")
        value = db.get("test_key").decode("utf-8")
        print(f"Test value retrieved: {value}")

        # Clean up
        db.delete("test_key")

    except Exception as e:
        print(f"Redis connection failed: {e}")


if __name__ == "__main__":
    test_redis_connection()
