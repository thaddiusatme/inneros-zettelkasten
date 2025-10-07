"""
Job Execution Utilities - Job wrapping and execution tracking

Extracted utilities for job execution management, following ADR-001 single responsibility.
Provides reusable job wrapping, callback coordination, and execution monitoring.
"""

import time
from typing import Callable, Optional


class JobExecutionTracker:
    """
    Utilities for job execution wrapping and tracking.
    
    Provides reusable helper methods for:
    - Job function wrapping
    - Execution time measurement
    - Success/failure tracking
    - Callback coordination
    
    Size: ~120 LOC (ADR-001 compliant)
    """
    
    @staticmethod
    def wrap_job_with_tracking(
        job_id: str, 
        func: Callable, 
        execution_callback: Optional[Callable] = None
    ) -> Callable:
        """
        Wrap job function to track execution metrics.
        
        Automatically tracks:
        - Execution duration
        - Success/failure status
        - Exception handling
        
        Args:
            job_id: Unique job identifier
            func: Original function to wrap
            execution_callback: Optional callback for execution reporting
                                Signature: (job_id: str, success: bool, duration: float)
        
        Returns:
            Wrapped function with execution tracking
            
        Examples:
            >>> def my_job():
            ...     print("Running")
            >>> tracked = JobExecutionTracker.wrap_job_with_tracking(
            ...     "job1", my_job, lambda j, s, d: print(f"{j}: {s} in {d}s")
            ... )
            >>> tracked()
            Running
            job1: True in 0.001s
        """
        def wrapped():
            start_time = time.time()
            success = False
            
            try:
                result = func()
                success = True
                return result
            except Exception as e:
                success = False
                raise
            finally:
                duration = time.time() - start_time
                if execution_callback:
                    execution_callback(job_id, success, duration)
        
        return wrapped
    
    @staticmethod
    def measure_execution_time(func: Callable) -> tuple:
        """
        Measure function execution time.
        
        Args:
            func: Function to measure
            
        Returns:
            Tuple of (result, duration_seconds, success)
            
        Examples:
            >>> def fast_job():
            ...     return 42
            >>> result, duration, success = JobExecutionTracker.measure_execution_time(fast_job)
            >>> result
            42
            >>> success
            True
        """
        start_time = time.time()
        success = False
        result = None
        
        try:
            result = func()
            success = True
        except Exception:
            success = False
            raise
        finally:
            duration = time.time() - start_time
        
        return result, duration, success
    
    @staticmethod
    def create_execution_callback(
        on_success: Optional[Callable] = None,
        on_failure: Optional[Callable] = None,
        on_complete: Optional[Callable] = None
    ) -> Callable:
        """
        Create composite execution callback from multiple handlers.
        
        Args:
            on_success: Called when execution succeeds (job_id, duration)
            on_failure: Called when execution fails (job_id, duration)
            on_complete: Always called after execution (job_id, success, duration)
            
        Returns:
            Unified callback function
            
        Examples:
            >>> callback = JobExecutionTracker.create_execution_callback(
            ...     on_success=lambda j, d: print(f"{j} succeeded"),
            ...     on_failure=lambda j, d: print(f"{j} failed")
            ... )
            >>> callback("job1", True, 0.5)
            job1 succeeded
        """
        def callback(job_id: str, success: bool, duration: float):
            # Call specific handler
            if success and on_success:
                on_success(job_id, duration)
            elif not success and on_failure:
                on_failure(job_id, duration)
            
            # Always call complete handler
            if on_complete:
                on_complete(job_id, success, duration)
        
        return callback
    
    @staticmethod
    def safe_execute_job(func: Callable, job_id: str = "unknown") -> bool:
        """
        Execute job with exception handling.
        
        Args:
            func: Function to execute
            job_id: Job identifier for logging
            
        Returns:
            True if execution succeeded, False if failed
            
        Examples:
            >>> def failing_job():
            ...     raise ValueError("Error")
            >>> success = JobExecutionTracker.safe_execute_job(failing_job, "job1")
            >>> success
            False
        """
        try:
            func()
            return True
        except Exception as e:
            # Job failed, but don't propagate exception
            return False
