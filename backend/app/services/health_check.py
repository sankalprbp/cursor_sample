"""
Health Check Service
Provides system health monitoring and status checks
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import redis.asyncio as redis

from app.core.config import settings
from app.core.database import get_db


logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Service status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class HealthCheckService:
    """Service for monitoring system health and status"""
    
    def __init__(self):
        self._redis_client: Optional[redis.Redis] = None
        self._last_check_time: Optional[datetime] = None
        self._cached_status: Optional[Dict[str, Any]] = None
        self._cache_duration_seconds = 30  # Cache status for 30 seconds
    
    async def get_system_status(self, db: Optional[AsyncSession] = None) -> Dict[str, Any]:
        """Get comprehensive system status"""
        
        # Check if we have a recent cached status
        if (self._cached_status and self._last_check_time and 
            (datetime.utcnow() - self._last_check_time).total_seconds() < self._cache_duration_seconds):
            return self._cached_status
        
        # Perform health checks
        database_status = await self._check_database_health(db)
        redis_status = await self._check_redis_health()
        
        # Determine overall system status
        overall_status = self._determine_overall_status(database_status, redis_status)
        
        # Build status response
        status_response = {
            "status": overall_status.value,
            "services": {
                "database": database_status.value,
                "redis": redis_status.value,
                "backend": ServiceStatus.HEALTHY.value  # Backend is running if we can execute this
            },
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "checks_performed": {
                "database": True,
                "redis": True,
                "backend": True
            }
        }
        
        # Cache the result
        self._cached_status = status_response
        self._last_check_time = datetime.utcnow()
        
        return status_response
    
    async def _check_database_health(self, db: Optional[AsyncSession] = None) -> ServiceStatus:
        """Check database connectivity and health"""
        try:
            # Use provided session or get a new one
            if db:
                session = db
                should_close = False
            else:
                session = next(get_db())
                should_close = True
            
            try:
                # Simple query to test database connectivity
                result = await session.execute(text("SELECT 1"))
                result.scalar()
                
                logger.debug("Database health check passed")
                return ServiceStatus.HEALTHY
                
            finally:
                if should_close:
                    await session.close()
                    
        except Exception as e:
            logger.warning(f"Database health check failed: {e}")
            return ServiceStatus.UNHEALTHY
    
    async def _check_redis_health(self) -> ServiceStatus:
        """Check Redis connectivity and health"""
        try:
            # Create Redis client if not exists
            if not self._redis_client:
                self._redis_client = redis.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True
                )
            
            # Test Redis connectivity with timeout
            await asyncio.wait_for(
                self._redis_client.ping(),
                timeout=5.0
            )
            
            logger.debug("Redis health check passed")
            return ServiceStatus.HEALTHY
            
        except asyncio.TimeoutError:
            logger.warning("Redis health check timed out")
            return ServiceStatus.DEGRADED
        except Exception as e:
            logger.warning(f"Redis health check failed: {e}")
            return ServiceStatus.UNHEALTHY
    
    def _determine_overall_status(self, database_status: ServiceStatus, redis_status: ServiceStatus) -> ServiceStatus:
        """Determine overall system status based on individual service statuses"""
        
        # If any critical service is unhealthy, system is unhealthy
        if database_status == ServiceStatus.UNHEALTHY:
            return ServiceStatus.UNHEALTHY
        
        # If Redis is unhealthy but database is ok, system is degraded
        if redis_status == ServiceStatus.UNHEALTHY:
            return ServiceStatus.DEGRADED
        
        # If any service is degraded, system is degraded
        if database_status == ServiceStatus.DEGRADED or redis_status == ServiceStatus.DEGRADED:
            return ServiceStatus.DEGRADED
        
        # If all services are healthy, system is healthy
        return ServiceStatus.HEALTHY
    
    async def get_detailed_health_info(self, db: Optional[AsyncSession] = None) -> Dict[str, Any]:
        """Get detailed health information including metrics"""
        
        basic_status = await self.get_system_status(db)
        
        # Add additional health metrics
        detailed_info = {
            **basic_status,
            "details": {
                "uptime_seconds": self._get_uptime_seconds(),
                "memory_usage": await self._get_memory_usage(),
                "active_connections": await self._get_active_connections(),
                "last_check": self._last_check_time.isoformat() + "Z" if self._last_check_time else None
            }
        }
        
        return detailed_info
    
    def _get_uptime_seconds(self) -> int:
        """Get approximate uptime in seconds (simplified implementation)"""
        # This is a simplified implementation
        # In production, you might track actual startup time
        return 3600  # Placeholder: 1 hour
    
    async def _get_memory_usage(self) -> Dict[str, Any]:
        """Get memory usage information"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                "rss_mb": round(memory_info.rss / 1024 / 1024, 2),
                "vms_mb": round(memory_info.vms / 1024 / 1024, 2),
                "percent": round(process.memory_percent(), 2)
            }
        except ImportError:
            return {"error": "psutil not available"}
        except Exception as e:
            logger.warning(f"Failed to get memory usage: {e}")
            return {"error": str(e)}
    
    async def _get_active_connections(self) -> Dict[str, int]:
        """Get active connection counts"""
        try:
            # This would need to be implemented based on your connection tracking
            # For now, return placeholder data
            return {
                "websocket_connections": 0,
                "active_calls": 0,
                "database_connections": 1
            }
        except Exception as e:
            logger.warning(f"Failed to get connection info: {e}")
            return {"error": str(e)}
    
    async def cleanup(self):
        """Cleanup resources"""
        if self._redis_client:
            await self._redis_client.close()
            self._redis_client = None


# Global instance
health_check_service = HealthCheckService()