"""
Configuration Utilities - Config validation and parsing helpers

Extracted utilities for configuration management, following ADR-001 single responsibility.
Provides reusable schema validation, type checking, and default value injection.
"""

from typing import List, Any, Dict


class ConfigValidator:
    """
    Utilities for configuration validation and parsing.
    
    Provides reusable helper methods for:
    - Schema validation
    - Type checking (log levels, intervals)
    - Default value injection
    - Job configuration validation
    
    Size: ~80 LOC (ADR-001 compliant)
    """
    
    VALID_LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    
    @staticmethod
    def validate_daemon_section(daemon_config: Dict[str, Any]) -> List[str]:
        """
        Validate daemon configuration section.
        
        Args:
            daemon_config: Daemon configuration dictionary
            
        Returns:
            List of validation error messages
        """
        errors = []
        
        # Validate check_interval
        if "check_interval" in daemon_config:
            interval = daemon_config["check_interval"]
            if not isinstance(interval, int) or interval <= 0:
                errors.append("check_interval must be a positive integer")
        
        # Validate log_level
        if "log_level" in daemon_config:
            level = daemon_config["log_level"]
            if level not in ConfigValidator.VALID_LOG_LEVELS:
                errors.append(
                    f"log_level must be one of {ConfigValidator.VALID_LOG_LEVELS}, got '{level}'"
                )
        
        return errors
    
    @staticmethod
    def validate_jobs_section(jobs: Any) -> List[str]:
        """
        Validate jobs configuration section.
        
        Args:
            jobs: Jobs configuration (expected to be a list)
            
        Returns:
            List of validation error messages
        """
        errors = []
        
        if not isinstance(jobs, list):
            errors.append("jobs must be a list")
            return errors
        
        for idx, job in enumerate(jobs):
            if not isinstance(job, dict):
                errors.append(f"Job {idx} must be a dictionary")
                continue
            
            # Validate required job fields
            if "name" not in job:
                errors.append(f"Job {idx} missing required field 'name'")
            if "schedule" not in job:
                errors.append(f"Job {idx} missing required field 'schedule'")
        
        return errors
    
    @staticmethod
    def validate_raw_config(config: dict) -> List[str]:
        """
        Validate complete raw configuration dictionary.
        
        Args:
            config: Raw configuration dictionary
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Validate daemon section
        if "daemon" in config:
            errors.extend(ConfigValidator.validate_daemon_section(config["daemon"]))
        
        # Validate jobs section
        if "jobs" in config:
            errors.extend(ConfigValidator.validate_jobs_section(config["jobs"]))
        
        return errors
    
    @staticmethod
    def inject_defaults(raw_config: dict) -> Dict[str, Any]:
        """
        Inject default values into configuration.
        
        Args:
            raw_config: Raw configuration dictionary
            
        Returns:
            Configuration with defaults injected
        """
        config = raw_config.copy()
        
        # Inject daemon defaults
        if "daemon" not in config:
            config["daemon"] = {}
        
        daemon = config["daemon"]
        if "check_interval" not in daemon:
            daemon["check_interval"] = 60
        if "log_level" not in daemon:
            daemon["log_level"] = "INFO"
        
        # Inject jobs default
        if "jobs" not in config:
            config["jobs"] = []
        
        return config
    
    @staticmethod
    def validate_log_level(level: str) -> bool:
        """
        Check if log level is valid.
        
        Args:
            level: Log level string
            
        Returns:
            True if valid, False otherwise
        """
        return level in ConfigValidator.VALID_LOG_LEVELS
    
    @staticmethod
    def validate_check_interval(interval: Any) -> bool:
        """
        Check if check interval is valid.
        
        Args:
            interval: Check interval value
            
        Returns:
            True if valid (positive integer), False otherwise
        """
        return isinstance(interval, int) and interval > 0
