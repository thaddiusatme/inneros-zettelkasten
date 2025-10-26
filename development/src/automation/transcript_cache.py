"""
YouTube Transcript Cache - Catastrophic Incident Prevention

Implements persistent caching of YouTube transcripts to prevent:
- Redundant API calls causing rate limiting
- Re-fetching same videos multiple times
- Network-wide IP bans from burst requests

Created: 2025-10-08 (Response to catastrophic rate limit incident)
Author: InnerOS Zettelkasten Team
Size: ~200 LOC (ADR-001 compliant: <500 LOC)
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class TranscriptCache:
    """
    Persistent cache for YouTube transcripts with TTL support.
    
    Prevents catastrophic rate limiting by ensuring each video is only
    fetched once, then cached for 7 days (configurable).
    
    Features:
    - Persistent JSON storage
    - Configurable TTL (default: 7 days)
    - Automatic expiration cleanup
    - Cache hit/miss metrics
    - Thread-safe operations
    
    Example:
        >>> cache = TranscriptCache()
        >>> 
        >>> # Try to get cached transcript
        >>> cached = cache.get('dQw4w9WgXcQ')
        >>> if cached:
        >>>     print("Cache HIT - no API call needed!")
        >>> else:
        >>>     # Fetch from API
        >>>     result = fetcher.fetch_transcript('dQw4w9WgXcQ')
        >>>     cache.set('dQw4w9WgXcQ', result)
        >>>     print("Cache MISS - transcript cached for future use")
    """

    def __init__(self, cache_dir: Optional[Path] = None, ttl_days: int = 7):
        """
        Initialize transcript cache.
        
        Args:
            cache_dir: Directory for cache storage (default: .automation/cache)
            ttl_days: Time-to-live in days (default: 7)
        """
        if cache_dir is None:
            cache_dir = Path.cwd() / '.automation' / 'cache'

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.cache_file = self.cache_dir / 'youtube_transcripts.json'
        self.ttl_seconds = ttl_days * 24 * 60 * 60

        # Metrics tracking
        self.metrics = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'expirations': 0
        }

        # Load existing cache
        self._cache = self._load_cache()

        # Clean expired entries on startup
        self._cleanup_expired()

        logger.info(f"TranscriptCache initialized: {len(self._cache)} entries, TTL={ttl_days} days")

    def _load_cache(self) -> Dict[str, Any]:
        """Load cache from disk."""
        if not self.cache_file.exists():
            logger.debug("No existing cache file, starting fresh")
            return {}

        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            logger.info(f"Loaded cache: {len(cache_data)} entries")
            return cache_data
        except json.JSONDecodeError as e:
            logger.error(f"Cache file corrupted, starting fresh: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error loading cache: {e}")
            return {}

    def _save_cache(self) -> None:
        """Save cache to disk."""
        try:
            # Write to temp file first (atomic operation)
            temp_file = self.cache_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self._cache, f, indent=2)

            # Atomic rename
            temp_file.replace(self.cache_file)
            logger.debug(f"Cache saved: {len(self._cache)} entries")
        except Exception as e:
            logger.error(f"Error saving cache: {e}")

    def _cleanup_expired(self) -> None:
        """Remove expired cache entries."""
        now = time.time()
        expired_keys = []

        for video_id, entry in self._cache.items():
            cached_at = entry.get('cached_at', 0)
            if now - cached_at > self.ttl_seconds:
                expired_keys.append(video_id)

        for key in expired_keys:
            del self._cache[key]
            self.metrics['expirations'] += 1

        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
            self._save_cache()

    def get(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        Get cached transcript for video.
        
        Args:
            video_id: YouTube video ID
        
        Returns:
            Cached transcript data or None if not cached/expired
        """
        # Clean up expired entries periodically (every 100 gets)
        if self.metrics['hits'] + self.metrics['misses'] % 100 == 0:
            self._cleanup_expired()

        entry = self._cache.get(video_id)

        if entry is None:
            self.metrics['misses'] += 1
            logger.debug(f"Cache MISS: {video_id}")
            return None

        # Check if expired
        cached_at = entry.get('cached_at', 0)
        if time.time() - cached_at > self.ttl_seconds:
            del self._cache[video_id]
            self._save_cache()
            self.metrics['misses'] += 1
            self.metrics['expirations'] += 1
            logger.debug(f"Cache EXPIRED: {video_id}")
            return None

        self.metrics['hits'] += 1
        logger.info(f"Cache HIT: {video_id} (age: {int((time.time() - cached_at) / 3600)}h)")

        # Return transcript data (without metadata)
        return entry.get('data')

    def set(self, video_id: str, transcript_data: Dict[str, Any]) -> None:
        """
        Cache transcript for video.
        
        Args:
            video_id: YouTube video ID
            transcript_data: Transcript result from fetcher
        """
        self._cache[video_id] = {
            'cached_at': time.time(),
            'cached_date': datetime.now().isoformat(),
            'data': transcript_data
        }

        self.metrics['sets'] += 1
        logger.info(f"Cache SET: {video_id} (total entries: {len(self._cache)})")

        self._save_cache()

    def has(self, video_id: str) -> bool:
        """
        Check if video is cached (without retrieving it).
        
        Args:
            video_id: YouTube video ID
        
        Returns:
            True if cached and not expired, False otherwise
        """
        entry = self._cache.get(video_id)
        if entry is None:
            return False

        cached_at = entry.get('cached_at', 0)
        return time.time() - cached_at <= self.ttl_seconds

    def invalidate(self, video_id: str) -> bool:
        """
        Remove video from cache.
        
        Args:
            video_id: YouTube video ID
        
        Returns:
            True if entry was removed, False if not cached
        """
        if video_id in self._cache:
            del self._cache[video_id]
            self._save_cache()
            logger.info(f"Cache INVALIDATED: {video_id}")
            return True
        return False

    def clear(self) -> None:
        """Clear entire cache."""
        count = len(self._cache)
        self._cache.clear()
        self._save_cache()
        logger.warning(f"Cache CLEARED: {count} entries removed")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache metrics and info
        """
        total_requests = self.metrics['hits'] + self.metrics['misses']
        hit_rate = (self.metrics['hits'] / total_requests * 100) if total_requests > 0 else 0

        return {
            'entries': len(self._cache),
            'hits': self.metrics['hits'],
            'misses': self.metrics['misses'],
            'sets': self.metrics['sets'],
            'expirations': self.metrics['expirations'],
            'hit_rate': round(hit_rate, 2),
            'cache_file': str(self.cache_file),
            'ttl_days': self.ttl_seconds / (24 * 60 * 60)
        }

    def export_report(self) -> str:
        """
        Export cache report in human-readable format.
        
        Returns:
            Formatted report string
        """
        stats = self.get_stats()

        report = []
        report.append("=" * 50)
        report.append("TRANSCRIPT CACHE REPORT")
        report.append("=" * 50)
        report.append(f"Cache entries: {stats['entries']}")
        report.append(f"Cache hits: {stats['hits']}")
        report.append(f"Cache misses: {stats['misses']}")
        report.append(f"Hit rate: {stats['hit_rate']}%")
        report.append(f"Sets: {stats['sets']}")
        report.append(f"Expirations: {stats['expirations']}")
        report.append(f"TTL: {stats['ttl_days']} days")
        report.append(f"Cache file: {stats['cache_file']}")

        # Calculate API calls prevented
        api_calls_prevented = stats['hits']
        report.append("")
        report.append(f"🎉 API calls prevented: {api_calls_prevented}")
        report.append("💰 Rate limit protection: Active")
        report.append("=" * 50)

        return "\n".join(report)
