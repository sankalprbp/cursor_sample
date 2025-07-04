"""
Redis Client Configuration
Handles caching, sessions, and real-time data
"""

import json
from typing import Any, Optional
import redis.asyncio as redis

from app.core.config import settings


class RedisClient:
    """Redis client wrapper with utility methods"""
    
    def __init__(self):
        self.redis = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
        )
    
    async def ping(self) -> bool:
        """Check Redis connection"""
        try:
            await self.redis.ping()
            return True
        except Exception:
            return False
    
    async def close(self):
        """Close Redis connection"""
        await self.redis.close()
    
    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Set a key-value pair with optional expiration"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            return await self.redis.set(key, value, ex=expire)
        except Exception:
            return False
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value by key"""
        try:
            value = await self.redis.get(key)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return None
        except Exception:
            return None
    
    async def delete(self, key: str) -> bool:
        """Delete a key"""
        try:
            return bool(await self.redis.delete(key))
        except Exception:
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            return bool(await self.redis.exists(key))
        except Exception:
            return False
    
    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment a counter"""
        try:
            return await self.redis.incrby(key, amount)
        except Exception:
            return None
    
    async def set_hash(self, key: str, mapping: dict, expire: Optional[int] = None) -> bool:
        """Set a hash with optional expiration"""
        try:
            await self.redis.hset(key, mapping=mapping)
            if expire:
                await self.redis.expire(key, expire)
            return True
        except Exception:
            return False
    
    async def get_hash(self, key: str) -> Optional[dict]:
        """Get hash value"""
        try:
            return await self.redis.hgetall(key)
        except Exception:
            return None
    
    async def add_to_set(self, key: str, value: str) -> bool:
        """Add value to set"""
        try:
            return bool(await self.redis.sadd(key, value))
        except Exception:
            return False
    
    async def remove_from_set(self, key: str, value: str) -> bool:
        """Remove value from set"""
        try:
            return bool(await self.redis.srem(key, value))
        except Exception:
            return False
    
    async def get_set_members(self, key: str) -> set:
        """Get all set members"""
        try:
            return await self.redis.smembers(key)
        except Exception:
            return set()
    
    async def publish(self, channel: str, message: Any) -> int:
        """Publish message to channel"""
        try:
            if isinstance(message, (dict, list)):
                message = json.dumps(message)
            return await self.redis.publish(channel, message)
        except Exception:
            return 0
    
    async def subscribe(self, *channels):
        """Subscribe to channels"""
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(*channels)
        return pubsub


# Create Redis client instance
redis_client = RedisClient()