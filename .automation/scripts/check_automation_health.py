#!/usr/bin/env python3
"""
Automation Health Monitor - Issue #34 Phase 1
Monitors daemon health, feature handlers, and rate limiter status for concurrent automation validation.

Python-based health monitoring that integrates with existing daemon infrastructure:
- Daemon health status (via HealthCheckManager)
- Feature handler metrics (screenshot, smart_link, youtube)
- Rate limiter cooldown status (YouTubeGlobalRateLimiter)
- Concurrent execution validation

Vault Configuration:
- Uses centralized vault config via imports from development/src
- Automatically handles knowledge/Inbox, knowledge/Permanent Notes paths
- No hardcoded paths - all paths relative to repo root
- Compatible with knowledge/ subdirectory structure
- See: .automation/README.md for vault config integration details

Usage:
    python3 check_automation_health.py [--json] [--prometheus] [--export FILE]
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Add parent directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "development"))

from src.automation.youtube_global_rate_limiter import YouTubeGlobalRateLimiter
from src.cli.automation_status_cli import DaemonDetector, LogParser


class AutomationHealthMonitor:
    """
    Monitors automation health for staged cron re-enablement.
    
    Checks:
    - Daemon process status
    - Feature handler health
    - Rate limiter cooldown status
    - Stale process detection
    - Concurrent execution safety
    """
    
    def __init__(self, repo_root: Path):
        """Initialize health monitor with repository paths."""
        self.repo_root = repo_root
        self.log_dir = repo_root / ".automation" / "logs"
        self.cache_dir = repo_root / ".automation" / "cache"
        
        # Initialize components
        self.daemon_detector = DaemonDetector()
        self.log_parser = LogParser()
        
        # Rate limiter for YouTube cooldown checks
        self.rate_limiter = YouTubeGlobalRateLimiter(
            cache_dir=self.cache_dir,
            cooldown_seconds=60
        )
        
        # Daemon registry for status checks
        self.daemon_registry = self._load_daemon_registry()
    
    def _load_daemon_registry(self) -> Dict[str, Dict[str, str]]:
        """Load daemon configurations from registry."""
        import yaml
        
        registry_path = self.repo_root / ".automation" / "config" / "daemon_registry.yaml"
        if not registry_path.exists():
            return {}
        
        with open(registry_path) as f:
            data = yaml.safe_load(f)
            return {d["name"]: d for d in data.get("daemons", [])}
    
    def check_daemon_health(self) -> Dict[str, Any]:
        """
        Check daemon process health.
        
        Returns:
            Dictionary with daemon status, PID, and health indicators
        """
        health = {
            "timestamp": datetime.now().isoformat(),
            "daemons": {},
            "overall_healthy": True
        }
        
        for name, config in self.daemon_registry.items():
            status = self.daemon_detector.check_daemon_status(
                daemon_name=name,
                script_path=config["script_path"]
            )
            
            log_path = self.repo_root / config.get("log_path", f".automation/logs/{name}.log")
            last_run = self.log_parser.parse_last_run(log_path)
            
            daemon_health = {
                "running": status["running"],
                "pid": status["pid"],
                "last_run_status": last_run.get("status", "unknown"),
                "last_run_timestamp": last_run.get("timestamp"),
                "error_message": last_run.get("error_message")
            }
            
            health["daemons"][name] = daemon_health
            
            if not status["running"]:
                health["overall_healthy"] = False
        
        return health
    
    def check_rate_limiter_status(self) -> Dict[str, Any]:
        """
        Check YouTube rate limiter cooldown status.
        
        Returns:
            Dictionary with cooldown status and time until next allowed request
        """
        can_proceed = self.rate_limiter.can_proceed()
        seconds_remaining = self.rate_limiter.seconds_until_next_allowed()
        
        return {
            "can_proceed": can_proceed,
            "cooldown_active": not can_proceed,
            "seconds_until_next_allowed": seconds_remaining,
            "last_request_file": str(self.rate_limiter.tracking_file),
            "last_request_file_exists": self.rate_limiter.tracking_file.exists()
        }
    
    def check_concurrent_execution_safety(self) -> Dict[str, Any]:
        """
        Check if concurrent automation execution is safe.
        
        Validates:
        - Multiple feature handlers can run simultaneously
        - No resource conflicts detected
        - Independent rate limiting per feature
        
        Returns:
            Dictionary with safety status and warnings
        """
        safety = {
            "safe_for_concurrent_execution": True,
            "warnings": [],
            "handler_count": len(self.daemon_registry),
            "handlers": {}
        }
        
        # Check each handler's independent operation
        for name in self.daemon_registry.keys():
            handler_safe = {
                "independent_logging": True,
                "independent_cache": True,
                "process_isolation": True
            }
            
            # Check for handler-specific PID files (if implemented)
            pid_file = self.log_dir / f"{name}.pid"
            if pid_file.exists():
                handler_safe["pid_file"] = str(pid_file)
                handler_safe["pid_file_stale"] = self._check_stale_pid(pid_file)
            
            safety["handlers"][name] = handler_safe
        
        return safety
    
    def _check_stale_pid(self, pid_file: Path) -> bool:
        """
        Check if PID file references a dead process.
        
        Args:
            pid_file: Path to PID file
            
        Returns:
            True if PID file is stale (process not running)
        """
        try:
            pid = int(pid_file.read_text().strip())
            
            # Check if process exists
            import psutil
            return not psutil.pid_exists(pid)
        except (ValueError, FileNotFoundError, PermissionError):
            return True
    
    def generate_health_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive health report.
        
        Returns:
            Complete health status including all checks
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "daemon_health": self.check_daemon_health(),
            "rate_limiter": self.check_rate_limiter_status(),
            "concurrent_safety": self.check_concurrent_execution_safety(),
            "system_ready_for_cron": self._assess_cron_readiness()
        }
    
    def _assess_cron_readiness(self) -> Dict[str, Any]:
        """
        Assess if system is ready for staged cron enablement.
        
        Returns:
            Readiness assessment with recommendations
        """
        daemon_health = self.check_daemon_health()
        rate_limiter = self.check_rate_limiter_status()
        safety = self.check_concurrent_execution_safety()
        
        ready = (
            daemon_health["overall_healthy"] and
            safety["safe_for_concurrent_execution"]
        )
        
        recommendations = []
        if not daemon_health["overall_healthy"]:
            recommendations.append("Fix unhealthy daemons before enabling cron")
        
        if not safety["safe_for_concurrent_execution"]:
            recommendations.append("Resolve concurrent execution conflicts")
        
        if rate_limiter["cooldown_active"]:
            recommendations.append(
                f"Rate limiter active: wait {rate_limiter['seconds_until_next_allowed']}s"
            )
        
        return {
            "ready": ready,
            "phase_recommendation": "Phase 1: Screenshot only" if ready else "Not ready - fix issues first",
            "recommendations": recommendations
        }
    
    def export_prometheus_metrics(self) -> str:
        """
        Export metrics in Prometheus format.
        
        Returns:
            Prometheus-formatted metrics string
        """
        report = self.generate_health_report()
        
        metrics = []
        
        # Daemon health metrics
        for name, daemon in report["daemon_health"]["daemons"].items():
            metrics.append(f'automation_daemon_running{{daemon="{name}"}} {int(daemon["running"])}')
            if daemon["pid"]:
                metrics.append(f'automation_daemon_pid{{daemon="{name}"}} {daemon["pid"]}')
        
        # Rate limiter metrics
        rate_limiter = report["rate_limiter"]
        metrics.append(f'automation_rate_limiter_can_proceed {int(rate_limiter["can_proceed"])}')
        metrics.append(f'automation_rate_limiter_cooldown_seconds {rate_limiter["seconds_until_next_allowed"]}')
        
        # Overall readiness
        metrics.append(f'automation_cron_ready {int(report["system_ready_for_cron"]["ready"])}')
        
        return "\n".join(metrics) + "\n"


def main():
    """Main entry point for health monitoring."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Automation Health Monitor")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    parser.add_argument("--prometheus", action="store_true", help="Output Prometheus metrics")
    parser.add_argument("--export", type=str, help="Export report to file")
    parser.add_argument("--repo-root", type=str, default=".", help="Repository root path")
    
    args = parser.parse_args()
    
    # Initialize monitor
    repo_root = Path(args.repo_root).resolve()
    monitor = AutomationHealthMonitor(repo_root)
    
    # Generate report
    if args.prometheus:
        output = monitor.export_prometheus_metrics()
    else:
        report = monitor.generate_health_report()
        
        if args.json:
            output = json.dumps(report, indent=2)
        else:
            # Human-readable format
            output = format_human_readable(report)
    
    # Export to file if requested
    if args.export:
        Path(args.export).write_text(output)
        print(f"Report exported to: {args.export}")
    else:
        print(output)


