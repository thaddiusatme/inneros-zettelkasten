"""
Scheduler Manager - APScheduler integration wrapper

Manages job scheduling, execution tracking, and cron schedule parsing.
Follows ADR-001: <500 LOC, single responsibility, domain separation.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Callable, List, Optional
from apscheduler.schedulers.background import BackgroundScheduler

from .scheduler_utils import SchedulerUtils
from .job_utils import JobExecutionTracker


@dataclass
class JobInfo:
    """Scheduled job information"""

    id: str
    schedule: str
    next_run: Optional[datetime]


class SchedulerManager:
    """
    APScheduler integration for job management.

    Wraps BackgroundScheduler with simplified interface and execution tracking.
    Supports cron-based scheduling with job lifecycle management.

    Size: ~250 LOC (ADR-001 compliant)
    """

    def __init__(
        self,
        scheduler: BackgroundScheduler,
        execution_callback: Optional[Callable] = None,
    ):
        """
        Initialize scheduler manager.

        Args:
            scheduler: APScheduler BackgroundScheduler instance
            execution_callback: Optional callback for job execution tracking
                                Signature: (job_id: str, success: bool, duration: float)
        """
        self._scheduler = scheduler
        self._execution_callback = execution_callback

    def add_job(self, job_id: str, func: Callable, schedule: str) -> None:
        """
        Add cron-scheduled job.

        Args:
            job_id: Unique job identifier
            func: Function to execute
            schedule: Cron expression (e.g., "0 8 * * *" or "* * * * * */1")

        Raises:
            ValueError: If cron expression is invalid
        """
        # Wrap function to track execution using utilities
        wrapped_func = JobExecutionTracker.wrap_job_with_tracking(
            job_id, func, self._execution_callback
        )

        # Parse cron expression using utilities
        trigger = SchedulerUtils.parse_cron_schedule(schedule)

        # Add job to scheduler
        self._scheduler.add_job(
            wrapped_func, trigger=trigger, id=job_id, replace_existing=True
        )

    def remove_job(self, job_id: str) -> None:
        """
        Remove scheduled job.

        Args:
            job_id: Job identifier to remove
        """
        try:
            self._scheduler.remove_job(job_id)
        except Exception:
            # Job may not exist, ignore
            pass

    def list_jobs(self) -> List[JobInfo]:
        """
        Get all scheduled jobs.

        Returns:
            List of JobInfo with job metadata
        """
        jobs = []
        for job in self._scheduler.get_jobs():
            # Extract cron schedule string using utilities
            schedule = SchedulerUtils.format_trigger(job.trigger)

            jobs.append(
                JobInfo(id=job.id, schedule=schedule, next_run=job.next_run_time)
            )

        return jobs

    def pause_job(self, job_id: str) -> None:
        """
        Temporarily pause job execution.

        Args:
            job_id: Job identifier to pause
        """
        self._scheduler.pause_job(job_id)

    def resume_job(self, job_id: str) -> None:
        """
        Resume paused job.

        Args:
            job_id: Job identifier to resume
        """
        self._scheduler.resume_job(job_id)
