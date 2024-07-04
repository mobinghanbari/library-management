import redis.asyncio as aioredis
import os
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_DB = os.getenv("REDIS_DB")




redis_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

redis_client = aioredis.from_url(redis_url)
