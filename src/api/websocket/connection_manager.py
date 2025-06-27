"""
WebSocket Connection Manager

This module manages WebSocket connections for real-time validation feedback.
"""

import logging
import json
import asyncio
from typing import Dict, Set, Optional, Any
from datetime import datetime
import uuid

from fastapi import WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections for real-time communication.
    
    This class handles connection lifecycle, message broadcasting,
    and connection state management.
    """
    
    def __init__(self):
        """Initialize the connection manager."""
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
        self.connection_groups: Dict[str, Set[str]] = {}
        self.max_connections = 100
        self.connection_timeout = 3600  # 1 hour
    
    async def connect(self, websocket: WebSocket, client_id: Optional[str] = None) -> str:
        """
        Accept a new WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            client_id: Optional client identifier
            
        Returns:
            Connection ID
        """
        try:
            await websocket.accept()
            
            # Generate connection ID
            connection_id = client_id or str(uuid.uuid4())
            
            # Check connection limit
            if len(self.active_connections) >= self.max_connections:
                await websocket.close(code=1008, reason="Connection limit exceeded")
                return connection_id
            
            # Store connection
            self.active_connections[connection_id] = websocket
            self.connection_metadata[connection_id] = {
                'connected_at': datetime.utcnow().isoformat(),
                'last_activity': datetime.utcnow().isoformat(),
                'client_id': client_id,
                'status': 'connected'
            }
            
            logger.info(f"WebSocket connected: {connection_id}")
            
            # Send welcome message
            await self.send_personal_message(connection_id, {
                'type': 'connection_established',
                'connection_id': connection_id,
                'timestamp': datetime.utcnow().isoformat(),
                'message': 'Connected to AI Shader Validator'
            })
            
            return connection_id
            
        except Exception as e:
            logger.error(f"Failed to accept WebSocket connection: {e}")
            raise
    
    async def disconnect(self, connection_id: str):
        """
        Disconnect a WebSocket connection.
        
        Args:
            connection_id: Connection identifier
        """
        try:
            if connection_id in self.active_connections:
                websocket = self.active_connections[connection_id]
                
                # Close connection if still open
                if websocket.client_state != WebSocketState.DISCONNECTED:
                    await websocket.close()
                
                # Remove from active connections
                del self.active_connections[connection_id]
                
                # Remove from groups
                for group_name, connections in self.connection_groups.items():
                    if connection_id in connections:
                        connections.remove(connection_id)
                
                # Clean up metadata
                if connection_id in self.connection_metadata:
                    self.connection_metadata[connection_id]['status'] = 'disconnected'
                    self.connection_metadata[connection_id]['disconnected_at'] = datetime.utcnow().isoformat()
                
                logger.info(f"WebSocket disconnected: {connection_id}")
                
        except Exception as e:
            logger.error(f"Error disconnecting WebSocket {connection_id}: {e}")
    
    async def send_personal_message(self, connection_id: str, message: Dict[str, Any]):
        """
        Send a message to a specific connection.
        
        Args:
            connection_id: Connection identifier
            message: Message to send
        """
        try:
            if connection_id in self.active_connections:
                websocket = self.active_connections[connection_id]
                
                if websocket.client_state == WebSocketState.CONNECTED:
                    await websocket.send_text(json.dumps(message))
                    
                    # Update last activity
                    if connection_id in self.connection_metadata:
                        self.connection_metadata[connection_id]['last_activity'] = datetime.utcnow().isoformat()
                else:
                    # Connection is no longer active, clean up
                    await self.disconnect(connection_id)
                    
        except WebSocketDisconnect:
            await self.disconnect(connection_id)
        except Exception as e:
            logger.error(f"Error sending message to {connection_id}: {e}")
            await self.disconnect(connection_id)
    
    async def broadcast(self, message: Dict[str, Any], exclude: Optional[str] = None):
        """
        Broadcast a message to all active connections.
        
        Args:
            message: Message to broadcast
            exclude: Connection ID to exclude from broadcast
        """
        disconnected_connections = []
        
        for connection_id, websocket in self.active_connections.items():
            if connection_id == exclude:
                continue
                
            try:
                if websocket.client_state == WebSocketState.CONNECTED:
                    await websocket.send_text(json.dumps(message))
                    
                    # Update last activity
                    if connection_id in self.connection_metadata:
                        self.connection_metadata[connection_id]['last_activity'] = datetime.utcnow().isoformat()
                else:
                    disconnected_connections.append(connection_id)
                    
            except WebSocketDisconnect:
                disconnected_connections.append(connection_id)
            except Exception as e:
                logger.error(f"Error broadcasting to {connection_id}: {e}")
                disconnected_connections.append(connection_id)
        
        # Clean up disconnected connections
        for connection_id in disconnected_connections:
            await self.disconnect(connection_id)
    
    async def send_to_group(self, group_name: str, message: Dict[str, Any], exclude: Optional[str] = None):
        """
        Send a message to all connections in a group.
        
        Args:
            group_name: Group name
            message: Message to send
            exclude: Connection ID to exclude
        """
        if group_name in self.connection_groups:
            for connection_id in self.connection_groups[group_name].copy():
                if connection_id != exclude:
                    await self.send_personal_message(connection_id, message)
    
    def add_to_group(self, connection_id: str, group_name: str):
        """
        Add a connection to a group.
        
        Args:
            connection_id: Connection identifier
            group_name: Group name
        """
        if group_name not in self.connection_groups:
            self.connection_groups[group_name] = set()
        
        self.connection_groups[group_name].add(connection_id)
        logger.info(f"Added {connection_id} to group {group_name}")
    
    def remove_from_group(self, connection_id: str, group_name: str):
        """
        Remove a connection from a group.
        
        Args:
            connection_id: Connection identifier
            group_name: Group name
        """
        if group_name in self.connection_groups:
            self.connection_groups[group_name].discard(connection_id)
            logger.info(f"Removed {connection_id} from group {group_name}")
    
    def get_connection_info(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a connection.
        
        Args:
            connection_id: Connection identifier
            
        Returns:
            Connection information or None if not found
        """
        if connection_id in self.connection_metadata:
            info = self.connection_metadata[connection_id].copy()
            info['active'] = connection_id in self.active_connections
            return info
        return None
    
    def get_active_connections_count(self) -> int:
        """Get the number of active connections."""
        return len(self.active_connections)
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics."""
        total_connections = len(self.connection_metadata)
        active_connections = len(self.active_connections)
        
        # Count connections by group
        group_stats = {}
        for group_name, connections in self.connection_groups.items():
            active_in_group = sum(1 for conn_id in connections if conn_id in self.active_connections)
            group_stats[group_name] = {
                'total': len(connections),
                'active': active_in_group
            }
        
        return {
            'total_connections': total_connections,
            'active_connections': active_connections,
            'max_connections': self.max_connections,
            'group_stats': group_stats,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def cleanup_inactive_connections(self):
        """Clean up inactive connections."""
        current_time = datetime.utcnow()
        inactive_connections = []
        
        for connection_id, metadata in self.connection_metadata.items():
            if metadata['status'] == 'connected':
                last_activity = datetime.fromisoformat(metadata['last_activity'])
                if (current_time - last_activity).total_seconds() > self.connection_timeout:
                    inactive_connections.append(connection_id)
        
        for connection_id in inactive_connections:
            logger.info(f"Cleaning up inactive connection: {connection_id}")
            await self.disconnect(connection_id)
    
    async def send_validation_progress(self, connection_id: str, progress: Dict[str, Any]):
        """
        Send validation progress update.
        
        Args:
            connection_id: Connection identifier
            progress: Progress information
        """
        message = {
            'type': 'validation_progress',
            'timestamp': datetime.utcnow().isoformat(),
            'progress': progress
        }
        await self.send_personal_message(connection_id, message)
    
    async def send_validation_result(self, connection_id: str, result: Dict[str, Any]):
        """
        Send validation result.
        
        Args:
            connection_id: Connection identifier
            result: Validation result
        """
        message = {
            'type': 'validation_result',
            'timestamp': datetime.utcnow().isoformat(),
            'result': result
        }
        await self.send_personal_message(connection_id, message)
    
    async def send_error(self, connection_id: str, error: str, details: Optional[Dict[str, Any]] = None):
        """
        Send error message.
        
        Args:
            connection_id: Connection identifier
            error: Error message
            details: Additional error details
        """
        message = {
            'type': 'error',
            'timestamp': datetime.utcnow().isoformat(),
            'error': error,
            'details': details or {}
        }
        await self.send_personal_message(connection_id, message)


# Global connection manager instance
connection_manager = ConnectionManager() 