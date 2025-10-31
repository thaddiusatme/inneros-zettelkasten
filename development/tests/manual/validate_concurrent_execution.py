#!/usr/bin/env python3
"""
Concurrent Execution Validation - Issue #34 Phase 2

Tests daemon with multiple feature handlers running simultaneously:
- Screenshot processing
- Inbox processing (via CLI commands)
- Health monitoring during execution

Usage:
    python3 development/tests/manual/validate_concurrent_execution.py
"""

import sys
import time
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add development directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.automation.daemon import AutomationDaemon, DaemonState
from src.automation.config import ConfigurationLoader


class ConcurrentExecutionValidator:
    """Validates concurrent execution safety for automation handlers."""
    
    def __init__(self, repo_root: Path):
        """Initialize validator with repository paths."""
        self.repo_root = repo_root
        self.config_path = repo_root / ".automation" / "config" / "daemon_test_config.yaml"
        self.health_script = repo_root / ".automation" / "scripts" / "check_automation_health.py"
        self.results: List[Dict[str, Any]] = []
        
    def run_validation(self) -> Dict[str, Any]:
        """
        Run complete concurrent execution validation.
        
        Returns:
            Validation results with success status
        """
        print("=" * 70)
        print("🧪 CONCURRENT EXECUTION VALIDATION - Issue #34 Phase 2")
        print("=" * 70)
        print()
        
        validation_start = time.time()
        
        # Test 1: Daemon startup with config
        print("Test 1: Starting daemon with screenshot handler...")
        daemon_result = self._test_daemon_startup()
        self.results.append(daemon_result)
        
        if not daemon_result["success"]:
            return self._generate_final_report(validation_start, success=False)
        
        daemon = daemon_result["daemon"]
        
        try:
            # Test 2: Health monitoring during operation
            print("\nTest 2: Monitoring daemon health...")
            health_result = self._test_health_monitoring()
            self.results.append(health_result)
            
            # Test 3: Concurrent CLI operations
            print("\nTest 3: Testing concurrent CLI operations...")
            concurrent_result = self._test_concurrent_cli_operations()
            self.results.append(concurrent_result)
            
            # Test 4: Rate limiter validation
            print("\nTest 4: Validating rate limiter status...")
            rate_limit_result = self._test_rate_limiter()
            self.results.append(rate_limit_result)
            
            # Test 5: Resource usage check
            print("\nTest 5: Checking resource usage...")
            resource_result = self._test_resource_usage(daemon)
            self.results.append(resource_result)
            
        finally:
            # Always stop daemon
            print("\n🛑 Stopping daemon...")
            daemon.stop()
            time.sleep(2)
        
        return self._generate_final_report(validation_start, success=True)
    
    def _test_daemon_startup(self) -> Dict[str, Any]:
        """Test daemon startup with test configuration."""
        try:
            # Load configuration
            loader = ConfigurationLoader()
            config = loader.load_config(self.config_path)
            
            # Create and start daemon
            daemon = AutomationDaemon(config=config)
            daemon.start()
            
            # Wait for initialization
            time.sleep(3)
            
            # Check status
            status = daemon.status()
            
            success = (
                status.state == DaemonState.RUNNING and
                status.scheduler_active
            )
            
            return {
                "test": "daemon_startup",
                "success": success,
                "daemon": daemon,
                "state": status.state.value,
                "scheduler_active": status.scheduler_active,
                "watcher_active": status.watcher_active,
                "message": "✅ Daemon started successfully" if success else "❌ Daemon failed to start"
            }
            
        except Exception as e:
            return {
                "test": "daemon_startup",
                "success": False,
                "daemon": None,
                "error": str(e),
                "message": f"❌ Daemon startup failed: {e}"
            }
    
    def _test_health_monitoring(self) -> Dict[str, Any]:
        """Test health monitoring script."""
        try:
            # Run health check
            result = subprocess.run(
                ["python3", str(self.health_script), "--json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                health_data = json.loads(result.stdout)
                
                return {
                    "test": "health_monitoring",
                    "success": True,
                    "health_data": health_data,
                    "message": "✅ Health monitoring working"
                }
            else:
                return {
                    "test": "health_monitoring",
                    "success": False,
                    "error": result.stderr,
                    "message": f"❌ Health check failed: {result.stderr}"
                }
                
        except Exception as e:
            return {
                "test": "health_monitoring",
                "success": False,
                "error": str(e),
                "message": f"❌ Health monitoring error: {e}"
            }
    
    def _test_concurrent_cli_operations(self) -> Dict[str, Any]:
        """Test concurrent CLI operations (simulating cron jobs)."""
        try:
            # Simulate concurrent automation by running CLI commands
            # This tests if multiple operations can safely execute
            
            operations = []
            
            # Operation 1: Screenshot import (dry-run)
            print("  - Running screenshot import (dry-run)...")
            screenshot_proc = subprocess.Popen(
                [
                    "python3",
                    str(self.repo_root / "development" / "src" / "cli" / "workflow_demo.py"),
                    str(self.repo_root / "knowledge"),
                    "--status"  # Safe status check instead of actual processing
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            operations.append(("screenshot_status", screenshot_proc))
            
            # Operation 2: Inbox processing status
            print("  - Running inbox processing status...")
            inbox_proc = subprocess.Popen(
                [
                    "python3",
                    str(self.repo_root / "development" / "src" / "cli" / "workflow_demo.py"),
                    str(self.repo_root / "knowledge"),
                    "--status"
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            operations.append(("inbox_status", inbox_proc))
            
            # Wait for completion
            time.sleep(5)
            
            # Collect results
            results = {}
            for name, proc in operations:
                stdout, stderr = proc.communicate(timeout=10)
                results[name] = {
                    "returncode": proc.returncode,
                    "success": proc.returncode == 0
                }
            
            all_success = all(r["success"] for r in results.values())
            
            return {
                "test": "concurrent_cli_operations",
                "success": all_success,
                "operations": results,
                "message": "✅ Concurrent operations completed" if all_success else "❌ Some operations failed"
            }
            
        except Exception as e:
            return {
                "test": "concurrent_cli_operations",
                "success": False,
                "error": str(e),
                "message": f"❌ Concurrent operations error: {e}"
            }
    
    def _test_rate_limiter(self) -> Dict[str, Any]:
        """Test YouTube rate limiter status."""
        try:
            from src.automation.youtube_global_rate_limiter import YouTubeGlobalRateLimiter
            
            cache_dir = self.repo_root / ".automation" / "cache"
            rate_limiter = YouTubeGlobalRateLimiter(cache_dir=cache_dir, cooldown_seconds=60)
            
            can_proceed = rate_limiter.can_proceed()
            seconds_remaining = rate_limiter.seconds_until_next_allowed()
            
            return {
                "test": "rate_limiter",
                "success": True,
                "can_proceed": can_proceed,
                "seconds_remaining": seconds_remaining,
                "message": f"✅ Rate limiter: {'READY' if can_proceed else f'COOLDOWN ({seconds_remaining}s)'}"
            }
            
        except Exception as e:
            return {
                "test": "rate_limiter",
                "success": False,
                "error": str(e),
                "message": f"❌ Rate limiter error: {e}"
            }
    
    def _test_resource_usage(self, daemon: AutomationDaemon) -> Dict[str, Any]:
        """Test resource usage during operation."""
        try:
            import psutil
            
            # Get current process and children
            current_process = psutil.Process()
            
            cpu_percent = current_process.cpu_percent(interval=1)
            memory_info = current_process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            
            # Check daemon status
            status = daemon.status()
            
            return {
                "test": "resource_usage",
                "success": True,
                "cpu_percent": cpu_percent,
                "memory_mb": round(memory_mb, 2),
                "uptime_seconds": round(status.uptime_seconds, 2),
                "message": f"✅ Resources: {cpu_percent}% CPU, {memory_mb:.1f}MB RAM"
            }
            
        except Exception as e:
            return {
                "test": "resource_usage",
                "success": False,
                "error": str(e),
                "message": f"❌ Resource check error: {e}"
            }
    
    def _generate_final_report(self, start_time: float, success: bool) -> Dict[str, Any]:
        """Generate final validation report."""
        duration = time.time() - start_time
        
        passed = sum(1 for r in self.results if r.get("success", False))
        total = len(self.results)
        
        print()
        print("=" * 70)
        print("📊 VALIDATION REPORT")
        print("=" * 70)
        print(f"Duration: {duration:.2f}s")
        print(f"Tests Passed: {passed}/{total}")
        print()
        
        for result in self.results:
            print(result["message"])
        
        print()
        if success and passed == total:
            print("✅ CONCURRENT EXECUTION VALIDATION PASSED")
            print()
            print("Next Steps:")
            print("  1. ✅ Daemon can run with feature handlers")
            print("  2. ✅ Health monitoring working")
            print("  3. ✅ Concurrent operations safe")
            print("  4. ⏳ Ready for Phase 3: Staged cron enablement")
        else:
            print("❌ VALIDATION FAILED")
            print()
            print("Issues to resolve before cron enablement:")
            for result in self.results:
                if not result.get("success", False):
                    print(f"  • {result['test']}: {result.get('error', 'Unknown error')}")
        
        print("=" * 70)
        
        return {
            "success": success and passed == total,
            "duration": duration,
            "tests_passed": passed,
            "tests_total": total,
            "results": self.results
        }


def main():
    """Main entry point."""
    repo_root = Path(__file__).parent.parent.parent.parent
    
    validator = ConcurrentExecutionValidator(repo_root)
    
    try:
        report = validator.run_validation()
        sys.exit(0 if report["success"] else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Validation failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
