"""
Metrics Collection Service
Handles real-time metrics collection and monitoring for voice agent system
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, field

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.call import Call, CallAnalytics
from app.models.tenant import Tenant

logger = logging.getLogger(__name__)


@dataclass
class MetricPoint:
    """Individual metric data point"""
    timestamp: datetime
    value: float
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class ServiceMetrics:
    """Service-level metrics"""
    response_times: deque = field(default_factory=lambda: deque(maxlen=1000))
    error_count: int = 0
    success_count: int = 0
    last_error_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None


class MetricsCollector:
    """Real-time metrics collection and monitoring service"""
    
    def __init__(self):
        # Service metrics
        self.service_metrics: Dict[str, ServiceMetrics] = defaultdict(ServiceMetrics)
        
        # Call metrics
        self.active_calls: Dict[str, Dict[str, Any]] = {}
        self.call_metrics: deque = deque(maxlen=10000)  # Last 10k calls
        
        # System metrics
        self.system_metrics: Dict[str, deque] = {
            "cpu_usage": deque(maxlen=100),
            "memory_usage": deque(maxlen=100),
            "active_connections": deque(maxlen=100),
            "response_times": deque(maxlen=1000)
        }
        
        # Performance thresholds
        self.thresholds = {
            "response_time_ms": 5000,  # 5 seconds
            "error_rate_percent": 5.0,  # 5%
            "active_calls_max": 50,
            "memory_usage_percent": 80.0
        }
        
        # Alerts
        self.alerts: List[Dict[str, Any]] = []
        self.alert_cooldown: Dict[str, datetime] = {}
        
        # Start background tasks
        self._start_background_tasks()
    
    def _start_background_tasks(self):
        """Start background metric collection tasks"""
        asyncio.create_task(self._collect_system_metrics())
        asyncio.create_task(self._cleanup_old_metrics())
    
    async def record_api_call(
        self, 
        service: str, 
        endpoint: str, 
        duration_ms: float, 
        success: bool,
        error_type: Optional[str] = None
    ):
        """Record API call metrics"""
        
        try:
            service_key = f"{service}_{endpoint}"
            metrics = self.service_metrics[service_key]
            
            # Record response time
            metrics.response_times.append(duration_ms)
            
            # Record success/error
            if success:
                metrics.success_count += 1
                metrics.last_success_time = datetime.utcnow()
            else:
                metrics.error_count += 1
                metrics.last_error_time = datetime.utcnow()
            
            # Check for alerts
            await self._check_service_alerts(service_key, metrics)
            
            logger.debug(f"Recorded {service_key}: {duration_ms}ms, success={success}")
            
        except Exception as e:
            logger.error(f"Error recording API call metrics: {e}")
    
    async def start_call_tracking(self, call_id: str, caller_number: str, tenant_id: str):
        """Start tracking metrics for a new call"""
        
        try:
            self.active_calls[call_id] = {
                "start_time": datetime.utcnow(),
                "caller_number": caller_number,
                "tenant_id": tenant_id,
                "turn_count": 0,
                "total_response_time": 0.0,
                "interruptions": 0,
                "errors": 0,
                "ai_speaking_time": 0.0,
                "caller_speaking_time": 0.0,
                "silence_periods": 0
            }
            
            logger.info(f"Started call tracking for {call_id}")
            
        except Exception as e:
            logger.error(f"Error starting call tracking: {e}")
    
    async def record_conversation_turn(
        self, 
        call_id: str, 
        response_time_ms: float,
        ai_response_length: int,
        user_input_length: int,
        interrupted: bool = False
    ):
        """Record conversation turn metrics"""
        
        try:
            if call_id not in self.active_calls:
                logger.warning(f"Call {call_id} not found in active calls")
                return
            
            call_metrics = self.active_calls[call_id]
            call_metrics["turn_count"] += 1
            call_metrics["total_response_time"] += response_time_ms
            
            if interrupted:
                call_metrics["interruptions"] += 1
            
            # Estimate speaking times (rough calculation)
            # Assume ~150 words per minute speaking rate
            ai_speaking_time = (ai_response_length / 5) / 150 * 60  # seconds
            caller_speaking_time = (user_input_length / 5) / 150 * 60  # seconds
            
            call_metrics["ai_speaking_time"] += ai_speaking_time
            call_metrics["caller_speaking_time"] += caller_speaking_time
            
            logger.debug(f"Recorded turn for {call_id}: {response_time_ms}ms")
            
        except Exception as e:
            logger.error(f"Error recording conversation turn: {e}")
    
    async def record_call_error(self, call_id: str, error_type: str, error_message: str):
        """Record call error"""
        
        try:
            if call_id in self.active_calls:
                self.active_calls[call_id]["errors"] += 1
            
            # Record system-wide error
            await self.record_api_call("voice_agent", "conversation", 0, False, error_type)
            
            logger.warning(f"Recorded error for {call_id}: {error_type}")
            
        except Exception as e:
            logger.error(f"Error recording call error: {e}")
    
    async def end_call_tracking(self, call_id: str, db: AsyncSession):
        """End call tracking and save metrics to database"""
        
        try:
            if call_id not in self.active_calls:
                logger.warning(f"Call {call_id} not found in active calls")
                return
            
            call_metrics = self.active_calls[call_id]
            end_time = datetime.utcnow()
            duration = (end_time - call_metrics["start_time"]).total_seconds()
            
            # Calculate quality metrics
            avg_response_time = (
                call_metrics["total_response_time"] / call_metrics["turn_count"]
                if call_metrics["turn_count"] > 0 else 0
            )
            
            talk_time_ratio = (
                call_metrics["caller_speaking_time"] / 
                (call_metrics["caller_speaking_time"] + call_metrics["ai_speaking_time"])
                if (call_metrics["caller_speaking_time"] + call_metrics["ai_speaking_time"]) > 0
                else 0.5
            )
            
            # Save to database
            await self._save_call_analytics(call_id, call_metrics, avg_response_time, talk_time_ratio, db)
            
            # Add to historical metrics
            self.call_metrics.append({
                "call_id": call_id,
                "duration": duration,
                "turn_count": call_metrics["turn_count"],
                "avg_response_time": avg_response_time,
                "interruptions": call_metrics["interruptions"],
                "errors": call_metrics["errors"],
                "talk_time_ratio": talk_time_ratio,
                "end_time": end_time
            })
            
            # Remove from active calls
            del self.active_calls[call_id]
            
            logger.info(f"Ended call tracking for {call_id}")
            
        except Exception as e:
            logger.error(f"Error ending call tracking: {e}")
    
    async def _save_call_analytics(
        self, 
        call_id: str, 
        call_metrics: Dict, 
        avg_response_time: float,
        talk_time_ratio: float,
        db: AsyncSession
    ):
        """Save call analytics to database"""
        
        try:
            # Check if analytics already exist
            stmt = select(CallAnalytics).where(CallAnalytics.call_id == call_id)
            result = await db.execute(stmt)
            analytics = result.scalar_one_or_none()
            
            if not analytics:
                analytics = CallAnalytics(call_id=call_id)
                db.add(analytics)
            
            # Update analytics
            analytics.agent_response_time_avg = avg_response_time / 1000  # Convert to seconds
            analytics.interruptions_count = call_metrics["interruptions"]
            analytics.talk_time_ratio = talk_time_ratio
            analytics.agent_talk_time_seconds = call_metrics["ai_speaking_time"]
            analytics.customer_talk_time_seconds = call_metrics["caller_speaking_time"]
            
            # Calculate quality scores
            analytics.conversation_quality_score = self._calculate_conversation_quality(call_metrics)
            analytics.agent_performance_score = self._calculate_agent_performance(avg_response_time, call_metrics["errors"])
            
            analytics.analyzed_at = datetime.utcnow()
            
            await db.commit()
            
        except Exception as e:
            logger.error(f"Error saving call analytics: {e}")
    
    def _calculate_conversation_quality(self, call_metrics: Dict) -> float:
        """Calculate conversation quality score (0.0 to 1.0)"""
        
        try:
            score = 1.0
            
            # Penalize for interruptions
            if call_metrics["turn_count"] > 0:
                interruption_rate = call_metrics["interruptions"] / call_metrics["turn_count"]
                score -= min(interruption_rate * 0.3, 0.3)
            
            # Penalize for errors
            if call_metrics["errors"] > 0:
                score -= min(call_metrics["errors"] * 0.1, 0.4)
            
            # Penalize for very short or very long calls
            duration = (datetime.utcnow() - call_metrics.get("start_time", datetime.utcnow())).total_seconds()
            if duration < 30:  # Very short call
                score -= 0.2
            elif duration > 1800:  # Very long call (30 minutes)
                score -= 0.1
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            logger.error(f"Error calculating conversation quality: {e}")
            return 0.5
    
    def _calculate_agent_performance(self, avg_response_time: float, error_count: int) -> float:
        """Calculate agent performance score (0.0 to 1.0)"""
        
        try:
            score = 1.0
            
            # Penalize for slow response times
            if avg_response_time > 3000:  # 3 seconds
                score -= min((avg_response_time - 3000) / 10000, 0.4)
            
            # Penalize for errors
            score -= min(error_count * 0.15, 0.5)
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            logger.error(f"Error calculating agent performance: {e}")
            return 0.5
    
    async def _collect_system_metrics(self):
        """Background task to collect system metrics"""
        
        while True:
            try:
                # Collect basic system metrics
                current_time = datetime.utcnow()
                
                # Active connections count
                active_connections = len(self.active_calls)
                self.system_metrics["active_connections"].append(
                    MetricPoint(current_time, active_connections)
                )
                
                # Check for system alerts
                await self._check_system_alerts()
                
                # Sleep for 30 seconds
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Error collecting system metrics: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _check_service_alerts(self, service_key: str, metrics: ServiceMetrics):
        """Check for service-level alerts"""
        
        try:
            # Check response time
            if metrics.response_times:
                avg_response_time = sum(metrics.response_times) / len(metrics.response_times)
                if avg_response_time > self.thresholds["response_time_ms"]:
                    await self._create_alert(
                        "high_response_time",
                        f"High response time for {service_key}: {avg_response_time:.0f}ms",
                        "warning"
                    )
            
            # Check error rate
            total_requests = metrics.success_count + metrics.error_count
            if total_requests > 10:  # Only check if we have enough data
                error_rate = (metrics.error_count / total_requests) * 100
                if error_rate > self.thresholds["error_rate_percent"]:
                    await self._create_alert(
                        "high_error_rate",
                        f"High error rate for {service_key}: {error_rate:.1f}%",
                        "critical"
                    )
            
        except Exception as e:
            logger.error(f"Error checking service alerts: {e}")
    
    async def _check_system_alerts(self):
        """Check for system-level alerts"""
        
        try:
            # Check active calls
            active_calls = len(self.active_calls)
            if active_calls > self.thresholds["active_calls_max"]:
                await self._create_alert(
                    "high_active_calls",
                    f"High number of active calls: {active_calls}",
                    "warning"
                )
            
        except Exception as e:
            logger.error(f"Error checking system alerts: {e}")
    
    async def _create_alert(self, alert_type: str, message: str, severity: str):
        """Create an alert with cooldown"""
        
        try:
            # Check cooldown
            cooldown_key = f"{alert_type}_{severity}"
            if cooldown_key in self.alert_cooldown:
                time_since_last = datetime.utcnow() - self.alert_cooldown[cooldown_key]
                if time_since_last < timedelta(minutes=15):  # 15-minute cooldown
                    return
            
            # Create alert
            alert = {
                "type": alert_type,
                "message": message,
                "severity": severity,
                "timestamp": datetime.utcnow(),
                "resolved": False
            }
            
            self.alerts.append(alert)
            self.alert_cooldown[cooldown_key] = datetime.utcnow()
            
            logger.warning(f"Alert created: {alert_type} - {message}")
            
            # Keep only last 100 alerts
            if len(self.alerts) > 100:
                self.alerts = self.alerts[-100:]
            
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
    
    async def _cleanup_old_metrics(self):
        """Background task to clean up old metrics"""
        
        while True:
            try:
                # Clean up old call metrics (keep last 24 hours)
                cutoff_time = datetime.utcnow() - timedelta(hours=24)
                
                # Clean call metrics
                self.call_metrics = deque([
                    metric for metric in self.call_metrics
                    if metric.get("end_time", datetime.utcnow()) > cutoff_time
                ], maxlen=10000)
                
                # Clean system metrics
                for metric_name, metric_deque in self.system_metrics.items():
                    # Keep only recent metrics
                    while metric_deque and metric_deque[0].timestamp < cutoff_time:
                        metric_deque.popleft()
                
                # Clean old alerts
                self.alerts = [
                    alert for alert in self.alerts
                    if alert["timestamp"] > cutoff_time
                ]
                
                logger.debug("Cleaned up old metrics")
                
                # Sleep for 1 hour
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"Error cleaning up metrics: {e}")
                await asyncio.sleep(3600)
    
    def get_service_metrics(self, service: str) -> Dict[str, Any]:
        """Get metrics for a specific service"""
        
        try:
            service_keys = [key for key in self.service_metrics.keys() if key.startswith(service)]
            
            if not service_keys:
                return {}
            
            combined_metrics = {
                "total_requests": 0,
                "total_errors": 0,
                "avg_response_time": 0,
                "error_rate": 0,
                "last_error": None,
                "last_success": None
            }
            
            total_response_times = []
            
            for key in service_keys:
                metrics = self.service_metrics[key]
                combined_metrics["total_requests"] += metrics.success_count + metrics.error_count
                combined_metrics["total_errors"] += metrics.error_count
                
                if metrics.response_times:
                    total_response_times.extend(metrics.response_times)
                
                if metrics.last_error_time:
                    if not combined_metrics["last_error"] or metrics.last_error_time > combined_metrics["last_error"]:
                        combined_metrics["last_error"] = metrics.last_error_time
                
                if metrics.last_success_time:
                    if not combined_metrics["last_success"] or metrics.last_success_time > combined_metrics["last_success"]:
                        combined_metrics["last_success"] = metrics.last_success_time
            
            # Calculate averages
            if total_response_times:
                combined_metrics["avg_response_time"] = sum(total_response_times) / len(total_response_times)
            
            if combined_metrics["total_requests"] > 0:
                combined_metrics["error_rate"] = (combined_metrics["total_errors"] / combined_metrics["total_requests"]) * 100
            
            return combined_metrics
            
        except Exception as e:
            logger.error(f"Error getting service metrics: {e}")
            return {}
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status and metrics"""
        
        try:
            return {
                "active_calls": len(self.active_calls),
                "total_calls_today": len([
                    call for call in self.call_metrics
                    if call["end_time"] > datetime.utcnow() - timedelta(days=1)
                ]),
                "avg_response_time_ms": self._get_avg_response_time(),
                "error_rate_percent": self._get_error_rate(),
                "alerts_count": len([alert for alert in self.alerts if not alert["resolved"]]),
                "services": {
                    "openai": self.get_service_metrics("openai"),
                    "elevenlabs": self.get_service_metrics("elevenlabs"),
                    "twilio": self.get_service_metrics("twilio")
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {}
    
    def _get_avg_response_time(self) -> float:
        """Get average response time across all services"""
        
        try:
            all_response_times = []
            for metrics in self.service_metrics.values():
                if metrics.response_times:
                    all_response_times.extend(metrics.response_times)
            
            return sum(all_response_times) / len(all_response_times) if all_response_times else 0
            
        except Exception as e:
            logger.error(f"Error calculating average response time: {e}")
            return 0
    
    def _get_error_rate(self) -> float:
        """Get overall error rate across all services"""
        
        try:
            total_requests = 0
            total_errors = 0
            
            for metrics in self.service_metrics.values():
                total_requests += metrics.success_count + metrics.error_count
                total_errors += metrics.error_count
            
            return (total_errors / total_requests * 100) if total_requests > 0 else 0
            
        except Exception as e:
            logger.error(f"Error calculating error rate: {e}")
            return 0


# Global metrics collector instance
metrics_collector = MetricsCollector()