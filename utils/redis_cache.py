import redis
import os

redis_client = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379, db=0)

def get_cached_response(key):
    return redis_client.get(key)

def set_cached_response(key, value, ttl=300):
    redis_client.set(key, value, ex=ttl)
