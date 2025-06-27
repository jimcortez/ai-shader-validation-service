"""
Real-time WebSocket Endpoints

This module provides WebSocket endpoints for real-time validation feedback.
"""

import logging
import json
from typing import Optional, Dict, Any
from fastapi import WebSocket, WebSocketDisconnect, HTTPException, Query
from fastapi.responses import JSONResponse

from src.api.websocket.connection_manager import connection_manager
from src.services.validation_service import get_validation_service
from src.services.visualization_service import get_visualization_service
from src.services.analysis_service import get_analysis_service

logger = logging.getLogger(__name__)


async def websocket_endpoint(websocket: WebSocket, client_id: Optional[str] = None):
    """
    Main WebSocket endpoint for real-time validation.
    
    Args:
        websocket: WebSocket connection
        client_id: Optional client identifier
    """
    connection_id = None
    
    try:
        # Accept connection
        connection_id = await connection_manager.connect(websocket, client_id)
        
        # Main message loop
        while True:
            try:
                # Receive message
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle message based on type
                await handle_websocket_message(connection_id, message)
                
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected: {connection_id}")
                break
            except json.JSONDecodeError:
                await connection_manager.send_error(
                    connection_id, 
                    "Invalid JSON message format"
                )
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {e}")
                await connection_manager.send_error(
                    connection_id, 
                    f"Internal server error: {str(e)}"
                )
                
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    finally:
        if connection_id:
            await connection_manager.disconnect(connection_id)


async def handle_websocket_message(connection_id: str, message: Dict[str, Any]):
    """
    Handle incoming WebSocket messages.
    
    Args:
        connection_id: Connection identifier
        message: Message data
    """
    message_type = message.get('type')
    
    if message_type == 'validate_shader':
        await handle_validation_request(connection_id, message)
    elif message_type == 'visualize_shader':
        await handle_visualization_request(connection_id, message)
    elif message_type == 'analyze_shader':
        await handle_analysis_request(connection_id, message)
    elif message_type == 'join_group':
        await handle_join_group(connection_id, message)
    elif message_type == 'leave_group':
        await handle_leave_group(connection_id, message)
    elif message_type == 'ping':
        await handle_ping(connection_id, message)
    else:
        await connection_manager.send_error(
            connection_id, 
            f"Unknown message type: {message_type}"
        )


async def handle_validation_request(connection_id: str, message: Dict[str, Any]):
    """
    Handle shader validation request.
    
    Args:
        connection_id: Connection identifier
        message: Validation request message
    """
    try:
        # Extract validation parameters
        shader_source = message.get('shader_source')
        shader_type = message.get('shader_type', 'GLSL')
        parameters = message.get('parameters', {})
        
        if not shader_source:
            await connection_manager.send_error(
                connection_id, 
                "Missing shader_source in validation request"
            )
            return
        
        # Send initial progress
        await connection_manager.send_validation_progress(connection_id, {
            'stage': 'starting',
            'message': 'Starting validation...',
            'progress': 0
        })
        
        # Get validation service
        validation_service = get_validation_service()
        
        # Send parsing progress
        await connection_manager.send_validation_progress(connection_id, {
            'stage': 'parsing',
            'message': 'Parsing shader...',
            'progress': 20
        })
        
        # Perform validation
        await connection_manager.send_validation_progress(connection_id, {
            'stage': 'validating',
            'message': 'Validating shader...',
            'progress': 50
        })
        
        result = validation_service.validate_shader(shader_source, shader_type, parameters)
        
        # Send completion progress
        await connection_manager.send_validation_progress(connection_id, {
            'stage': 'completing',
            'message': 'Finalizing results...',
            'progress': 90
        })
        
        # Send final result
        await connection_manager.send_validation_result(connection_id, result)
        
        # Send completion
        await connection_manager.send_validation_progress(connection_id, {
            'stage': 'completed',
            'message': 'Validation completed',
            'progress': 100
        })
        
    except Exception as e:
        logger.error(f"Error in validation request: {e}")
        await connection_manager.send_error(
            connection_id, 
            f"Validation failed: {str(e)}"
        )


async def handle_visualization_request(connection_id: str, message: Dict[str, Any]):
    """
    Handle shader visualization request.
    
    Args:
        connection_id: Connection identifier
        message: Visualization request message
    """
    try:
        # Extract visualization parameters
        shader_source = message.get('shader_source')
        shader_type = message.get('shader_type', 'GLSL')
        width = message.get('width', 512)
        height = message.get('height', 512)
        format_type = message.get('format', 'PNG')
        parameters = message.get('parameters', {})
        
        if not shader_source:
            await connection_manager.send_error(
                connection_id, 
                "Missing shader_source in visualization request"
            )
            return
        
        # Send initial progress
        await connection_manager.send_validation_progress(connection_id, {
            'stage': 'visualization_starting',
            'message': 'Starting visualization...',
            'progress': 0
        })
        
        # Get visualization service
        visualization_service = get_visualization_service()
        
        # Send rendering progress
        await connection_manager.send_validation_progress(connection_id, {
            'stage': 'rendering',
            'message': 'Rendering shader...',
            'progress': 50
        })
        
        # Perform visualization
        if shader_type == 'GLSL':
            image_id, image_data = visualization_service.render_glsl_shader(
                shader_source, width, height, parameters, format_type
            )
        elif shader_type == 'ISF':
            # Parse ISF data
            if isinstance(shader_source, str):
                import json
                isf_data = json.loads(shader_source)
            else:
                isf_data = shader_source
            image_id, image_data = visualization_service.render_isf_shader(
                isf_data, width, height, parameters, format_type
            )
        else:
            # Treat as GLSL
            image_id, image_data = visualization_service.render_glsl_shader(
                shader_source, width, height, parameters, format_type
            )
        
        # Send completion progress
        await connection_manager.send_validation_progress(connection_id, {
            'stage': 'visualization_completing',
            'message': 'Finalizing visualization...',
            'progress': 90
        })
        
        # Send visualization result
        result = {
            'image_id': image_id,
            'image_url': f"/api/v1/images/{image_id}",
            'width': width,
            'height': height,
            'format': format_type,
            'metadata': visualization_service.get_image_metadata(image_id) or {}
        }
        
        await connection_manager.send_validation_result(connection_id, {
            'type': 'visualization_result',
            'result': result
        })
        
        # Send completion
        await connection_manager.send_validation_progress(connection_id, {
            'stage': 'visualization_completed',
            'message': 'Visualization completed',
            'progress': 100
        })
        
    except Exception as e:
        logger.error(f"Error in visualization request: {e}")
        await connection_manager.send_error(
            connection_id, 
            f"Visualization failed: {str(e)}"
        )


