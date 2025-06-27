"""
Performance Monitor

This module provides performance monitoring capabilities for tracking
system performance metrics and identifying bottlenecks.
"""

import logging
import time
import psutil
import threading
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """Performance metric data structure."""
    name: str
    value: float
    unit: str
    timestamp: datetime
    category: str


@dataclass
class PerformanceAlert:
    """Performance alert data structure."""
    metric_name: str
    threshold: float
    current_value: float
    severity: str
    message: str
    timestamp: datetime


class PerformanceMonitorError(Exception):
    """Exception raised for performance monitor errors."""
    pass


class PerformanceMonitor:
    """
    Performance monitoring system.
    
    This class provides comprehensive performance monitoring including
    system metrics, application metrics, and custom metrics.
    """
    
    def __init__(self, 
                 collection_interval: int = 30,
                 alert_thresholds: Optional[Dict[str, float]] = None):
        """
        Initialize the performance monitor.
        
        Args:
            collection_interval: Metrics collection interval in seconds
            alert_thresholds: Dictionary of metric thresholds for alerts
        """
        self.collection_interval = collection_interval
        self.alert_thresholds = alert_thresholds or {}
        
        # Metrics storage
        self.metrics: List[PerformanceMetric] = []
        self.alerts: List[PerformanceAlert] = []
        
        # Monitoring state
        self.is_monitoring = False
        self.monitor_thread = None
        
        # Custom metrics
        self.custom_metrics: Dict[str, Callable] = {}
        
        # Alert callbacks
        self.alert_callbacks: List[Callable[[PerformanceAlert], None]] = []
        
        # Statistics
        self.stats = {
            'total_metrics_collected': 0,
            'total_alerts_generated': 0,
            'monitoring_start_time': None,
            'last_collection_time': None
        }
    
    def start_monitoring(self):
        """Start performance monitoring."""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.stats['monitoring_start_time'] = datetime.utcnow()
        
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring."""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        logger.info("Performance monitoring stopped")
    
    def add_custom_metric(self, name: str, collector: Callable[[], float], unit: str = "count"):
        """
        Add a custom metric collector.
        
        Args:
            name: Metric name
            collector: Function that returns the metric value
            unit: Unit of measurement
        """
        self.custom_metrics[name] = (collector, unit)
        logger.info(f"Added custom metric: {name}")
    
    def add_alert_callback(self, callback: Callable[[PerformanceAlert], None]):
        """
        Add an alert callback function.
        
        Args:
            callback: Function to call when an alert is generated
        """
        self.alert_callbacks.append(callback)
    
    def set_alert_threshold(self, metric_name: str, threshold: float):
        """
        Set an alert threshold for a metric.
        
        Args:
            metric_name: Name of the metric
            threshold: Threshold value
        """
        self.alert_thresholds[metric_name] = threshold
        logger.info(f"Set alert threshold for {metric_name}: {threshold}")
    
    def get_metrics(self, 
                   metric_name: Optional[str] = None,
                   category: Optional[str] = None,
                   time_range: Optional[timedelta] = None) -> List[PerformanceMetric]:
        """
        Get performance metrics.
        
        Args:
            metric_name: Filter by metric name
            category: Filter by category
            time_range: Filter by time range
            
        Returns:
            List of performance metrics
        """
        filtered_metrics = self.metrics
        
        if metric_name:
            filtered_metrics = [m for m in filtered_metrics if m.name == metric_name]
        
        if category:
            filtered_metrics = [m for m in filtered_metrics if m.category == category]
        
        if time_range:
            cutoff_time = datetime.utcnow() - time_range
            filtered_metrics = [m for m in filtered_metrics if m.timestamp > cutoff_time]
        
        return filtered_metrics
    
    def get_latest_metrics(self) -> Dict[str, PerformanceMetric]:
        """Get the latest value for each metric."""
        latest_metrics = {}
        
        for metric in reversed(self.metrics):
            if metric.name not in latest_metrics:
                latest_metrics[metric.name] = metric
        
        return latest_metrics
    
    def get_alerts(self, 
                  severity: Optional[str] = None,
                  time_range: Optional[timedelta] = None) -> List[PerformanceAlert]:
        """
        Get performance alerts.
        
        Args:
            severity: Filter by severity
            time_range: Filter by time range
            
        Returns:
            List of performance alerts
        """
        filtered_alerts = self.alerts
        
        if severity:
            filtered_alerts = [a for a in filtered_alerts if a.severity == severity]
        
        if time_range:
            cutoff_time = datetime.utcnow() - time_range
            filtered_alerts = [a for a in filtered_alerts if a.timestamp > cutoff_time]
        
        return filtered_alerts
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get a performance summary."""
        if not self.metrics:
            return {
                'status': 'no_data',
                'message': 'No metrics collected yet'
            }
        
        latest_metrics = self.get_latest_metrics()
        
        # Calculate averages for key metrics
        cpu_metrics = [m for m in self.metrics if m.name == 'cpu_usage']
        memory_metrics = [m for m in self.metrics if m.name == 'memory_usage']
        
        avg_cpu = sum(m.value for m in cpu_metrics) / len(cpu_metrics) if cpu_metrics else 0
        avg_memory = sum(m.value for m in memory_metrics) / len(memory_metrics) if memory_metrics else 0
        
        # Count alerts by severity
        alert_counts = {}
        for alert in self.alerts:
            alert_counts[alert.severity] = alert_counts.get(alert.severity, 0) + 1
        
        return {
            'status': 'monitoring',
            'monitoring_duration': (datetime.utcnow() - self.stats['monitoring_start_time']).total_seconds() if self.stats['monitoring_start_time'] else 0,
            'total_metrics_collected': self.stats['total_metrics_collected'],
            'total_alerts': self.stats['total_alerts_generated'],
            'current_metrics': {name: metric.value for name, metric in latest_metrics.items()},
            'average_cpu_usage': avg_cpu,
            'average_memory_usage': avg_memory,
            'alert_counts': alert_counts,
            'last_collection': self.stats['last_collection_time'].isoformat() if self.stats['last_collection_time'] else None
        }
    
    def clear_metrics(self, older_than: Optional[timedelta] = None):
        """
        Clear old metrics.
        
        Args:
            older_than: Clear metrics older than this time
        """
        if older_than:
            cutoff_time = datetime.utcnow() - older_than
            self.metrics = [m for m in self.metrics if m.timestamp > cutoff_time]
        else:
            self.metrics.clear()
        
        logger.info("Cleared old metrics")
    
    def clear_alerts(self, older_than: Optional[timedelta] = None):
        """
        Clear old alerts.
        
        Args:
            older_than: Clear alerts older than this time
        """
        if older_than:
            cutoff_time = datetime.utcnow() - older_than
            self.alerts = [a for a in self.alerts if a.timestamp > cutoff_time]
        else:
            self.alerts.clear()
        
        logger.info("Cleared old alerts")
    
    def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.is_monitoring:
            try:
                self._collect_metrics()
                time.sleep(self.collection_interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)  # Wait before retrying
    
    def _collect_metrics(self):
        """Collect all performance metrics."""
        timestamp = datetime.utcnow()
        
        # System metrics
        self._collect_system_metrics(timestamp)
        
        # Custom metrics
        self._collect_custom_metrics(timestamp)
        
        # Check for alerts
        self._check_alerts()
        
        self.stats['last_collection_time'] = timestamp
        self.stats['total_metrics_collected'] += 1
    
    def _collect_system_metrics(self, timestamp: datetime):
        """Collect system performance metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.metrics.append(PerformanceMetric(
                name='cpu_usage',
                value=cpu_percent,
                unit='percent',
                timestamp=timestamp,
                category='system'
            ))
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.metrics.append(PerformanceMetric(
                name='memory_usage',
                value=memory.percent,
                unit='percent',
                timestamp=timestamp,
                category='system'
            ))
            
            # Memory available
            self.metrics.append(PerformanceMetric(
                name='memory_available',
                value=memory.available / (1024**3),  # GB
                unit='GB',
                timestamp=timestamp,
                category='system'
            ))
            
            # Disk usage
            disk = psutil.disk_usage('/')
            self.metrics.append(PerformanceMetric(
                name='disk_usage',
                value=disk.percent,
                unit='percent',
                timestamp=timestamp,
                category='system'
            ))
            
            # Network I/O
            network = psutil.net_io_counters()
            self.metrics.append(PerformanceMetric(
                name='network_bytes_sent',
                value=network.bytes_sent / (1024**2),  # MB
                unit='MB',
                timestamp=timestamp,
                category='system'
            ))
            
            self.metrics.append(PerformanceMetric(
                name='network_bytes_recv',
                value=network.bytes_recv / (1024**2),  # MB
                unit='MB',
                timestamp=timestamp,
                category='system'
            ))
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
    
    def _collect_custom_metrics(self, timestamp: datetime):
        """Collect custom metrics."""
        for name, (collector, unit) in self.custom_metrics.items():
            try:
                value = collector()
                self.metrics.append(PerformanceMetric(
                    name=name,
                    value=value,
                    unit=unit,
                    timestamp=timestamp,
                    category='custom'
                ))
            except Exception as e:
                logger.error(f"Error collecting custom metric {name}: {e}")
    
    def _check_alerts(self):
        """Check for performance alerts."""
        latest_metrics = self.get_latest_metrics()
        
        for metric_name, threshold in self.alert_thresholds.items():
            if metric_name in latest_metrics:
                metric = latest_metrics[metric_name]
                
                if metric.value > threshold:
                    alert = PerformanceAlert(
                        metric_name=metric_name,
                        threshold=threshold,
                        current_value=metric.value,
                        severity='warning' if metric.value < threshold * 1.5 else 'critical',
                        message=f"{metric_name} exceeded threshold: {metric.value} > {threshold}",
                        timestamp=datetime.utcnow()
                    )
                    
                    self.alerts.append(alert)
                    self.stats['total_alerts_generated'] += 1
                    
                    # Call alert callbacks
                    for callback in self.alert_callbacks:
                        try:
                            callback(alert)
                        except Exception as e:
                            logger.error(f"Error in alert callback: {e}")
                    
                    logger.warning(f"Performance alert: {alert.message}")


class AsyncPerformanceMonitor:
    """
    Asynchronous performance monitor wrapper.
    
    This class provides async methods for performance monitoring.
    """
    
    def __init__(self, monitor: PerformanceMonitor):
        """Initialize with a performance monitor."""
        self.monitor = monitor
    
    async def start_monitoring(self):
        """Async start monitoring."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.monitor.start_monitoring)
    
    async def stop_monitoring(self):
        """Async stop monitoring."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.monitor.stop_monitoring)
    
    async def get_metrics(self, 
                         metric_name: Optional[str] = None,
                         category: Optional[str] = None,
                         time_range: Optional[timedelta] = None) -> List[PerformanceMetric]:
        """Async get metrics."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.monitor.get_metrics, metric_name, category, time_range)
    
    async def get_performance_summary(self) -> Dict[str, Any]:
        """Async get performance summary."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.monitor.get_performance_summary)
    
    async def clear_metrics(self, older_than: Optional[timedelta] = None):
        """Async clear metrics."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.monitor.clear_metrics, older_than)


# Global performance monitor instances
_performance_monitor = None
_async_performance_monitor = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance."""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


def get_async_performance_monitor() -> AsyncPerformanceMonitor:
    """Get the global async performance monitor instance."""
    global _async_performance_monitor
    if _async_performance_monitor is None:
        _async_performance_monitor = AsyncPerformanceMonitor(get_performance_monitor())
    return _async_performance_monitor 