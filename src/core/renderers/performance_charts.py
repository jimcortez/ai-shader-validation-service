"""
Performance Charts and Visualization

This module provides performance chart generation for shader analysis,
including performance metrics visualization and trend analysis.
"""

import logging
from typing import Dict, Any, List, Tuple, Optional
import io
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)


class PerformanceChartError(Exception):
    """Exception raised for performance chart errors."""
    pass


class PerformanceCharts:
    """
    Generates performance charts and visualizations for shader analysis.
    
    This class provides methods for creating various types of performance
    charts and visualizations to help analyze shader performance.
    """
    
    def __init__(self):
        """Initialize the performance charts generator."""
        self._font_size = 12
        self._line_height = 16
        self._margin = 20
        self._colors = {
            'primary': (0, 100, 200, 255),
            'secondary': (200, 100, 0, 255),
            'success': (0, 150, 0, 255),
            'warning': (200, 150, 0, 255),
            'error': (200, 0, 0, 255),
            'background': (240, 240, 240, 255),
            'grid': (200, 200, 200, 255),
            'text': (50, 50, 50, 255)
        }
    
    def create_performance_bar_chart(self,
                                   data: Dict[str, float],
                                   title: str = "Performance Metrics",
                                   width: int = 600,
                                   height: int = 400) -> bytes:
        """
        Create a bar chart for performance metrics.
        
        Args:
            data: Dictionary of metric names to values
            title: Chart title
            width: Image width
            height: Image height
            
        Returns:
            Bar chart image as bytes
        """
        try:
            # Create base image
            image = Image.new('RGBA', (width, height), (255, 255, 255, 255))
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
            
            if not data:
                # Draw no data message
                no_data_text = "No performance data available"
                text_bbox = draw.textbbox((0, 0), no_data_text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_x = (width - text_width) // 2
                text_y = height // 2
                draw.text((text_x, text_y), no_data_text, fill=self._colors['text'], font=font)
                
                buffer = io.BytesIO()
                image.save(buffer, format='PNG')
                return buffer.getvalue()
            
            # Calculate chart area
            chart_top = self._margin + 50
            chart_bottom = height - self._margin - 30
            chart_left = self._margin + 100
            chart_right = width - self._margin
            
            chart_width = chart_right - chart_left
            chart_height = chart_bottom - chart_top
            
            # Find data range
            min_val = min(data.values())
            max_val = max(data.values())
            value_range = max_val - min_val if max_val != min_val else 1
            
            # Draw bars
            bar_width = chart_width // len(data)
            bar_spacing = 5
            
            for i, (metric, value) in enumerate(data.items()):
                # Calculate bar position and height
                bar_x = chart_left + i * (bar_width + bar_spacing)
                normalized_value = (value - min_val) / value_range
                bar_height = int(chart_height * normalized_value)
                bar_y = chart_bottom - bar_height
                
                # Draw bar
                color = self._get_bar_color(normalized_value)
                draw.rectangle([bar_x, bar_y, bar_x + bar_width - bar_spacing, bar_y + bar_height], 
                              fill=color, outline=self._colors['text'])
                
                # Draw value label
                value_text = f"{value:.2f}"
                text_bbox = draw.textbbox((0, 0), value_text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_x = bar_x + (bar_width - bar_spacing - text_width) // 2
                text_y = bar_y - 20
                draw.text((text_x, text_y), value_text, fill=self._colors['text'], font=font)
                
                # Draw metric label
                metric_text = metric[:10] + "..." if len(metric) > 10 else metric
                text_bbox = draw.textbbox((0, 0), metric_text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_x = bar_x + (bar_width - bar_spacing - text_width) // 2
                text_y = chart_bottom + 5
                draw.text((text_x, text_y), metric_text, fill=self._colors['text'], font=font)
            
            # Draw axes
            draw.line([chart_left, chart_top, chart_left, chart_bottom], 
                     fill=self._colors['text'], width=2)  # Y-axis
            draw.line([chart_left, chart_bottom, chart_right, chart_bottom], 
                     fill=self._colors['text'], width=2)  # X-axis
            
            # Convert to bytes
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Failed to create performance bar chart: {e}")
            raise PerformanceChartError(f"Failed to create performance bar chart: {e}")
    
    def create_performance_line_chart(self,
                                    data: List[Tuple[str, float]],
                                    title: str = "Performance Trend",
                                    width: int = 600,
                                    height: int = 400) -> bytes:
        """
        Create a line chart for performance trends.
        
        Args:
            data: List of (label, value) tuples
            title: Chart title
            width: Image width
            height: Image height
            
        Returns:
            Line chart image as bytes
        """
        try:
            # Create base image
            image = Image.new('RGBA', (width, height), (255, 255, 255, 255))
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
            
            if len(data) < 2:
                # Draw no data message
                no_data_text = "Insufficient data for trend analysis"
                text_bbox = draw.textbbox((0, 0), no_data_text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_x = (width - text_width) // 2
                text_y = height // 2
                draw.text((text_x, text_y), no_data_text, fill=self._colors['text'], font=font)
                
                buffer = io.BytesIO()
                image.save(buffer, format='PNG')
                return buffer.getvalue()
            
            # Calculate chart area
            chart_top = self._margin + 50
            chart_bottom = height - self._margin - 30
            chart_left = self._margin + 60
            chart_right = width - self._margin
            
            chart_width = chart_right - chart_left
            chart_height = chart_bottom - chart_top
            
            # Find data range
            values = [value for _, value in data]
            min_val = min(values)
            max_val = max(values)
            value_range = max_val - min_val if max_val != min_val else 1
            
            # Draw grid lines
            for i in range(5):
                y = chart_top + (chart_height * i) // 4
                draw.line([chart_left, y, chart_right, y], 
                         fill=self._colors['grid'], width=1)
                
                # Draw Y-axis labels
                label_value = max_val - (value_range * i) // 4
                label_text = f"{label_value:.1f}"
                text_bbox = draw.textbbox((0, 0), label_text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_x = chart_left - text_width - 5
                text_y = y - 8
                draw.text((text_x, text_y), label_text, fill=self._colors['text'], font=font)
            
            # Calculate point positions
            points = []
            for i, (label, value) in enumerate(data):
                x = chart_left + (chart_width * i) // (len(data) - 1)
                normalized_value = (value - min_val) / value_range
                y = chart_bottom - int(chart_height * normalized_value)
                points.append((x, y))
            
            # Draw line
            if len(points) > 1:
                for i in range(len(points) - 1):
                    draw.line([points[i], points[i + 1]], 
                             fill=self._colors['primary'], width=3)
            
            # Draw points
            for x, y in points:
                draw.ellipse([x - 4, y - 4, x + 4, y + 4], 
                           fill=self._colors['primary'], outline=self._colors['text'])
            
            # Draw X-axis labels
            for i, (label, _) in enumerate(data):
                x = chart_left + (chart_width * i) // (len(data) - 1)
                label_text = label[:8] + "..." if len(label) > 8 else label
                text_bbox = draw.textbbox((0, 0), label_text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_x = x - text_width // 2
                text_y = chart_bottom + 5
                draw.text((text_x, text_y), label_text, fill=self._colors['text'], font=font)
            
            # Draw axes
            draw.line([chart_left, chart_top, chart_left, chart_bottom], 
                     fill=self._colors['text'], width=2)  # Y-axis
            draw.line([chart_left, chart_bottom, chart_right, chart_bottom], 
                     fill=self._colors['text'], width=2)  # X-axis
            
            # Convert to bytes
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Failed to create performance line chart: {e}")
            raise PerformanceChartError(f"Failed to create performance line chart: {e}")
    
    def create_performance_pie_chart(self,
                                   data: Dict[str, float],
                                   title: str = "Performance Distribution",
                                   width: int = 500,
                                   height: int = 500) -> bytes:
        """
        Create a pie chart for performance distribution.
        
        Args:
            data: Dictionary of labels to values
            title: Chart title
            width: Image width
            height: Image height
            
        Returns:
            Pie chart image as bytes
        """
        try:
            # Create base image
            image = Image.new('RGBA', (width, height), (255, 255, 255, 255))
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
            
            if not data:
                # Draw no data message
                no_data_text = "No data available"
                text_bbox = draw.textbbox((0, 0), no_data_text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_x = (width - text_width) // 2
                text_y = height // 2
                draw.text((text_x, text_y), no_data_text, fill=self._colors['text'], font=font)
                
                buffer = io.BytesIO()
                image.save(buffer, format='PNG')
                return buffer.getvalue()
            
            # Calculate pie chart area
            total_value = sum(data.values())
            if total_value == 0:
                total_value = 1
            
            center_x = width // 2
            center_y = height // 2
            radius = min(width, height) // 3
            
            # Draw pie slices
            colors = [self._colors['primary'], self._colors['secondary'], 
                     self._colors['success'], self._colors['warning'], 
                     self._colors['error']]
            
            current_angle = 0
            legend_y = self._margin + 50
            
            for i, (label, value) in enumerate(data.items()):
                # Calculate slice angle
                slice_angle = (value / total_value) * 360
                
                # Draw pie slice
                color = colors[i % len(colors)]
                bbox = [center_x - radius, center_y - radius, 
                       center_x + radius, center_y + radius]
                
                # Draw slice
                draw.pieslice(bbox, start=current_angle, end=current_angle + slice_angle, 
                            fill=color, outline=self._colors['text'])
                
                # Draw legend
                legend_x = width - 150
                legend_color_box = [legend_x, legend_y, legend_x + 20, legend_y + 15]
                draw.rectangle(legend_color_box, fill=color, outline=self._colors['text'])
                
                # Draw legend text
                label_text = label[:15] + "..." if len(label) > 15 else label
                percentage = (value / total_value) * 100
                legend_text = f"{label_text} ({percentage:.1f}%)"
                draw.text((legend_x + 25, legend_y), legend_text, 
                         fill=self._colors['text'], font=font)
                
                legend_y += 20
                current_angle += slice_angle
            
            # Convert to bytes
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Failed to create performance pie chart: {e}")
            raise PerformanceChartError(f"Failed to create performance pie chart: {e}")
    
    def _get_bar_color(self, normalized_value: float) -> Tuple[int, int, int, int]:
        """Get color for bar based on normalized value."""
        if normalized_value < 0.3:
            return self._colors['success']
        elif normalized_value < 0.7:
            return self._colors['warning']
        else:
            return self._colors['error'] 