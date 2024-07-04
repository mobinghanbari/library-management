from cache.connection import redis_client

async def is_banned(ip: str):
    return await redis_client.get(f"blacklist_{ip}") or await redis_client.get(f"temp_blacklist_{ip}")

async def temporary_blacklist_ip(ip: str):
    await redis_client.set(f"temp_blacklist_{ip}", "0", ex=60)  # 1 minute

async def permanent_blacklist_ip(ip: str):
    await redis_client.set(f"blacklist_{ip}", "0", ex=300)  # 5 minutes
