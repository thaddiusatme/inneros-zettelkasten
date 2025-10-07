"""
Configuration Loader - YAML configuration loading and validation

Loads daemon configuration from YAML files with schema validation.
Follows ADR-001: <500 LOC, single responsibility, domain separation.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
import yaml

from .config_utils import ConfigValidator


@dataclass
class JobConfig:
    """Job configuration"""
    name: str
    schedule: str
    enabled: bool = True
    description: Optional[str] = None


@dataclass
class FileWatchConfig:
    """File watching configuration"""
    enabled: bool = False
    watch_path: str = ""
    patterns: List[str] = field(default_factory=lambda: ["*.md"])
    ignore_patterns: List[str] = field(default_factory=list)
    debounce_seconds: float = 2.0


@dataclass
class DaemonConfig:
    """Daemon configuration"""
    check_interval: int = 60
    log_level: str = "INFO"
    jobs: List[JobConfig] = field(default_factory=list)
    file_watching: Optional[FileWatchConfig] = None


class ConfigurationLoader:
    """
    Configuration loading and validation.
    
    Loads YAML configuration files with schema validation.
    Provides default configuration and validation error reporting.
    
    Size: ~150 LOC (ADR-001 compliant)
    """
    
    def load_config(self, path: Path) -> DaemonConfig:
        """
        Load and validate YAML config file.
        
        Args:
            path: Path to YAML configuration file
            
        Returns:
            DaemonConfig object with validated configuration
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config is invalid
            yaml.YAMLError: If YAML parsing fails
        """
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")
        
        # Load YAML
        with open(path, 'r') as f:
            raw_config = yaml.safe_load(f)
        
        if not raw_config:
            raise ValueError("Configuration file is empty")
        
        # Validate and construct config object using validator
        errors = ConfigValidator.validate_raw_config(raw_config)
        if errors:
            raise ValueError(f"Configuration validation errors: {'; '.join(errors)}")
        
        return self._parse_config(raw_config)
    
    def validate_config_file(self, path: Path) -> List[str]:
        """
        Validate config file and return errors.
        
        Args:
            path: Path to configuration file
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Check file exists
        if not path.exists():
            errors.append(f"Configuration file not found: {path}")
            return errors
        
        # Load and validate YAML
        try:
            with open(path, 'r') as f:
                raw_config = yaml.safe_load(f)
            
            if not raw_config:
                errors.append("Configuration file is empty")
                return errors
            
            # Validate configuration using validator
            errors.extend(ConfigValidator.validate_raw_config(raw_config))
            
        except yaml.YAMLError as e:
            errors.append(f"YAML parsing error: {e}")
        except Exception as e:
            errors.append(f"Error reading config: {e}")
        
        return errors
    
    def get_default_config(self) -> DaemonConfig:
        """
        Get safe default configuration.
        
        Returns:
            DaemonConfig with default values
        """
        return DaemonConfig(
            check_interval=60,
            log_level="INFO",
            jobs=[]
        )
    
    def _parse_config(self, raw_config: dict) -> DaemonConfig:
        """
        Parse raw configuration into DaemonConfig object.
        
        Args:
            raw_config: Raw configuration dictionary
            
        Returns:
            DaemonConfig object
        """
        # Parse daemon section
        daemon_section = raw_config.get("daemon", {})
        check_interval = daemon_section.get("check_interval", 60)
        log_level = daemon_section.get("log_level", "INFO")
        
        # Parse jobs section
        jobs = []
        jobs_section = raw_config.get("jobs", [])
        
        for job_data in jobs_section:
            job = JobConfig(
                name=job_data["name"],
                schedule=job_data["schedule"],
                enabled=job_data.get("enabled", True),
                description=job_data.get("description")
            )
            jobs.append(job)
        
        return DaemonConfig(
            check_interval=check_interval,
            log_level=log_level,
            jobs=jobs
        )
