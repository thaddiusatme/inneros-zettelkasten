"""
Scheduler Utilities - Cron parsing and validation helpers

Extracted utilities for schedule management, following ADR-001 single responsibility.
Provides reusable cron expression validation, parsing, and formatting functions.
"""

from typing import Tuple, Optional
from apscheduler.triggers.cron import CronTrigger


class SchedulerUtils:
    """
    Utilities for cron schedule parsing and validation.
    
    Provides reusable helper methods for:
    - Cron expression validation
    - Format detection (5-field vs 6-field)
    - Trigger creation and formatting
    - Timezone handling
    
    Size: ~100 LOC (ADR-001 compliant)
    """
    
    @staticmethod
    def validate_cron_expression(schedule: str) -> Tuple[bool, Optional[str]]:
        """
        Validate cron expression format.
        
        Args:
            schedule: Cron expression string
            
        Returns:
            Tuple of (is_valid, error_message)
            
        Examples:
            >>> SchedulerUtils.validate_cron_expression("0 8 * * *")
            (True, None)
            >>> SchedulerUtils.validate_cron_expression("invalid")
            (False, "Invalid cron expression: must have 5 or 6 fields")
        """
        if not schedule or not isinstance(schedule, str):
            return False, "Cron expression must be a non-empty string"
        
        parts = schedule.split()
        
        if len(parts) not in (5, 6):
            return False, f"Invalid cron expression: must have 5 or 6 fields, got {len(parts)}"
        
        # Try creating a CronTrigger to validate syntax
        try:
            SchedulerUtils.parse_cron_schedule(schedule)
            return True, None
        except ValueError as e:
            return False, str(e)
    
    @staticmethod
    def detect_cron_format(schedule: str) -> str:
        """
        Detect cron expression format.
        
        Args:
            schedule: Cron expression string
            
        Returns:
            "extended" for 6-field (with seconds), "standard" for 5-field
            
        Raises:
            ValueError: If schedule is invalid
        """
        parts = schedule.split()
        
        if len(parts) == 6:
            return "extended"
        elif len(parts) == 5:
            return "standard"
        else:
            raise ValueError(f"Invalid cron expression: {schedule}")
    
    @staticmethod
    def parse_cron_schedule(schedule: str) -> CronTrigger:
        """
        Parse cron expression into APScheduler trigger.
        
        Supports both standard cron (5 fields) and extended cron (6 fields with seconds).
        
        Args:
            schedule: Cron expression string
            
        Returns:
            CronTrigger instance
            
        Raises:
            ValueError: If cron expression is invalid
            
        Examples:
            Standard: "0 8 * * *" -> minute=0, hour=8, day=*, month=*, day_of_week=*
            Extended: "0 0 8 * * *" -> second=0, minute=0, hour=8, ...
        """
        parts = schedule.split()
        
        if len(parts) == 6:
            # Extended cron with seconds: second minute hour day month day_of_week
            return CronTrigger(
                second=parts[0],
                minute=parts[1],
                hour=parts[2],
                day=parts[3],
                month=parts[4],
                day_of_week=parts[5]
            )
        elif len(parts) == 5:
            # Standard cron: minute hour day month day_of_week
            return CronTrigger(
                minute=parts[0],
                hour=parts[1],
                day=parts[2],
                month=parts[3],
                day_of_week=parts[4]
            )
        else:
            raise ValueError(f"Invalid cron expression: {schedule}")
    
    @staticmethod
    def format_trigger(trigger) -> str:
        """
        Format APScheduler trigger as cron string.
        
        Args:
            trigger: APScheduler trigger object
            
        Returns:
            Cron expression string
            
        Examples:
            CronTrigger(minute=0, hour=8) -> "0 8 * * *"
            CronTrigger(second=0, minute=0, hour=8) -> "0 0 8 * * *"
        """
        if isinstance(trigger, CronTrigger):
            fields = trigger.fields
            parts = []
            
            # Check if seconds field exists (6-field format)
            if len(fields) == 6:
                parts = [
                    str(fields[0]),  # second
                    str(fields[1]),  # minute
                    str(fields[2]),  # hour
                    str(fields[3]),  # day
                    str(fields[4]),  # month
                    str(fields[5]),  # day_of_week
                ]
            else:
                # 5-field format (no seconds)
                parts = [
                    str(fields[0]),  # minute
                    str(fields[1]),  # hour
                    str(fields[2]),  # day
                    str(fields[3]),  # month
                    str(fields[4]),  # day_of_week
                ]
            
            return " ".join(parts)
        
        return str(trigger)
    
    @staticmethod
    def normalize_cron_expression(schedule: str) -> str:
        """
        Normalize cron expression to canonical form.
        
        Validates and returns a standardized version of the cron expression.
        
        Args:
            schedule: Cron expression string
            
        Returns:
            Normalized cron expression
            
        Raises:
            ValueError: If expression is invalid
        """
        # Validate first
        is_valid, error = SchedulerUtils.validate_cron_expression(schedule)
        if not is_valid:
            raise ValueError(error)
        
        # Parse and format to normalize
        trigger = SchedulerUtils.parse_cron_schedule(schedule)
        return SchedulerUtils.format_trigger(trigger)