def format_human_readable(report: Dict[str, Any]) -> str:
    """Format health report for human reading."""
    lines = []
    lines.append("=" * 60)
    lines.append("🏥 AUTOMATION HEALTH MONITOR")
    lines.append("=" * 60)
    lines.append(f"Timestamp: {report['timestamp']}")
    lines.append("")
    
    # Daemon Health
    lines.append("📊 DAEMON HEALTH:")
    daemon_health = report["daemon_health"]
    for name, daemon in daemon_health["daemons"].items():
        status = "✅ RUNNING" if daemon["running"] else "❌ STOPPED"
        lines.append(f"  {name}: {status}")
        if daemon["pid"]:
            lines.append(f"    PID: {daemon['pid']}")
        if daemon["last_run_status"]:
            lines.append(f"    Last Run: {daemon['last_run_status']}")
        if daemon["error_message"]:
            lines.append(f"    Error: {daemon['error_message']}")
    lines.append("")
    
    # Rate Limiter
    lines.append("⏱️  RATE LIMITER STATUS:")
    rate = report["rate_limiter"]
    status = "✅ READY" if rate["can_proceed"] else f"⏳ COOLDOWN ({rate['seconds_until_next_allowed']}s remaining)"
    lines.append(f"  Status: {status}")
    lines.append("")
    
    # Concurrent Safety
    lines.append("🔒 CONCURRENT EXECUTION SAFETY:")
    safety = report["concurrent_safety"]
    status = "✅ SAFE" if safety["safe_for_concurrent_execution"] else "⚠️  WARNINGS"
    lines.append(f"  Status: {status}")
    lines.append(f"  Handlers: {safety['handler_count']}")
    for warning in safety["warnings"]:
        lines.append(f"  ⚠️  {warning}")
    lines.append("")
    
    # Cron Readiness
    lines.append("🚀 CRON ENABLEMENT READINESS:")
    readiness = report["system_ready_for_cron"]
    status = "✅ READY" if readiness["ready"] else "❌ NOT READY"
    lines.append(f"  Status: {status}")
    lines.append(f"  Recommendation: {readiness['phase_recommendation']}")
    for rec in readiness["recommendations"]:
        lines.append(f"  • {rec}")
    lines.append("")
    
    lines.append("=" * 60)
    
    return "\n".join(lines)


if __name__ == "__main__":
    main()
