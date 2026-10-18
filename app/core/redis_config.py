import os
import redis.asyncio as redis
from dotenv import load_dotenv


load_dotenv()


REDIS_URL=os.getenv("REDIS_UPSTASH_URL")

# print("REDIS_URL:", repr(REDIS_URL[:20]) if REDIS_URL else None)
# print("TYPE:", type(REDIS_URL))
if REDIS_URL is None:
    raise RuntimeError("UPSTASH_URL is not configured")

redis_client = redis.from_url(REDIS_URL,
                            decode_responses=True,
                            socket_timeout=None,          # don't time out while blocking on an empty queue
                            socket_connect_timeout=10,
                            socket_keepalive=True,
                            health_check_interval=30)