async def handle_analysis_request(connection_id: str, message: Dict[str, Any]):
    """
    Handle shader analysis request.
    
    Args:
        connection_id: Connection identifier
        message: Analysis request message
    """
    try:
        # Extract analysis parameters
        shader_source = message.get('shader_source')
        shader_type = message.get('shader_type', 'GLSL')
        parameters = message.get('parameters', {})
        
        if not shader_source:
            await connection_manager.send_error(
                connection_id, 
                "Missing shader_source in analysis request"
            )
            return
        
        # Send initial progress
        await connection_manager.send_validation_progress(connection_id, {
            'stage': 'analysis_starting',
            'message': 'Starting analysis...',
            'progress': 0
        })
        
        # Get analysis service
        analysis_service = get_analysis_service()
        
        # Send analysis progress
        await connection_manager.send_validation_progress(connection_id, {
            'stage': 'analyzing',
            'message': 'Analyzing shader...',
            'progress': 50
        })
        
        # Perform analysis
        result = analysis_service.create_comprehensive_analysis(
            shader_source, shader_type, parameters
        )
        
        # Send completion progress
        await connection_manager.send_validation_progress(connection_id, {
            'stage': 'analysis_completing',
            'message': 'Finalizing analysis...',
            'progress': 90
        })
        
        # Send analysis result
        await connection_manager.send_validation_result(connection_id, {
            'type': 'analysis_result',
            'result': result
        })
        
        # Send completion
        await connection_manager.send_validation_progress(connection_id, {
            'stage': 'analysis_completed',
            'message': 'Analysis completed',
            'progress': 100
        })
        
    except Exception as e:
        logger.error(f"Error in analysis request: {e}")
        await connection_manager.send_error(
            connection_id, 
            f"Analysis failed: {str(e)}"
        )


async def handle_join_group(connection_id: str, message: Dict[str, Any]):
    """
    Handle join group request.
    
    Args:
        connection_id: Connection identifier
        message: Join group message
    """
    try:
        group_name = message.get('group_name')
        
        if not group_name:
            await connection_manager.send_error(
                connection_id, 
                "Missing group_name in join group request"
            )
            return
        
        # Add to group
        connection_manager.add_to_group(connection_id, group_name)
        
        # Send confirmation
        await connection_manager.send_personal_message(connection_id, {
            'type': 'group_joined',
            'group_name': group_name,
            'timestamp': connection_manager.connection_metadata[connection_id]['last_activity']
        })
        
    except Exception as e:
        logger.error(f"Error joining group: {e}")
        await connection_manager.send_error(
            connection_id, 
            f"Failed to join group: {str(e)}"
        )


async def handle_leave_group(connection_id: str, message: Dict[str, Any]):
    """
    Handle leave group request.
    
    Args:
        connection_id: Connection identifier
        message: Leave group message
    """
    try:
        group_name = message.get('group_name')
        
        if not group_name:
            await connection_manager.send_error(
                connection_id, 
                "Missing group_name in leave group request"
            )
            return
        
        # Remove from group
        connection_manager.remove_from_group(connection_id, group_name)
        
        # Send confirmation
        await connection_manager.send_personal_message(connection_id, {
            'type': 'group_left',
            'group_name': group_name,
            'timestamp': connection_manager.connection_metadata[connection_id]['last_activity']
        })
        
    except Exception as e:
        logger.error(f"Error leaving group: {e}")
        await connection_manager.send_error(
            connection_id, 
            f"Failed to leave group: {str(e)}"
        )


async def handle_ping(connection_id: str, message: Dict[str, Any]):
    """
    Handle ping request.
    
    Args:
        connection_id: Connection identifier
        message: Ping message
    """
    try:
        # Send pong response
        await connection_manager.send_personal_message(connection_id, {
            'type': 'pong',
            'timestamp': connection_manager.connection_metadata[connection_id]['last_activity'],
            'connection_id': connection_id
        })
        
    except Exception as e:
        logger.error(f"Error handling ping: {e}")


async def get_websocket_stats():
    """
    Get WebSocket connection statistics.
    
    Returns:
        Connection statistics
    """
    try:
        return connection_manager.get_connection_stats()
    except Exception as e:
        logger.error(f"Error getting WebSocket stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get WebSocket statistics")


async def cleanup_websocket_connections():
    """Clean up inactive WebSocket connections."""
    try:
        await connection_manager.cleanup_inactive_connections()
    except Exception as e:
        logger.error(f"Error cleaning up WebSocket connections: {e}") 