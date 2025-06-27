"""
Dependency Graph Generation

This module provides dependency graph visualization for shader analysis,
including function dependencies, variable usage, and code structure.
"""

import logging
from typing import Dict, Any, List, Tuple, Optional, Set
import io
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)


class DependencyGraphError(Exception):
    """Exception raised for dependency graph errors."""
    pass


class DependencyGraphs:
    """
    Generates dependency graphs for shader analysis.
    
    This class provides methods for creating visual representations of
    shader dependencies, function calls, and code structure.
    """
    
    def __init__(self):
        """Initialize the dependency graph generator."""
        self._font_size = 10
        self._node_radius = 30
        self._margin = 50
        self._colors = {
            'function': (100, 150, 255, 255),
            'variable': (255, 150, 100, 255),
            'uniform': (150, 255, 150, 255),
            'texture': (255, 150, 255, 255),
            'background': (255, 255, 255, 255),
            'edge': (100, 100, 100, 255),
            'text': (50, 50, 50, 255)
        }
    
    def create_function_dependency_graph(self,
                                       functions: Dict[str, List[str]],
                                       title: str = "Function Dependencies",
                                       width: int = 800,
                                       height: int = 600) -> bytes:
        """
        Create a function dependency graph.
        
        Args:
            functions: Dictionary mapping function names to their dependencies
            title: Graph title
            width: Image width
            height: Image height
            
        Returns:
            Dependency graph image as bytes
        """
        try:
            # Create base image
            image = Image.new('RGBA', (width, height), self._colors['background'])
            draw = ImageDraw.Draw(image)
            
            # Try to load fonts
            try:
                font = ImageFont.truetype("arial.ttf", self._font_size)
                title_font = ImageFont.truetype("arial.ttf", self._font_size + 4)
            except:
                font = ImageFont.load_default()
                title_font = ImageFont.load_default()
            
            # Draw title
            title_bbox = draw.textbbox((0, 0), title, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            title_x = (width - title_width) // 2
            draw.text((title_x, self._margin), title, fill=self._colors['text'], font=title_font)
            
            if not functions:
                # Draw no data message
                no_data_text = "No function dependencies found"
                text_bbox = draw.textbbox((0, 0), no_data_text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_x = (width - text_width) // 2
                text_y = height // 2
                draw.text((text_x, text_y), no_data_text, fill=self._colors['text'], font=font)
                
                buffer = io.BytesIO()
                image.save(buffer, format='PNG')
                return buffer.getvalue()
            
            # Calculate node positions (simple circular layout)
            nodes = list(functions.keys())
            node_positions = self._calculate_circular_layout(nodes, width, height)
            
            # Draw edges first (so they appear behind nodes)
            for func_name, dependencies in functions.items():
                if func_name in node_positions:
                    start_pos = node_positions[func_name]
                    for dep in dependencies:
                        if dep in node_positions:
                            end_pos = node_positions[dep]
                            self._draw_edge(draw, start_pos, end_pos)
            
            # Draw nodes
            for func_name, pos in node_positions.items():
                self._draw_node(draw, func_name, pos, self._colors['function'], font)
            
            # Convert to bytes
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Failed to create function dependency graph: {e}")
            raise DependencyGraphError(f"Failed to create function dependency graph: {e}")
    
    def create_variable_usage_graph(self,
                                  variables: Dict[str, List[str]],
                                  title: str = "Variable Usage",
                                  width: int = 800,
                                  height: int = 600) -> bytes:
        """
        Create a variable usage graph.
        
        Args:
            variables: Dictionary mapping variable names to their usage locations
            title: Graph title
            width: Image width
            height: Image height
            
        Returns:
            Variable usage graph image as bytes
        """
        try:
            # Create base image
            image = Image.new('RGBA', (width, height), self._colors['background'])
            draw = ImageDraw.Draw(image)
            
            # Try to load fonts
            try:
                font = ImageFont.truetype("arial.ttf", self._font_size)
                title_font = ImageFont.truetype("arial.ttf", self._font_size + 4)
            except:
                font = ImageFont.load_default()
                title_font = ImageFont.load_default()
            
            # Draw title
            title_bbox = draw.textbbox((0, 0), title, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            title_x = (width - title_width) // 2
            draw.text((title_x, self._margin), title, fill=self._colors['text'], font=title_font)
            
            if not variables:
                # Draw no data message
                no_data_text = "No variable usage data found"
                text_bbox = draw.textbbox((0, 0), no_data_text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_x = (width - text_width) // 2
                text_y = height // 2
                draw.text((text_x, text_y), no_data_text, fill=self._colors['text'], font=font)
                
                buffer = io.BytesIO()
                image.save(buffer, format='PNG')
                return buffer.getvalue()
            
            # Create hierarchical layout
            y_offset = self._margin + 50
            x_offset = self._margin
            
            for var_name, usages in variables.items():
                if y_offset > height - 100:
                    break
                
                # Draw variable node
                var_pos = (x_offset + self._node_radius, y_offset + self._node_radius)
                self._draw_node(draw, var_name, var_pos, self._colors['variable'], font)
                
                # Draw usage connections
                usage_x = x_offset + 200
                for i, usage in enumerate(usages[:5]):  # Limit to 5 usages
                    usage_y = y_offset + i * 30
                    usage_pos = (usage_x, usage_y + 15)
                    
                    # Draw usage node
                    self._draw_small_node(draw, usage, usage_pos, self._colors['uniform'], font)
                    
                    # Draw edge
                    self._draw_edge(draw, var_pos, usage_pos)
                
                y_offset += max(len(usages) * 30, 60) + 20
                
                # Start new column if needed
                if y_offset > height - 100 and x_offset < width - 300:
                    x_offset += 300
                    y_offset = self._margin + 50
            
            # Convert to bytes
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Failed to create variable usage graph: {e}")
            raise DependencyGraphError(f"Failed to create variable usage graph: {e}")
    
    def create_code_structure_graph(self,
                                  structure: Dict[str, Any],
                                  title: str = "Code Structure",
                                  width: int = 800,
                                  height: int = 600) -> bytes:
        """
        Create a code structure visualization.
        
        Args:
            structure: Dictionary representing code structure
            title: Graph title
            width: Image width
            height: Image height
            
        Returns:
            Code structure graph image as bytes
        """
        try:
            # Create base image
            image = Image.new('RGBA', (width, height), self._colors['background'])
            draw = ImageDraw.Draw(image)
            
            # Try to load fonts
            try:
                font = ImageFont.truetype("arial.ttf", self._font_size)
                title_font = ImageFont.truetype("arial.ttf", self._font_size + 4)
            except:
                font = ImageFont.load_default()
                title_font = ImageFont.load_default()
            
            # Draw title
            title_bbox = draw.textbbox((0, 0), title, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            title_x = (width - title_width) // 2
            draw.text((title_x, self._margin), title, fill=self._colors['text'], font=title_font)
            
            if not structure:
                # Draw no data message
                no_data_text = "No code structure data found"
                text_bbox = draw.textbbox((0, 0), no_data_text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_x = (width - text_width) // 2
                text_y = height // 2
                draw.text((text_x, text_y), no_data_text, fill=self._colors['text'], font=font)
                
                buffer = io.BytesIO()
                image.save(buffer, format='PNG')
                return buffer.getvalue()
            
            # Draw structure as a tree
            y_offset = self._margin + 50
            self._draw_structure_node(draw, structure, self._margin, y_offset, font, 0)
            
            # Convert to bytes
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Failed to create code structure graph: {e}")
            raise DependencyGraphError(f"Failed to create code structure graph: {e}")
    
    def _calculate_circular_layout(self, nodes: List[str], width: int, height: int) -> Dict[str, Tuple[int, int]]:
        """Calculate circular layout for nodes."""
        positions = {}
        center_x = width // 2
        center_y = height // 2
        radius = min(width, height) // 3
        
        for i, node in enumerate(nodes):
            angle = (2 * 3.14159 * i) / len(nodes)
            x = center_x + int(radius * (0.8 + 0.2 * (i % 2)) * (1 if i % 2 == 0 else -1))
            y = center_y + int(radius * (0.8 + 0.2 * (i % 3)) * (1 if i % 3 == 0 else -1))
            positions[node] = (x, y)
        
        return positions
    
    def _draw_node(self, draw: ImageDraw.Draw, label: str, pos: Tuple[int, int], 
                  color: Tuple[int, int, int, int], font: ImageFont.FreeTypeFont):
        """Draw a node with label."""
        x, y = pos
        
        # Draw node circle
        draw.ellipse([x - self._node_radius, y - self._node_radius, 
                     x + self._node_radius, y + self._node_radius], 
                    fill=color, outline=self._colors['text'])
        
        # Draw label
        label_text = label[:8] + "..." if len(label) > 8 else label
        text_bbox = draw.textbbox((0, 0), label_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        text_x = x - text_width // 2
        text_y = y - text_height // 2
        draw.text((text_x, text_y), label_text, fill=self._colors['text'], font=font)
    
    def _draw_small_node(self, draw: ImageDraw.Draw, label: str, pos: Tuple[int, int], 
                        color: Tuple[int, int, int, int], font: ImageFont.FreeTypeFont):
        """Draw a small node with label."""
        x, y = pos
        small_radius = 15
        
        # Draw node circle
        draw.ellipse([x - small_radius, y - small_radius, 
                     x + small_radius, y + small_radius], 
                    fill=color, outline=self._colors['text'])
        
        # Draw label
        label_text = label[:6] + "..." if len(label) > 6 else label
        text_bbox = draw.textbbox((0, 0), label_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        text_x = x - text_width // 2
        text_y = y - text_height // 2
        draw.text((text_x, text_y), label_text, fill=self._colors['text'], font=font)
    
    def _draw_edge(self, draw: ImageDraw.Draw, start: Tuple[int, int], end: Tuple[int, int]):
        """Draw an edge between two nodes."""
        draw.line([start, end], fill=self._colors['edge'], width=2)
    
    def _draw_structure_node(self, draw: ImageDraw.Draw, node: Dict[str, Any], 
                           x: int, y: int, font: ImageFont.FreeTypeFont, depth: int):
        """Recursively draw structure nodes."""
        if depth > 3:  # Limit depth to avoid overflow
            return
        
        # Draw current node
        node_type = node.get('type', 'unknown')
        node_name = node.get('name', 'unnamed')
        
        # Choose color based on node type
        if node_type == 'function':
            color = self._colors['function']
        elif node_type == 'variable':
            color = self._colors['variable']
        elif node_type == 'uniform':
            color = self._colors['uniform']
        else:
            color = self._colors['text']
        
        # Draw node
        node_pos = (x + 50, y + 20)
        self._draw_small_node(draw, node_name, node_pos, color, font)
        
        # Draw children
        children = node.get('children', [])
        child_y = y + 60
        for child in children[:3]:  # Limit children to avoid overflow
            # Draw edge to child
            child_pos = (x + 50, child_y + 20)
            self._draw_edge(draw, node_pos, child_pos)
            
            # Recursively draw child
            self._draw_structure_node(draw, child, x + 100, child_y, font, depth + 1)
            child_y += 60 