"""
Cache Manager

This module provides caching functionality for performance optimization.
"""

import logging
import time
import hashlib
import json
from typing import Any, Optional, Dict, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import threading
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Cache entry data structure."""
    key: str
    value: Any
    created_at: datetime
    accessed_at: datetime
    ttl: Optional[int] = None  # Time to live in seconds
    access_count: int = 0


class CachePolicy(str, Enum):
    """Cache eviction policies."""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In, First Out


class CacheManagerError(Exception):
    """Exception raised for cache manager errors."""
    pass


class CacheManager:
    """
    Cache manager for performance optimization.
    
    This class provides in-memory caching with configurable policies,
    TTL support, and automatic cleanup.
    """
    
    def __init__(self, 
                 max_size: int = 1000,
                 policy: CachePolicy = CachePolicy.LRU,
                 default_ttl: Optional[int] = 3600):
        """
        Initialize the cache manager.
        
        Args:
            max_size: Maximum number of cache entries
            policy: Cache eviction policy
            default_ttl: Default time to live in seconds
        """
        self.max_size = max_size
        self.policy = policy
        self.default_ttl = default_ttl
        
        # Cache storage
        self.cache: Dict[str, CacheEntry] = {}
        
        # Policy-specific data structures
        self.access_order: List[str] = []  # For LRU
        self.access_counts: Dict[str, int] = {}  # For LFU
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'size': 0
        }
        
        # Start cleanup task
        self._cleanup_task = None
        self._start_cleanup_task()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        with self._lock:
            if key not in self.cache:
                self.stats['misses'] += 1
                return None
            
            entry = self.cache[key]
            
            # Check if expired
            if self._is_expired(entry):
                self._remove_entry(key)
                self.stats['misses'] += 1
                return None
            
            # Update access information
            entry.accessed_at = datetime.utcnow()
            entry.access_count += 1
            
            # Update policy-specific data
            self._update_access_info(key)
            
            self.stats['hits'] += 1
            return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set a value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (uses default if None)
            
        Returns:
            True if successfully cached, False otherwise
        """
        with self._lock:
            # Check if key already exists
            if key in self.cache:
                # Update existing entry
                entry = self.cache[key]
                entry.value = value
                entry.accessed_at = datetime.utcnow()
                entry.ttl = ttl or self.default_ttl
                self._update_access_info(key)
                return True
            
            # Check if cache is full
            if len(self.cache) >= self.max_size:
                self._evict_entry()
            
            # Create new entry
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.utcnow(),
                accessed_at=datetime.utcnow(),
                ttl=ttl or self.default_ttl,
                access_count=1
            )
            
            self.cache[key] = entry
            self._add_access_info(key)
            self.stats['size'] = len(self.cache)
            
            return True
    
    def delete(self, key: str) -> bool:
        """
        Delete a value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if key was found and deleted, False otherwise
        """
        with self._lock:
            return self._remove_entry(key)
    
    def clear(self):
        """Clear all cache entries."""
        with self._lock:
            self.cache.clear()
            self.access_order.clear()
            self.access_counts.clear()
            self.stats['size'] = 0
            logger.info("Cache cleared")
    
    def exists(self, key: str) -> bool:
        """
        Check if a key exists in cache and is not expired.
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists and is valid, False otherwise
        """
        with self._lock:
            if key not in self.cache:
                return False
            
            entry = self.cache[key]
            if self._is_expired(entry):
                self._remove_entry(key)
                return False
            
            return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = self.stats['hits'] / total_requests if total_requests > 0 else 0
            
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'hits': self.stats['hits'],
                'misses': self.stats['misses'],
                'hit_rate': hit_rate,
                'evictions': self.stats['evictions'],
                'policy': self.policy.value,
                'default_ttl': self.default_ttl,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def get_keys(self) -> List[str]:
        """Get all cache keys."""
        with self._lock:
            return list(self.cache.keys())
    
    def get_entry_info(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a cache entry.
        
        Args:
            key: Cache key
            
        Returns:
            Entry information or None if not found
        """
        with self._lock:
            if key not in self.cache:
                return None
            
            entry = self.cache[key]
            return {
                'key': entry.key,
                'created_at': entry.created_at.isoformat(),
                'accessed_at': entry.accessed_at.isoformat(),
                'ttl': entry.ttl,
                'access_count': entry.access_count,
                'is_expired': self._is_expired(entry),
                'size': self._estimate_size(entry.value)
            }
    
    def cleanup_expired(self) -> int:
        """
        Remove expired entries from cache.
        
        Returns:
            Number of entries removed
        """
        with self._lock:
            expired_keys = []
            
            for key, entry in self.cache.items():
                if self._is_expired(entry):
                    expired_keys.append(key)
            
            for key in expired_keys:
                self._remove_entry(key)
            
            if expired_keys:
                logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
            
            return len(expired_keys)
    
    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if a cache entry is expired."""
        if entry.ttl is None:
            return False
        
        expiry_time = entry.created_at + timedelta(seconds=entry.ttl)
        return datetime.utcnow() > expiry_time
    
    def _remove_entry(self, key: str) -> bool:
        """Remove an entry from cache."""
        if key not in self.cache:
            return False
        
        del self.cache[key]
        
        # Remove from policy-specific data structures
        if key in self.access_order:
            self.access_order.remove(key)
        if key in self.access_counts:
            del self.access_counts[key]
        
        self.stats['size'] = len(self.cache)
        return True
    
    def _evict_entry(self):
        """Evict an entry based on the cache policy."""
        if not self.cache:
            return
        
        if self.policy == CachePolicy.LRU:
            key_to_evict = self.access_order[0] if self.access_order else next(iter(self.cache))
        elif self.policy == CachePolicy.LFU:
            if self.access_counts:
                key_to_evict = min(self.access_counts, key=self.access_counts.get)
            else:
                key_to_evict = next(iter(self.cache))
        else:  # FIFO
            key_to_evict = next(iter(self.cache))
        
        self._remove_entry(key_to_evict)
        self.stats['evictions'] += 1
        logger.debug(f"Evicted cache entry: {key_to_evict}")
    
    def _update_access_info(self, key: str):
        """Update access information for a key."""
        if self.policy == CachePolicy.LRU:
            if key in self.access_order:
                self.access_order.remove(key)
            self.access_order.append(key)
        
        if self.policy == CachePolicy.LFU:
            self.access_counts[key] = self.access_counts.get(key, 0) + 1
    
    def _add_access_info(self, key: str):
        """Add access information for a new key."""
        if self.policy == CachePolicy.LRU:
            self.access_order.append(key)
        
        if self.policy == CachePolicy.LFU:
            self.access_counts[key] = 1
    
    def _estimate_size(self, value: Any) -> int:
        """Estimate the size of a cached value in bytes."""
        try:
            if isinstance(value, (str, bytes)):
                return len(value)
            elif isinstance(value, (int, float)):
                return 8
            elif isinstance(value, (list, tuple)):
                return sum(self._estimate_size(item) for item in value)
            elif isinstance(value, dict):
                return sum(self._estimate_size(k) + self._estimate_size(v) for k, v in value.items())
            else:
                return len(str(value))
        except:
            return 0
    
    def _start_cleanup_task(self):
        """Start the cleanup task."""
        async def cleanup_loop():
            while True:
                try:
                    await asyncio.sleep(300)  # Run every 5 minutes
                    self.cleanup_expired()
                except Exception as e:
                    logger.error(f"Error in cache cleanup: {e}")
        
        self._cleanup_task = asyncio.create_task(cleanup_loop())
    
    def stop_cleanup_task(self):
        """Stop the cleanup task."""
        if self._cleanup_task:
            self._cleanup_task.cancel()


class AsyncCacheManager:
    """
    Asynchronous cache manager wrapper.
    
    This class provides async methods for cache operations.
    """
    
    def __init__(self, cache_manager: CacheManager):
        """Initialize with a cache manager."""
        self.cache_manager = cache_manager
    
    async def get(self, key: str) -> Optional[Any]:
        """Async get operation."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.cache_manager.get, key)
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Async set operation."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.cache_manager.set, key, value, ttl)
    
    async def delete(self, key: str) -> bool:
        """Async delete operation."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.cache_manager.delete, key)
    
    async def exists(self, key: str) -> bool:
        """Async exists operation."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.cache_manager.exists, key)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Async get stats operation."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.cache_manager.get_stats)
    
    async def cleanup_expired(self) -> int:
        """Async cleanup operation."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.cache_manager.cleanup_expired)


# Global cache manager instances
_cache_manager = None
_async_cache_manager = None


def get_cache_manager() -> CacheManager:
    """Get the global cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


def get_async_cache_manager() -> AsyncCacheManager:
    """Get the global async cache manager instance."""
    global _async_cache_manager
    if _async_cache_manager is None:
        _async_cache_manager = AsyncCacheManager(get_cache_manager())
    return _async_cache_manager 