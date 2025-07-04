"""
WebSocket Connection Manager
Handles real-time connections for call monitoring and updates
"""

import json
import logging
from typing import Dict, List, Set, Optional
from uuid import UUID

from fastapi import WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time features"""
    
    def __init__(self):
        # Active connections by connection ID
        self.active_connections: Dict[str, WebSocket] = {}
        
        # Connections grouped by tenant
        self.tenant_connections: Dict[str, Set[str]] = {}
        
        # Connections grouped by user
        self.user_connections: Dict[str, Set[str]] = {}
        
        # Call-specific connections (for live call monitoring)
        self.call_connections: Dict[str, Set[str]] = {}
        
        # Connection metadata
        self.connection_metadata: Dict[str, dict] = {}
    
    async def connect(
        self, 
        websocket: WebSocket, 
        connection_id: str,
        tenant_id: Optional[str] = None,
        user_id: Optional[str] = None,
        call_id: Optional[str] = None
    ):
        """Accept a new WebSocket connection"""
        try:
            await websocket.accept()
            
            # Store connection
            self.active_connections[connection_id] = websocket
            
            # Store metadata
            self.connection_metadata[connection_id] = {
                "tenant_id": tenant_id,
                "user_id": user_id,
                "call_id": call_id,
                "connected_at": websocket.client.host if websocket.client else None,
            }
            
            # Group by tenant
            if tenant_id:
                if tenant_id not in self.tenant_connections:
                    self.tenant_connections[tenant_id] = set()
                self.tenant_connections[tenant_id].add(connection_id)
            
            # Group by user
            if user_id:
                if user_id not in self.user_connections:
                    self.user_connections[user_id] = set()
                self.user_connections[user_id].add(connection_id)
            
            # Group by call
            if call_id:
                if call_id not in self.call_connections:
                    self.call_connections[call_id] = set()
                self.call_connections[call_id].add(connection_id)
            
            logger.info(f"WebSocket connection {connection_id} established")
            
        except Exception as e:
            logger.error(f"Failed to establish WebSocket connection {connection_id}: {e}")
            raise
    
    def disconnect(self, connection_id: str):
        """Remove a WebSocket connection"""
        try:
            # Get metadata before removal
            metadata = self.connection_metadata.get(connection_id, {})
            tenant_id = metadata.get("tenant_id")
            user_id = metadata.get("user_id")
            call_id = metadata.get("call_id")
            
            # Remove from active connections
            if connection_id in self.active_connections:
                del self.active_connections[connection_id]
            
            # Remove from metadata
            if connection_id in self.connection_metadata:
                del self.connection_metadata[connection_id]
            
            # Remove from tenant group
            if tenant_id and tenant_id in self.tenant_connections:
                self.tenant_connections[tenant_id].discard(connection_id)
                if not self.tenant_connections[tenant_id]:
                    del self.tenant_connections[tenant_id]
            
            # Remove from user group
            if user_id and user_id in self.user_connections:
                self.user_connections[user_id].discard(connection_id)
                if not self.user_connections[user_id]:
                    del self.user_connections[user_id]
            
            # Remove from call group
            if call_id and call_id in self.call_connections:
                self.call_connections[call_id].discard(connection_id)
                if not self.call_connections[call_id]:
                    del self.call_connections[call_id]
            
            logger.info(f"WebSocket connection {connection_id} disconnected")
            
        except Exception as e:
            logger.error(f"Error disconnecting WebSocket {connection_id}: {e}")
    
    async def send_personal_message(self, message: dict, connection_id: str):
        """Send message to a specific connection"""
        websocket = self.active_connections.get(connection_id)
        if websocket and websocket.client_state == WebSocketState.CONNECTED:
            try:
                await websocket.send_text(json.dumps(message))
                return True
            except Exception as e:
                logger.error(f"Failed to send message to {connection_id}: {e}")
                self.disconnect(connection_id)
                return False
        return False
    
    async def broadcast_to_tenant(self, message: dict, tenant_id: str):
        """Broadcast message to all connections of a tenant"""
        if tenant_id not in self.tenant_connections:
            return
        
        connection_ids = list(self.tenant_connections[tenant_id])
        successful_sends = 0
        
        for connection_id in connection_ids:
            if await self.send_personal_message(message, connection_id):
                successful_sends += 1
        
        logger.info(f"Broadcasted to {successful_sends}/{len(connection_ids)} tenant connections")
    
    async def broadcast_to_user(self, message: dict, user_id: str):
        """Broadcast message to all connections of a user"""
        if user_id not in self.user_connections:
            return
        
        connection_ids = list(self.user_connections[user_id])
        successful_sends = 0
        
        for connection_id in connection_ids:
            if await self.send_personal_message(message, connection_id):
                successful_sends += 1
        
        logger.info(f"Broadcasted to {successful_sends}/{len(connection_ids)} user connections")
    
    async def broadcast_to_call(self, message: dict, call_id: str):
        """Broadcast message to all connections monitoring a call"""
        if call_id not in self.call_connections:
            return
        
        connection_ids = list(self.call_connections[call_id])
        successful_sends = 0
        
        for connection_id in connection_ids:
            if await self.send_personal_message(message, connection_id):
                successful_sends += 1
        
        logger.info(f"Broadcasted to {successful_sends}/{len(connection_ids)} call monitoring connections")
    
    async def broadcast_to_all(self, message: dict):
        """Broadcast message to all active connections"""
        connection_ids = list(self.active_connections.keys())
        successful_sends = 0
        
        for connection_id in connection_ids:
            if await self.send_personal_message(message, connection_id):
                successful_sends += 1
        
        logger.info(f"Broadcasted to {successful_sends}/{len(connection_ids)} total connections")
    
    def get_connection_count(self) -> int:
        """Get total number of active connections"""
        return len(self.active_connections)
    
    def get_tenant_connection_count(self, tenant_id: str) -> int:
        """Get number of connections for a specific tenant"""
        return len(self.tenant_connections.get(tenant_id, set()))
    
    def get_user_connection_count(self, user_id: str) -> int:
        """Get number of connections for a specific user"""
        return len(self.user_connections.get(user_id, set()))
    
    def get_call_connection_count(self, call_id: str) -> int:
        """Get number of connections monitoring a specific call"""
        return len(self.call_connections.get(call_id, set()))
    
    def is_user_connected(self, user_id: str) -> bool:
        """Check if a user has any active connections"""
        return user_id in self.user_connections and len(self.user_connections[user_id]) > 0
    
    def is_call_being_monitored(self, call_id: str) -> bool:
        """Check if a call is being actively monitored"""
        return call_id in self.call_connections and len(self.call_connections[call_id]) > 0
    
    async def send_call_update(self, call_id: str, update_type: str, data: dict):
        """Send real-time call update"""
        message = {
            "type": "call_update",
            "call_id": call_id,
            "update_type": update_type,
            "data": data,
            "timestamp": json.dumps({"timestamp": "now"})  # Will be replaced with actual timestamp
        }
        await self.broadcast_to_call(message, call_id)
    
    async def send_tenant_notification(self, tenant_id: str, notification_type: str, data: dict):
        """Send notification to all tenant connections"""
        message = {
            "type": "notification",
            "notification_type": notification_type,
            "data": data,
            "timestamp": json.dumps({"timestamp": "now"})
        }
        await self.broadcast_to_tenant(message, tenant_id)
    
    async def send_user_notification(self, user_id: str, notification_type: str, data: dict):
        """Send notification to specific user"""
        message = {
            "type": "notification",
            "notification_type": notification_type,
            "data": data,
            "timestamp": json.dumps({"timestamp": "now"})
        }
        await self.broadcast_to_user(message, user_id)
    
    def get_stats(self) -> dict:
        """Get connection statistics"""
        return {
            "total_connections": len(self.active_connections),
            "tenants_connected": len(self.tenant_connections),
            "users_connected": len(self.user_connections),
            "calls_being_monitored": len(self.call_connections),
            "tenant_breakdown": {
                tenant_id: len(connections) 
                for tenant_id, connections in self.tenant_connections.items()
            }
        }