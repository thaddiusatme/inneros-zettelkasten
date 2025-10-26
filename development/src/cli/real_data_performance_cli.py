"""
TDD Iteration 5 REFACTOR Phase: Real Data Performance CLI
Production-ready CLI interface integrating performance validation with existing utilities

REFACTOR Phase: Production-ready architecture with comprehensive integration
"""

import time
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Import our existing CLI architecture from Iteration 4
from .safe_workflow_cli_utils import SafeWorkflowCLI

# Import our new performance validation implementations
from .real_data_performance_validator import RealDataPerformanceValidator
from .memory_usage_monitor import MemoryUsageMonitor
from .concurrent_processing_manager import ConcurrentProcessingManager
from .performance_metrics_collector import PerformanceMetricsCollector
from .stress_test_manager import StressTestManager
from .real_time_progress_reporter import RealTimeProgressReporter


class RealDataPerformanceCLI:
    """
    REFACTOR Phase: Production-ready CLI for real data performance validation
    Integrates with existing SafeWorkflowCLI architecture from Iteration 4
    """

    def __init__(self, vault_path: str, max_concurrent: int = 3):
        self.vault_path = vault_path
        self.max_concurrent = max_concurrent

        # Integration with existing CLI utilities
        self.safe_cli = SafeWorkflowCLI(vault_path, max_concurrent)

        # Performance validation components
        self.validator = RealDataPerformanceValidator(vault_path)
        self.memory_monitor = MemoryUsageMonitor()
        self.concurrent_manager = ConcurrentProcessingManager(vault_path, max_concurrent)
        self.metrics_collector = PerformanceMetricsCollector()
        self.stress_manager = StressTestManager(vault_path)
        self.progress_reporter = RealTimeProgressReporter()

        self.performance_history = []

    def run_performance_benchmark(self, benchmark_type: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        REFACTOR Phase: Run comprehensive performance benchmarks
        Production-ready with full error handling and reporting
        """
        options = options or {}
        start_time = time.time()

        try:
            if benchmark_type == "small_batch":
                return self._run_small_batch_benchmark(options)
            elif benchmark_type == "medium_batch":
                return self._run_medium_batch_benchmark(options)
            elif benchmark_type == "large_batch":
                return self._run_large_batch_benchmark(options)
            elif benchmark_type == "memory_validation":
                return self._run_memory_validation_benchmark(options)
            elif benchmark_type == "concurrent_processing":
                return self._run_concurrent_processing_benchmark(options)
            elif benchmark_type == "stress_test":
                return self._run_stress_test_benchmark(options)
            else:
                return {
                    "success": False,
                    "error": f"Unknown benchmark type: {benchmark_type}",
                    "available_types": ["small_batch", "medium_batch", "large_batch",
                                      "memory_validation", "concurrent_processing", "stress_test"]
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "benchmark_type": benchmark_type,
                "execution_time": time.time() - start_time
            }

    def _run_small_batch_benchmark(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """REFACTOR: Small batch benchmark with <30s target"""
        test_notes = self._generate_test_notes(10, "small_batch")

        with self.memory_monitor.track_memory_usage():
            result = self.validator.process_notes_with_performance_tracking(test_notes)

        return {
            "success": result["success"],
            "benchmark_type": "small_batch",
            "target_time": 30,
            "actual_time": result.get("processing_time", 0),
            "meets_target": result.get("processing_time", 0) < 30,
            "processed_count": result.get("processed_count", 0),
            "memory_usage_mb": self.memory_monitor.get_peak_memory_usage_mb(),
            "performance_metrics": result.get("performance_metrics", {})
        }

    def _run_medium_batch_benchmark(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """REFACTOR: Medium batch benchmark with <2min target"""
        test_notes = self._generate_test_notes(50, "medium_batch")

        with self.memory_monitor.track_memory_usage():
            result = self.validator.process_notes_with_performance_tracking(test_notes)

        return {
            "success": result["success"],
            "benchmark_type": "medium_batch",
            "target_time": 120,
            "actual_time": result.get("processing_time", 0),
            "meets_target": result.get("processing_time", 0) < 120,
            "processed_count": result.get("processed_count", 0),
            "memory_usage_mb": self.memory_monitor.get_peak_memory_usage_mb(),
            "performance_metrics": result.get("performance_metrics", {})
        }

    def _run_large_batch_benchmark(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """REFACTOR: Large batch benchmark with <5min target (CRITICAL)"""
        test_notes = self._generate_test_notes(100, "large_batch")

        with self.memory_monitor.track_memory_usage():
            # Add progress reporting for large batches
            result = self.validator.process_notes_with_progress_reporting(
                test_notes, self.progress_reporter
            )

        return {
            "success": result["success"],
            "benchmark_type": "large_batch",
            "target_time": 300,  # 5 minutes
            "actual_time": result.get("processing_time", 0),
            "meets_target": result.get("processing_time", 0) < 300,
            "processed_count": result.get("processed_count", 0),
            "memory_usage_mb": self.memory_monitor.get_peak_memory_usage_mb(),
            "progress_updates": len(self.progress_reporter.get_updates()),
            "performance_metrics": result.get("performance_metrics", {})
        }

    def _run_memory_validation_benchmark(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """REFACTOR: Memory validation with <512MB target"""
        test_notes = self._generate_test_notes(100, "memory_validation")

        with self.memory_monitor.track_memory_usage():
            result = self.validator.process_notes_with_metrics_collection(
                test_notes, self.metrics_collector
            )

        peak_memory = self.memory_monitor.get_peak_memory_usage_mb()

        return {
            "success": result["success"],
            "benchmark_type": "memory_validation",
            "target_memory_mb": 512,
            "actual_memory_mb": peak_memory,
            "meets_target": peak_memory < 512,
            "processed_count": result.get("processed_count", 0),
            "comprehensive_metrics": self.metrics_collector.get_comprehensive_metrics()
        }

    def _run_concurrent_processing_benchmark(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """REFACTOR: Concurrent processing validation"""
        note_sets = [
            self._generate_test_notes(20, "concurrent_session_1"),
            self._generate_test_notes(15, "concurrent_session_2"),
            self._generate_test_notes(25, "concurrent_session_3")
        ]

        start_time = time.time()
        results = self.concurrent_manager.process_concurrent_sessions(note_sets)
        processing_time = time.time() - start_time

        successful_sessions = sum(1 for r in results if r["success"])
        total_processed = sum(r.get("processed_count", 0) for r in results)

        return {
            "success": successful_sessions == len(note_sets),
            "benchmark_type": "concurrent_processing",
            "sessions_requested": len(note_sets),
            "sessions_successful": successful_sessions,
            "total_processed": total_processed,
            "processing_time": processing_time,
            "session_results": results,
            "isolation_maintained": all(r.get("conflicts", 0) == 0 for r in results)
        }

    def _run_stress_test_benchmark(self, options: Dict[str, Any]) -> Dict[str, Any]:
        """REFACTOR: Stress test with large datasets"""
        large_dataset = self._generate_test_notes(200, "stress_test")

        # Run both dataset and memory pressure stress tests
        dataset_result = self.stress_manager.run_stress_test(large_dataset)

        large_content_notes = self._generate_large_content_notes(50)
        memory_result = self.stress_manager.run_memory_pressure_test(large_content_notes)

        return {
            "success": dataset_result["completed"] and memory_result["completed"],
            "benchmark_type": "stress_test",
            "dataset_stress": dataset_result,
            "memory_pressure_stress": memory_result,
            "overall_resilience": not (dataset_result.get("crashed", True) or
                                     memory_result.get("memory_exceeded", True))
        }

    def _generate_test_notes(self, count: int, batch_type: str) -> List[Dict[str, Any]]:
        """Generate realistic test notes for performance testing"""
        notes = []
        for i in range(count):
            note = {
                "path": Path(self.vault_path) / f"perf-test-{batch_type}-{i:03d}.md",
                "content": f"""# Performance Test Note {i} ({batch_type})

This is a realistic performance test note with substantial content for benchmarking.

## Performance Metrics
- Batch Type: {batch_type}
- Note Index: {i}
- Generated: {datetime.now().isoformat()}

## Content Section
This section contains realistic markdown content that would be typical in a 
knowledge management system. The content includes various markdown elements
and sufficient text to test processing performance under real-world conditions.

### Links and Tags
- Related: [[other-note-{(i+1) % count}]]
- Tags: #performance-test #{batch_type} #tdd-iteration-5

### Processing Notes
This note is designed to test the performance characteristics of the system
under realistic load conditions with varied content types and structures.
""",
                "metadata": {
                    "created": datetime.now().isoformat(),
                    "batch_type": batch_type,
                    "index": i,
                    "tags": ["performance-test", batch_type, "tdd-iteration-5"]
                }
            }
            notes.append(note)
        return notes

    def _generate_large_content_notes(self, count: int) -> List[Dict[str, Any]]:
        """Generate notes with large content for memory pressure testing"""
        notes = []
        large_content = "Large content section for memory pressure testing. " * 500  # ~25KB per note

        for i in range(count):
            note = {
                "path": Path(self.vault_path) / f"memory-pressure-{i:03d}.md",
                "content": f"# Memory Pressure Test Note {i}\n\n{large_content}",
                "metadata": {"type": "memory_pressure", "index": i, "size": "large"}
            }
            notes.append(note)
        return notes

    def generate_performance_report(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """REFACTOR: Generate comprehensive performance report"""
        total_benchmarks = len(results)
        successful_benchmarks = sum(1 for r in results if r.get("success", False))

        performance_summary = {
            "report_generated": datetime.now().isoformat(),
            "total_benchmarks": total_benchmarks,
            "successful_benchmarks": successful_benchmarks,
            "success_rate": successful_benchmarks / max(total_benchmarks, 1),
            "benchmark_results": results,
            "performance_targets_met": self._analyze_targets_met(results),
            "recommendations": self._generate_recommendations(results)
        }

        return performance_summary

    def _analyze_targets_met(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze which performance targets were met"""
        targets_analysis = {}

        for result in results:
            benchmark_type = result.get("benchmark_type", "unknown")
            meets_target = result.get("meets_target", False)
            targets_analysis[benchmark_type] = meets_target

        return targets_analysis

    def _generate_recommendations(self, results: List[Dict[str, Any]]) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []

        for result in results:
            if not result.get("meets_target", True):
                benchmark_type = result.get("benchmark_type", "unknown")
                if benchmark_type == "large_batch":
                    recommendations.append("Consider batch size optimization for large dataset processing")
                elif benchmark_type == "memory_validation":
                    recommendations.append("Memory usage optimization needed - consider streaming processing")
                elif "concurrent" in benchmark_type:
                    recommendations.append("Concurrent processing optimization - review session isolation")

        if not recommendations:
            recommendations.append("All performance targets met - system operating at optimal levels")

        return recommendations
