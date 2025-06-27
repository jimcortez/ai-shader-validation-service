"""
Error Visualization System

This module provides error visualization capabilities for shader analysis,
including error overlays on images and visual error reporting.
"""

import logging
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io

from src.core.models.errors import ValidationError, ErrorSeverity

logger = logging.getLogger(__name__)


class ErrorVisualizationError(Exception):
    """Exception raised for error visualization errors."""
    pass


class ErrorVisualizer:
    """
    Visualizes validation errors and analysis results.
    
    This class provides methods for creating error overlays on images,
    generating visual error reports, and highlighting issues in shader code.
    """
    
    def __init__(self):
        """Initialize the error visualizer."""
        self._colors = {
            ErrorSeverity.ERROR: (255, 0, 0, 180),      # Red with alpha
            ErrorSeverity.WARNING: (255, 165, 0, 180),  # Orange with alpha
            ErrorSeverity.INFO: (0, 0, 255, 180),       # Blue with alpha
            ErrorSeverity.SUCCESS: (0, 255, 0, 180)     # Green with alpha
        }
        
        self._font_size = 12
        self._line_height = 16
        self._margin = 10
    
    def create_error_overlay(self, 
                           image_data: bytes, 
                           errors: List[ValidationError],
                           image_format: str = 'PNG') -> bytes:
        """
        Create an error overlay on an image.
        
        Args:
            image_data: Original image data as bytes
            errors: List of validation errors
            image_format: Image format
            
        Returns:
            Image data with error overlay as bytes
        """
        try:
            # Convert image data to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Create overlay
            overlay = self._create_overlay_image(image.size, errors)
            
            # Composite images
            result = Image.alpha_composite(image.convert('RGBA'), overlay)
            
            # Convert back to bytes
            buffer = io.BytesIO()
            result.save(buffer, format=image_format)
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Failed to create error overlay: {e}")
            raise ErrorVisualizationError(f"Failed to create error overlay: {e}")
    
    def create_error_report_image(self, 
                                errors: List[ValidationError],
                                width: int = 800,
                                height: int = 600) -> bytes:
        """
        Create a visual error report as an image.
        
        Args:
            errors: List of validation errors
            width: Image width
            height: Image height
            
        Returns:
            Error report image as bytes
        """
        try:
            # Create base image
            image = Image.new('RGBA', (width, height), (255, 255, 255, 255))
            draw = ImageDraw.Draw(image)
            
            # Try to load a font, fall back to default if not available
            try:
                font = ImageFont.truetype("arial.ttf", self._font_size)
                bold_font = ImageFont.truetype("arial.ttf", self._font_size + 2)
            except:
                font = ImageFont.load_default()
                bold_font = ImageFont.load_default()
            
            # Draw title
            title = "Shader Validation Error Report"
            draw.text((self._margin, self._margin), title, fill=(0, 0, 0, 255), font=bold_font)
            
            # Draw error summary
            y_offset = self._margin + 30
            summary = f"Total Errors: {len([e for e in errors if e.severity == ErrorSeverity.ERROR])}"
            draw.text((self._margin, y_offset), summary, fill=(255, 0, 0, 255), font=font)
            
            warnings = len([e for e in errors if e.severity == ErrorSeverity.WARNING])
            if warnings > 0:
                y_offset += self._line_height
                warning_text = f"Total Warnings: {warnings}"
                draw.text((self._margin, y_offset), warning_text, fill=(255, 165, 0, 255), font=font)
            
            # Draw individual errors
            y_offset += self._line_height * 2
            for i, error in enumerate(errors):
                if y_offset > height - 50:  # Leave some margin at bottom
                    break
                
                # Error header
                severity_color = self._colors[error.severity]
                header = f"{error.severity.value.upper()}: {error.category}"
                draw.text((self._margin, y_offset), header, fill=severity_color, font=bold_font)
                y_offset += self._line_height
                
                # Error message
                message = error.message[:80] + "..." if len(error.message) > 80 else error.message
                draw.text((self._margin + 10, y_offset), message, fill=(0, 0, 0, 255), font=font)
                y_offset += self._line_height
                
                # Error details
                if error.line_number:
                    details = f"Line: {error.line_number}"
                    if error.column_number:
                        details += f", Column: {error.column_number}"
                    draw.text((self._margin + 10, y_offset), details, fill=(100, 100, 100, 255), font=font)
                    y_offset += self._line_height
                
                y_offset += 5  # Spacing between errors
            
            # Convert to bytes
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Failed to create error report image: {e}")
            raise ErrorVisualizationError(f"Failed to create error report image: {e}")
    
    def create_code_highlight_image(self, 
                                  shader_code: str,
                                  errors: List[ValidationError],
                                  width: int = 800,
                                  height: int = 600) -> bytes:
        """
        Create an image with highlighted code and error markers.
        
        Args:
            shader_code: Shader source code
            errors: List of validation errors
            width: Image width
            height: Image height
            
        Returns:
            Code highlight image as bytes
        """
        try:
            # Create base image
            image = Image.new('RGBA', (width, height), (255, 255, 255, 255))
            draw = ImageDraw.Draw(image)
            
            # Try to load a monospace font
            try:
                font = ImageFont.truetype("courier.ttf", self._font_size)
            except:
                font = ImageFont.load_default()
            
            # Split code into lines
            lines = shader_code.split('\n')
            
            # Calculate line positions
            line_positions = {}
            y_offset = self._margin
            for i, line in enumerate(lines):
                line_positions[i + 1] = y_offset
                y_offset += self._line_height
                if y_offset > height - 50:
                    break
            
            # Draw code lines
            y_offset = self._margin
            for i, line in enumerate(lines):
                if y_offset > height - 50:
                    break
                
                # Draw line number
                line_num = f"{i + 1:3d} "
                draw.text((self._margin, y_offset), line_num, fill=(150, 150, 150, 255), font=font)
                
                # Draw code line
                code_x = self._margin + 40
                draw.text((code_x, y_offset), line, fill=(0, 0, 0, 255), font=font)
                
                y_offset += self._line_height
            
            # Draw error markers
            for error in errors:
                if error.line_number and error.line_number in line_positions:
                    y_pos = line_positions[error.line_number]
                    color = self._colors[error.severity]
                    
                    # Draw error marker
                    marker_x = self._margin + 35
                    marker_y = y_pos + self._line_height // 2
                    draw.ellipse([marker_x - 3, marker_y - 3, marker_x + 3, marker_y + 3], 
                               fill=color, outline=(0, 0, 0, 255))
                    
                    # Draw error line
                    if error.column_number:
                        line_start = self._margin + 40
                        error_x = line_start + (error.column_number - 1) * 8  # Approximate character width
                        draw.line([error_x, y_pos, error_x, y_pos + self._line_height], 
                                fill=color, width=2)
            
            # Convert to bytes
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Failed to create code highlight image: {e}")
            raise ErrorVisualizationError(f"Failed to create code highlight image: {e}")
    
    def _create_overlay_image(self, size: Tuple[int, int], errors: List[ValidationError]) -> Image.Image:
        """Create an overlay image with error markers."""
        overlay = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Try to load a font
        try:
            font = ImageFont.truetype("arial.ttf", self._font_size)
        except:
            font = ImageFont.load_default()
        
        # Draw error markers
        for error in errors:
            color = self._colors[error.severity]
            
            # Calculate position based on error line/column if available
            if error.line_number and error.column_number:
                # This is a simplified positioning - in a real implementation,
                # you'd need to map code positions to image coordinates
                x = min(error.column_number * 10, size[0] - 50)
                y = min(error.line_number * 20, size[1] - 50)
            else:
                # Random position if no line/column info
                x = np.random.randint(50, size[0] - 50)
                y = np.random.randint(50, size[1] - 50)
            
            # Draw error marker
            marker_size = 8
            draw.ellipse([x - marker_size, y - marker_size, x + marker_size, y + marker_size], 
                        fill=color, outline=(0, 0, 0, 255))
            
            # Draw error text
            text = f"{error.severity.value[0]}: {error.category}"
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            # Ensure text fits within image bounds
            text_x = max(0, min(x + marker_size + 5, size[0] - text_width - 5))
            text_y = max(0, min(y - text_height // 2, size[1] - text_height - 5))
            
            # Draw text background
            draw.rectangle([text_x - 2, text_y - 2, text_x + text_width + 2, text_y + text_height + 2], 
                          fill=(255, 255, 255, 200))
            draw.text((text_x, text_y), text, fill=(0, 0, 0, 255), font=font)
        
        return overlay
    
    def create_performance_heatmap(self, 
                                  performance_data: Dict[str, float],
                                  width: int = 400,
                                  height: int = 300) -> bytes:
        """
        Create a performance heatmap visualization.
        
        Args:
            performance_data: Dictionary of performance metrics
            width: Image width
            height: Image height
            
        Returns:
            Performance heatmap as bytes
        """
        try:
            # Create base image
            image = Image.new('RGBA', (width, height), (255, 255, 255, 255))
            draw = ImageDraw.Draw(image)
            
            # Try to load a font
            try:
                font = ImageFont.truetype("arial.ttf", self._font_size)
                bold_font = ImageFont.truetype("arial.ttf", self._font_size + 2)
            except:
                font = ImageFont.load_default()
                bold_font = ImageFont.load_default()
            
            # Draw title
            title = "Performance Analysis"
            draw.text((self._margin, self._margin), title, fill=(0, 0, 0, 255), font=bold_font)
            
            # Calculate color scale
            if performance_data:
                min_val = min(performance_data.values())
                max_val = max(performance_data.values())
                value_range = max_val - min_val if max_val != min_val else 1
            else:
                min_val = max_val = value_range = 1
            
            # Draw performance bars
            y_offset = self._margin + 40
            bar_height = 20
            bar_spacing = 5
            
            for metric, value in performance_data.items():
                if y_offset > height - 50:
                    break
                
                # Calculate color based on value
                normalized_value = (value - min_val) / value_range
                if normalized_value < 0.3:
                    color = (0, 255, 0, 255)  # Green for good performance
                elif normalized_value < 0.7:
                    color = (255, 255, 0, 255)  # Yellow for moderate performance
                else:
                    color = (255, 0, 0, 255)  # Red for poor performance
                
                # Draw metric name
                draw.text((self._margin, y_offset), metric, fill=(0, 0, 0, 255), font=font)
                
                # Draw performance bar
                bar_width = int((width - 2 * self._margin) * 0.6)
                bar_x = self._margin + 150
                draw.rectangle([bar_x, y_offset, bar_x + bar_width, y_offset + bar_height], 
                              fill=(200, 200, 200, 255), outline=(0, 0, 0, 255))
                
                # Draw performance value
                value_width = int(bar_width * normalized_value)
                draw.rectangle([bar_x, y_offset, bar_x + value_width, y_offset + bar_height], 
                              fill=color)
                
                # Draw value text
                value_text = f"{value:.2f}"
                draw.text((bar_x + bar_width + 10, y_offset), value_text, fill=(0, 0, 0, 255), font=font)
                
                y_offset += bar_height + bar_spacing
            
            # Convert to bytes
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Failed to create performance heatmap: {e}")
            raise ErrorVisualizationError(f"Failed to create performance heatmap: {e}") 