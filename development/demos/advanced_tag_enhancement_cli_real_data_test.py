#!/usr/bin/env python3
"""
Real Data Testing & Validation for Advanced Tag Enhancement CLI

This script validates TDD Iteration 4's CLI implementation against actual user data:
- Live vault analysis with 698+ problematic tags
- Performance benchmarking (<30s processing targets)
- Quality assessment (improvement suggestion accuracy)
- User experience testing (interactive mode scenarios)

Purpose: Validate CLI before TDD Iteration 5 Enhanced AI Features
"""

import sys
import time
import json
from pathlib import Path
from typing import Dict, List, Any

# Add development directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.cli.advanced_tag_enhancement_cli import AdvancedTagEnhancementCLI
from src.ai.workflow_manager import WorkflowManager


class RealDataTestSuite:
    """Comprehensive real data testing for CLI validation"""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.cli = AdvancedTagEnhancementCLI(str(self.vault_path))
        self.workflow_manager = WorkflowManager(str(self.vault_path))
        self.test_results = {}
        
    def run_comprehensive_test_suite(self) -> Dict[str, Any]:
        """Run complete real data validation test suite"""
        print("🧪 REAL DATA TESTING & VALIDATION")
        print("=" * 60)
        print(f"📁 Vault Path: {self.vault_path}")
        print(f"🎯 Target: Validate CLI with 698+ problematic tags")
        print(f"⏱️  Performance Target: <30s processing")
        print()
        
        # Test 1: Basic CLI functionality validation
        print("🔧 Test 1: Basic CLI Functionality Validation")
        basic_test_results = self.test_basic_cli_functionality()
        self.test_results["basic_functionality"] = basic_test_results
        
        # Test 2: Live vault analysis
        print("\n📊 Test 2: Live Vault Analysis")
        vault_analysis_results = self.test_live_vault_analysis()
        self.test_results["vault_analysis"] = vault_analysis_results
        
        # Test 3: Performance benchmarking
        print("\n⚡ Test 3: Performance Benchmarking")
        performance_results = self.test_performance_benchmarking()
        self.test_results["performance"] = performance_results
        
        # Test 4: Quality assessment
        print("\n🎯 Test 4: Quality Assessment")
        quality_results = self.test_quality_assessment()
        self.test_results["quality"] = quality_results
        
        # Test 5: Export functionality
        print("\n📤 Test 5: Export Functionality")
        export_results = self.test_export_functionality()
        self.test_results["export"] = export_results
        
        # Test 6: Error handling
        print("\n🛡️  Test 6: Error Handling")
        error_handling_results = self.test_error_handling()
        self.test_results["error_handling"] = error_handling_results
        
        # Generate comprehensive report
        self.generate_test_report()
        
        return self.test_results
        
    def test_basic_cli_functionality(self) -> Dict[str, Any]:
        """Test basic CLI initialization and command execution"""
        results = {"status": "running", "tests": []}
        
        try:
            # Test CLI initialization
            cli_init_result = self._test_cli_initialization()
            results["tests"].append(cli_init_result)
            
            # Test command execution framework
            command_exec_result = self._test_command_execution()
            results["tests"].append(command_exec_result)
            
            # Test utility integration
            utility_integration_result = self._test_utility_integration()
            results["tests"].append(utility_integration_result)
            
            results["status"] = "completed"
            results["success_rate"] = sum(1 for test in results["tests"] if test["passed"]) / len(results["tests"])
            
        except Exception as e:
            results["status"] = "failed"
            results["error"] = str(e)
            
        return results
        
    def test_live_vault_analysis(self) -> Dict[str, Any]:
        """Test CLI with actual vault data"""
        results = {"status": "running", "analysis": {}}
        
        try:
            print("  📁 Scanning vault for tags...")
            
            # Run analyze-tags command on real vault
            start_time = time.time()
            analysis_result = self.cli.execute_command("analyze-tags", show_progress=True)
            analysis_time = time.time() - start_time
            
            if "error" in analysis_result:
                results["status"] = "failed"
                results["error"] = analysis_result["error"]
                return results
                
            # Extract analysis metrics
            total_tags = analysis_result.get("total_tags", 0)
            problematic_tags = analysis_result.get("problematic_tags", 0)
            quality_distribution = analysis_result.get("quality_distribution", {})
            
            results["analysis"] = {
                "total_tags": total_tags,
                "problematic_tags": problematic_tags,
                "problematic_percentage": (problematic_tags / total_tags * 100) if total_tags > 0 else 0,
                "quality_distribution": quality_distribution,
                "analysis_time": analysis_time,
                "meets_target": total_tags >= 698  # Target: 698+ tags
            }
            
            print(f"  ✅ Found {total_tags} total tags")
            print(f"  ⚠️  {problematic_tags} problematic tags ({results['analysis']['problematic_percentage']:.1f}%)")
            print(f"  ⏱️  Analysis time: {analysis_time:.2f}s")
            print(f"  🎯 Meets 698+ target: {'Yes' if results['analysis']['meets_target'] else 'No'}")
            
            results["status"] = "completed"
            
        except Exception as e:
            results["status"] = "failed"
            results["error"] = str(e)
            print(f"  ❌ Error: {e}")
            
        return results
        
    def test_performance_benchmarking(self) -> Dict[str, Any]:
        """Test performance against <30s processing targets"""
        results = {"status": "running", "benchmarks": []}
        
        try:
            # Benchmark 1: Analyze-tags performance
            print("  ⏱️  Benchmarking analyze-tags command...")
            start_time = time.time()
            analysis_result = self.cli.execute_command("analyze-tags")
            analyze_time = time.time() - start_time
            
            analyze_benchmark = {
                "command": "analyze-tags",
                "execution_time": analyze_time,
                "meets_target": analyze_time < 30.0,
                "target": "< 30s",
                "total_tags": analysis_result.get("total_tags", 0)
            }
            results["benchmarks"].append(analyze_benchmark)
            
            print(f"    📊 analyze-tags: {analyze_time:.2f}s ({'✅' if analyze_benchmark['meets_target'] else '❌'})")
            
            # Benchmark 2: Suggest-improvements performance
            print("  ⏱️  Benchmarking suggest-improvements command...")
            start_time = time.time()
            suggestions_result = self.cli.execute_command("suggest-improvements", min_quality=0.7)
            suggestions_time = time.time() - start_time
            
            suggestions_benchmark = {
                "command": "suggest-improvements",
                "execution_time": suggestions_time,
                "meets_target": suggestions_time < 30.0,
                "target": "< 30s",
                "suggestions_generated": len(suggestions_result.get("analyzed_tags", []))
            }
            results["benchmarks"].append(suggestions_benchmark)
            
            print(f"    💡 suggest-improvements: {suggestions_time:.2f}s ({'✅' if suggestions_benchmark['meets_target'] else '❌'})")
            
            # Benchmark 3: Batch processing simulation
            print("  ⏱️  Benchmarking batch processing simulation...")
            start_time = time.time()
            simulation_data = {
                "total_tags": 698,
                "problematic_tags": 431  # ~62% problematic (realistic)
            }
            simulation_result = self.cli.process_real_data_simulation(simulation_data)
            simulation_time = time.time() - start_time
            
            batch_benchmark = {
                "command": "batch-simulation",
                "execution_time": simulation_time,
                "meets_target": simulation_time < 30.0,
                "target": "< 30s",
                "simulated_tags": simulation_data["total_tags"]
            }
            results["benchmarks"].append(batch_benchmark)
            
            print(f"    🔄 batch-simulation: {simulation_time:.2f}s ({'✅' if batch_benchmark['meets_target'] else '❌'})")
            
            # Calculate overall performance metrics
            all_meet_targets = all(b["meets_target"] for b in results["benchmarks"])
            avg_time = sum(b["execution_time"] for b in results["benchmarks"]) / len(results["benchmarks"])
            
            results["overall"] = {
                "all_meet_targets": all_meet_targets,
                "average_execution_time": avg_time,
                "performance_grade": "A" if all_meet_targets else "B" if avg_time < 20 else "C"
            }
            
            print(f"  🏆 Overall Performance: {results['overall']['performance_grade']} (avg: {avg_time:.2f}s)")
            
            results["status"] = "completed"
            
        except Exception as e:
            results["status"] = "failed"
            results["error"] = str(e)
            print(f"  ❌ Performance test error: {e}")
            
        return results
        
    def test_quality_assessment(self) -> Dict[str, Any]:
        """Test improvement suggestion accuracy and quality"""
        results = {"status": "running", "quality_metrics": {}}
        
        try:
            print("  🎯 Analyzing improvement suggestion quality...")
            
            # Get suggestions for problematic tags
            suggestions_result = self.cli.execute_command("suggest-improvements", min_quality=0.7)
            analyzed_tags = suggestions_result.get("analyzed_tags", [])
            
            if not analyzed_tags:
                results["quality_metrics"] = {
                    "total_analyzed": 0,
                    "suggestions_provided": 0,
                    "suggestion_rate": 0.0,
                    "meets_90_percent_target": False
                }
            else:
                # Calculate quality metrics
                total_analyzed = len(analyzed_tags)
                with_suggestions = len([tag for tag in analyzed_tags if tag.get("suggestions", [])])
                suggestion_rate = with_suggestions / total_analyzed if total_analyzed > 0 else 0.0
                
                # Analyze suggestion quality patterns
                suggestion_quality = self._analyze_suggestion_patterns(analyzed_tags)
                
                results["quality_metrics"] = {
                    "total_analyzed": total_analyzed,
                    "suggestions_provided": with_suggestions,
                    "suggestion_rate": suggestion_rate,
                    "meets_90_percent_target": suggestion_rate >= 0.9,
                    "patterns": suggestion_quality
                }
                
            print(f"    📊 Analyzed {results['quality_metrics']['total_analyzed']} problematic tags")
            print(f"    💡 Suggestions provided: {results['quality_metrics']['suggestions_provided']}")
            print(f"    📈 Suggestion rate: {results['quality_metrics']['suggestion_rate']:.1%}")
            print(f"    🎯 Meets 90% target: {'Yes' if results['quality_metrics']['meets_90_percent_target'] else 'No'}")
            
            results["status"] = "completed"
            
        except Exception as e:
            results["status"] = "failed"
            results["error"] = str(e)
            print(f"  ❌ Quality assessment error: {e}")
            
        return results
        
    def test_export_functionality(self) -> Dict[str, Any]:
        """Test JSON/CSV export functionality"""
        results = {"status": "running", "exports": []}
        
        try:
            print("  📤 Testing export functionality...")
            
            # Test JSON export
            json_result = self.cli.execute_command("analyze-tags", export_format="json")
            json_test = {
                "format": "json",
                "success": "export_data" in json_result,
                "data_valid": False
            }
            
            if json_test["success"]:
                try:
                    json.loads(json_result["export_data"])
                    json_test["data_valid"] = True
                except json.JSONDecodeError:
                    json_test["data_valid"] = False
                    
            results["exports"].append(json_test)
            print(f"    📋 JSON export: {'✅' if json_test['success'] and json_test['data_valid'] else '❌'}")
            
            # Test CSV export
            csv_result = self.cli.execute_command("suggest-improvements", export_format="csv")
            csv_test = {
                "format": "csv",
                "success": "export_data" in csv_result,
                "data_valid": bool(csv_result.get("export_data", "").strip())
            }
            results["exports"].append(csv_test)
            print(f"    📊 CSV export: {'✅' if csv_test['success'] and csv_test['data_valid'] else '❌'}")
            
            results["status"] = "completed"
            
        except Exception as e:
            results["status"] = "failed"
            results["error"] = str(e)
            print(f"  ❌ Export test error: {e}")
            
        return results
        
    def test_error_handling(self) -> Dict[str, Any]:
        """Test error handling and graceful failures"""
        results = {"status": "running", "error_tests": []}
        
        try:
            print("  🛡️  Testing error handling...")
            
            # Test invalid vault path
            invalid_path_result = self.cli.execute_command("analyze-tags", vault_path="/nonexistent/path")
            invalid_path_test = {
                "test": "invalid_vault_path",
                "handled_gracefully": "error" in invalid_path_result,
                "error_message": invalid_path_result.get("error", "")
            }
            results["error_tests"].append(invalid_path_test)
            
            # Test invalid command  
            invalid_command_result = self.cli.execute_command("invalid-command")
            invalid_command_test = {
                "test": "invalid_command",
                "handled_gracefully": "error" in invalid_command_result,
                "error_message": invalid_command_result.get("error", "")
            }
            results["error_tests"].append(invalid_command_test)
            
            graceful_handling_rate = sum(1 for test in results["error_tests"] if test["handled_gracefully"]) / len(results["error_tests"])
            
            print(f"    🛡️  Graceful error handling: {graceful_handling_rate:.1%}")
            
            results["graceful_handling_rate"] = graceful_handling_rate
            results["status"] = "completed"
            
        except Exception as e:
            results["status"] = "failed"
            results["error"] = str(e)
            print(f"  ❌ Error handling test error: {e}")
            
        return results
        
    def _test_cli_initialization(self) -> Dict[str, Any]:
        """Test CLI initialization"""
        try:
            cli_test = AdvancedTagEnhancementCLI(str(self.vault_path))
            return {"test": "cli_initialization", "passed": True, "message": "CLI initialized successfully"}
        except Exception as e:
            return {"test": "cli_initialization", "passed": False, "error": str(e)}
            
    def _test_command_execution(self) -> Dict[str, Any]:
        """Test command execution framework"""
        try:
            result = self.cli.execute_command("analyze-tags", vault_path=str(self.vault_path))
            success = "error" not in result or "Vault not found" not in result.get("error", "")
            return {"test": "command_execution", "passed": success, "message": "Command execution working"}
        except Exception as e:
            return {"test": "command_execution", "passed": False, "error": str(e)}
            
    def _test_utility_integration(self) -> Dict[str, Any]:
        """Test utility class integration"""
        try:
            # Test if utilities are properly initialized
            has_utilities = all([
                hasattr(self.cli, 'tag_processor'),
                hasattr(self.cli, 'export_manager'),
                hasattr(self.cli, 'interaction_manager'),
                hasattr(self.cli, 'performance_optimizer'),
                hasattr(self.cli, 'backup_manager'),
                hasattr(self.cli, 'tag_collector')
            ])
            return {"test": "utility_integration", "passed": has_utilities, "message": "All utilities integrated"}
        except Exception as e:
            return {"test": "utility_integration", "passed": False, "error": str(e)}
            
    def _analyze_suggestion_patterns(self, analyzed_tags: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns in tag suggestions"""
        patterns = {
            "common_issues": {},
            "suggestion_types": {},
            "quality_improvements": []
        }
        
        for tag_data in analyzed_tags:
            tag = tag_data.get("tag", "")
            suggestions = tag_data.get("suggestions", [])
            quality_score = tag_data.get("quality_score", 0.0)
            
            # Identify common issues
            if tag.isdigit():
                patterns["common_issues"]["numeric_only"] = patterns["common_issues"].get("numeric_only", 0) + 1
            if not tag.strip():
                patterns["common_issues"]["empty_tags"] = patterns["common_issues"].get("empty_tags", 0) + 1
            if len(tag.split('-')) > 3:
                patterns["common_issues"]["overly_complex"] = patterns["common_issues"].get("overly_complex", 0) + 1
                
            # Track suggestion types
            if suggestions:
                patterns["suggestion_types"]["with_suggestions"] = patterns["suggestion_types"].get("with_suggestions", 0) + 1
            else:
                patterns["suggestion_types"]["no_suggestions"] = patterns["suggestion_types"].get("no_suggestions", 0) + 1
                
        return patterns
        
    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📋 COMPREHENSIVE TEST REPORT")
        print("=" * 60)
        
        # Overall summary
        total_tests = sum(1 for category in self.test_results.values() if category.get("status") == "completed")
        failed_tests = sum(1 for category in self.test_results.values() if category.get("status") == "failed")
        success_rate = (total_tests - failed_tests) / total_tests if total_tests > 0 else 0
        
        print(f"🏆 Overall Success Rate: {success_rate:.1%}")
        print(f"✅ Completed Tests: {total_tests}")
        print(f"❌ Failed Tests: {failed_tests}")
        print()
        
        # Performance summary
        if "performance" in self.test_results and self.test_results["performance"].get("status") == "completed":
            perf_data = self.test_results["performance"]
            print(f"⚡ Performance Grade: {perf_data['overall']['performance_grade']}")
            print(f"⏱️  Average Execution Time: {perf_data['overall']['average_execution_time']:.2f}s")
            print()
            
        # Vault analysis summary
        if "vault_analysis" in self.test_results and self.test_results["vault_analysis"].get("status") == "completed":
            vault_data = self.test_results["vault_analysis"]["analysis"]
            print(f"📊 Vault Analysis:")
            print(f"   Total Tags: {vault_data['total_tags']}")
            print(f"   Problematic Tags: {vault_data['problematic_tags']} ({vault_data['problematic_percentage']:.1f}%)")
            print(f"   Meets 698+ Target: {'Yes' if vault_data['meets_target'] else 'No'}")
            print()
            
        # Quality assessment summary
        if "quality" in self.test_results and self.test_results["quality"].get("status") == "completed":
            quality_data = self.test_results["quality"]["quality_metrics"]
            print(f"🎯 Quality Assessment:")
            print(f"   Suggestion Rate: {quality_data['suggestion_rate']:.1%}")
            print(f"   Meets 90% Target: {'Yes' if quality_data['meets_90_percent_target'] else 'No'}")
            print()
            
        print("📁 Report saved to: real_data_test_results.json")
        
        # Save detailed results to file
        with open("real_data_test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2, default=str)


def main():
    """Main execution function"""
    vault_path = Path.cwd().parent  # Assuming we're in development/, vault is parent
    
    print("🧪 ADVANCED TAG ENHANCEMENT CLI - REAL DATA TESTING")
    print(f"📅 Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Vault: {vault_path}")
    print()
    
    # Initialize test suite
    test_suite = RealDataTestSuite(str(vault_path))
    
    # Run comprehensive tests
    results = test_suite.run_comprehensive_test_suite()
    
    print(f"\n🎯 Testing completed! Results saved to real_data_test_results.json")
    return results


if __name__ == "__main__":
    main()
