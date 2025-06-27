"""
Queue Service

This module provides job queue management for batch processing of shader validation.
"""

import logging
import asyncio
import json
import uuid
from typing import Dict, Any, List, Optional, Callable, Awaitable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class JobStatus(str, Enum):
    """Job status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobPriority(int, Enum):
    """Job priority enumeration."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass
class Job:
    """Job data structure."""
    id: str
    job_type: str
    data: Dict[str, Any]
    status: JobStatus
    priority: JobPriority
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    progress: float = 0.0
    max_retries: int = 3
    retry_count: int = 0


class QueueServiceError(Exception):
    """Exception raised for queue service errors."""
    pass


class QueueService:
    """
    Job queue service for batch processing.
    
    This service manages job queues for shader validation, visualization,
    and analysis tasks with priority handling and retry logic.
    """
    
    def __init__(self, max_workers: int = 4, max_queue_size: int = 1000):
        """
        Initialize the queue service.
        
        Args:
            max_workers: Maximum number of concurrent workers
            max_queue_size: Maximum number of jobs in queue
        """
        self.max_workers = max_workers
        self.max_queue_size = max_queue_size
        
        # Job storage
        self.jobs: Dict[str, Job] = {}
        self.pending_queue: List[str] = []
        self.processing_jobs: Dict[str, Job] = {}
        
        # Worker management
        self.workers: List[asyncio.Task] = []
        self.is_running = False
        
        # Job handlers
        self.job_handlers: Dict[str, Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]] = {}
        
        # Statistics
        self.stats = {
            'total_jobs': 0,
            'completed_jobs': 0,
            'failed_jobs': 0,
            'cancelled_jobs': 0,
            'average_processing_time': 0.0
        }
    
    async def start(self):
        """Start the queue service and workers."""
        if self.is_running:
            return
        
        self.is_running = True
        logger.info(f"Starting queue service with {self.max_workers} workers")
        
        # Start worker tasks
        for i in range(self.max_workers):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self.workers.append(worker)
    
    async def stop(self):
        """Stop the queue service and workers."""
        if not self.is_running:
            return
        
        self.is_running = False
        logger.info("Stopping queue service")
        
        # Cancel all workers
        for worker in self.workers:
            worker.cancel()
        
        # Wait for workers to finish
        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers.clear()
        
        # Cancel all pending jobs
        for job_id in self.pending_queue:
            if job_id in self.jobs:
                self.jobs[job_id].status = JobStatus.CANCELLED
                self.jobs[job_id].completed_at = datetime.utcnow()
        
        self.pending_queue.clear()
    
    async def submit_job(self, 
                        job_type: str, 
                        data: Dict[str, Any], 
                        priority: JobPriority = JobPriority.NORMAL) -> str:
        """
        Submit a new job to the queue.
        
        Args:
            job_type: Type of job to execute
            data: Job data
            priority: Job priority
            
        Returns:
            Job ID
        """
        if not self.is_running:
            raise QueueServiceError("Queue service is not running")
        
        if len(self.jobs) >= self.max_queue_size:
            raise QueueServiceError("Queue is full")
        
        if job_type not in self.job_handlers:
            raise QueueServiceError(f"No handler registered for job type: {job_type}")
        
        # Create job
        job_id = str(uuid.uuid4())
        job = Job(
            id=job_id,
            job_type=job_type,
            data=data,
            status=JobStatus.PENDING,
            priority=priority,
            created_at=datetime.utcnow()
        )
        
        # Store job
        self.jobs[job_id] = job
        self.pending_queue.append(job_id)
        
        # Sort queue by priority
        self.pending_queue.sort(key=lambda jid: self.jobs[jid].priority.value, reverse=True)
        
        self.stats['total_jobs'] += 1
        logger.info(f"Submitted job {job_id} of type {job_type} with priority {priority.value}")
        
        return job_id
    
    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get job status and details.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job status information or None if not found
        """
        if job_id not in self.jobs:
            return None
        
        job = self.jobs[job_id]
        return asdict(job)
    
    async def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a pending job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            True if job was cancelled, False otherwise
        """
        if job_id not in self.jobs:
            return False
        
        job = self.jobs[job_id]
        
        if job.status == JobStatus.PENDING:
            job.status = JobStatus.CANCELLED
            job.completed_at = datetime.utcnow()
            
            # Remove from pending queue
            if job_id in self.pending_queue:
                self.pending_queue.remove(job_id)
            
            self.stats['cancelled_jobs'] += 1
            logger.info(f"Cancelled job {job_id}")
            return True
        
        return False
    
    async def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        pending_count = len(self.pending_queue)
        processing_count = len(self.processing_jobs)
        
        return {
            'queue_size': len(self.jobs),
            'pending_jobs': pending_count,
            'processing_jobs': processing_count,
            'available_workers': self.max_workers - processing_count,
            'max_workers': self.max_workers,
            'max_queue_size': self.max_queue_size,
            'is_running': self.is_running,
            'stats': self.stats.copy(),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def register_handler(self, job_type: str, handler: Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]):
        """
        Register a job handler.
        
        Args:
            job_type: Type of job to handle
            handler: Async function to handle the job
        """
        self.job_handlers[job_type] = handler
        logger.info(f"Registered handler for job type: {job_type}")
    
    async def _worker(self, worker_name: str):
        """Worker task that processes jobs."""
        logger.info(f"Worker {worker_name} started")
        
        while self.is_running:
            try:
                # Get next job
                job_id = await self._get_next_job()
                if not job_id:
                    await asyncio.sleep(0.1)
                    continue
                
                # Process job
                await self._process_job(job_id, worker_name)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker {worker_name} error: {e}")
                await asyncio.sleep(1)
        
        logger.info(f"Worker {worker_name} stopped")
    
    async def _get_next_job(self) -> Optional[str]:
        """Get the next job from the queue."""
        if not self.pending_queue:
            return None
        
        job_id = self.pending_queue.pop(0)
        job = self.jobs[job_id]
        
        # Check if job was cancelled
        if job.status == JobStatus.CANCELLED:
            return None
        
        # Mark as processing
        job.status = JobStatus.PROCESSING
        job.started_at = datetime.utcnow()
        self.processing_jobs[job_id] = job
        
        return job_id
    
    async def _process_job(self, job_id: str, worker_name: str):
        """Process a job."""
        job = self.jobs[job_id]
        logger.info(f"Worker {worker_name} processing job {job_id} of type {job.job_type}")
        
        try:
            # Get handler
            handler = self.job_handlers.get(job.job_type)
            if not handler:
                raise QueueServiceError(f"No handler for job type: {job.job_type}")
            
            # Update progress
            job.progress = 0.1
            await self._update_job_progress(job_id, 0.1)
            
            # Execute job
            result = await handler(job.data)
            
            # Update progress
            job.progress = 1.0
            await self._update_job_progress(job_id, 1.0)
            
            # Mark as completed
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            job.result = result
            
            self.stats['completed_jobs'] += 1
            
            # Update average processing time
            processing_time = (job.completed_at - job.started_at).total_seconds()
            self._update_average_processing_time(processing_time)
            
            logger.info(f"Job {job_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}")
            
            # Handle retries
            if job.retry_count < job.max_retries:
                job.retry_count += 1
                job.status = JobStatus.PENDING
                job.started_at = None
                job.progress = 0.0
                
                # Add back to queue with lower priority
                job.priority = JobPriority(max(1, job.priority.value - 1))
                self.pending_queue.append(job_id)
                self.pending_queue.sort(key=lambda jid: self.jobs[jid].priority.value, reverse=True)
                
                logger.info(f"Retrying job {job_id} (attempt {job.retry_count}/{job.max_retries})")
            else:
                # Mark as failed
                job.status = JobStatus.FAILED
                job.completed_at = datetime.utcnow()
                job.error = str(e)
                
                self.stats['failed_jobs'] += 1
                logger.error(f"Job {job_id} failed after {job.max_retries} retries")
        
        finally:
            # Remove from processing
            if job_id in self.processing_jobs:
                del self.processing_jobs[job_id]
    
    async def _update_job_progress(self, job_id: str, progress: float):
        """Update job progress."""
        if job_id in self.jobs:
            self.jobs[job_id].progress = progress
    
    def _update_average_processing_time(self, processing_time: float):
        """Update average processing time statistic."""
        total_completed = self.stats['completed_jobs']
        current_avg = self.stats['average_processing_time']
        
        if total_completed == 1:
            self.stats['average_processing_time'] = processing_time
        else:
            self.stats['average_processing_time'] = (
                (current_avg * (total_completed - 1) + processing_time) / total_completed
            )
    
    async def cleanup_old_jobs(self, max_age_hours: int = 24):
        """
        Clean up old completed/failed jobs.
        
        Args:
            max_age_hours: Maximum age in hours to keep jobs
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        jobs_to_remove = []
        
        for job_id, job in self.jobs.items():
            if (job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED] and
                job.completed_at and job.completed_at < cutoff_time):
                jobs_to_remove.append(job_id)
        
        for job_id in jobs_to_remove:
            del self.jobs[job_id]
            if job_id in self.pending_queue:
                self.pending_queue.remove(job_id)
            if job_id in self.processing_jobs:
                del self.processing_jobs[job_id]
        
        if jobs_to_remove:
            logger.info(f"Cleaned up {len(jobs_to_remove)} old jobs")


# Global queue service instance
_queue_service = None


def get_queue_service() -> QueueService:
    """Get the global queue service instance."""
    global _queue_service
    if _queue_service is None:
        _queue_service = QueueService()
    return _queue_service 