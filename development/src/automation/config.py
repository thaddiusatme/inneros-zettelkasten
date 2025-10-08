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
class ScreenshotHandlerConfig:
    """Screenshot handler configuration"""
    enabled: bool = False
    onedrive_path: str = ""
    knowledge_path: str = ""
    ocr_enabled: bool = True
    processing_timeout: int = 600


@dataclass
class SmartLinkHandlerConfig:
    """Smart link handler configuration"""
    enabled: bool = False
    vault_path: str = ""
    similarity_threshold: float = 0.75
    max_suggestions: int = 5
    auto_insert: bool = False


@dataclass
class YouTubeHandlerConfig:
    """YouTube handler configuration"""
    enabled: bool = False
    vault_path: str = ""
    max_quotes: int = 7
    min_quality: float = 0.7
    processing_timeout: int = 300


@dataclass
class DaemonConfig:
    """Daemon configuration"""
    check_interval: int = 60
    log_level: str = "INFO"
    jobs: List[JobConfig] = field(default_factory=list)
    file_watching: Optional[FileWatchConfig] = None
    screenshot_handler: Optional[ScreenshotHandlerConfig] = None
    smart_link_handler: Optional[SmartLinkHandlerConfig] = None
    youtube_handler: Optional[YouTubeHandlerConfig] = None


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
        
        # Parse file_watching section
        file_watching = None
        if "file_watching" in raw_config:
            fw_data = raw_config["file_watching"]
            file_watching = FileWatchConfig(
                enabled=fw_data.get("enabled", False),
                watch_path=fw_data.get("watch_path", ""),
                patterns=fw_data.get("patterns", ["*.md"]),
                ignore_patterns=fw_data.get("ignore_patterns", []),
                debounce_seconds=fw_data.get("debounce_seconds", 2.0)
            )
        
        # Parse screenshot_handler section
        screenshot_handler = None
        if "screenshot_handler" in raw_config:
            sh_data = raw_config["screenshot_handler"]
            screenshot_handler = ScreenshotHandlerConfig(
                enabled=sh_data.get("enabled", False),
                onedrive_path=sh_data.get("onedrive_path", ""),
                knowledge_path=sh_data.get("knowledge_path", ""),
                ocr_enabled=sh_data.get("ocr_enabled", True),
                processing_timeout=sh_data.get("processing_timeout", 600)
            )
        
        # Parse smart_link_handler section
        smart_link_handler = None
        if "smart_link_handler" in raw_config:
            sl_data = raw_config["smart_link_handler"]
            smart_link_handler = SmartLinkHandlerConfig(
                enabled=sl_data.get("enabled", False),
                vault_path=sl_data.get("vault_path", ""),
                similarity_threshold=sl_data.get("similarity_threshold", 0.75),
                max_suggestions=sl_data.get("max_suggestions", 5),
                auto_insert=sl_data.get("auto_insert", False)
            )
        
        # Parse youtube_handler section
        youtube_handler = None
        if "youtube_handler" in raw_config:
            yt_data = raw_config["youtube_handler"]
            youtube_handler = YouTubeHandlerConfig(
                enabled=yt_data.get("enabled", False),
                vault_path=yt_data.get("vault_path", ""),
                max_quotes=yt_data.get("max_quotes", 7),
                min_quality=yt_data.get("min_quality", 0.7),
                processing_timeout=yt_data.get("processing_timeout", 300)
            )
        
        return DaemonConfig(
            check_interval=check_interval,
            log_level=log_level,
            jobs=jobs,
            file_watching=file_watching,
            screenshot_handler=screenshot_handler,
            smart_link_handler=smart_link_handler,
            youtube_handler=youtube_handler
        )
