import os
import sys

# Get the absolute path of the current file
current_file_path = os.path.abspath(__file__)
# Get the directory path of the current file
current_dir_path = os.path.dirname(current_file_path)
# Get the parent directory path
parent_dir_path = os.path.dirname(current_dir_path)
# Add the parent directory path to the sys.path
sys.path.insert(0, parent_dir_path)

import redis
from dotenv import load_dotenv
from backend.log import logger

# Load environment variables from .env file
load_dotenv()

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"), port=os.getenv("REDIS_PORT", 6379), db=0
)


def get_cached_response(key):
    """
    Retrieve a cached response from Redis.

    Args:
        key (str): The key for the cached response.

    Returns:
        str: The cached response if it exists, otherwise None.
    """
    logger.info(f"Fetching cached response for key: {key}")
    return redis_client.get(key)


def set_cached_response(key, value, ttl=300):
    """
    Set a response in the Redis cache.

    Args:
        key (str): The key for the cached response.
        value (str): The response to cache.
        ttl (int): Time-to-live for the cache in seconds. Default is 300 seconds.
    """
    logger.info(f"Setting cached response for key: {key} with TTL: {ttl}")
    redis_client.set(key, value, ex=ttl)
