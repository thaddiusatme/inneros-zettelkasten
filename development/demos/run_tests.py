#!/usr/bin/env python3
"""
Test runner script for TDD development.
Provides quick access to different test suites and coverage reports.
"""

import subprocess
import sys
import argparse
from pathlib import Path


def run_command(cmd: str, description: str = "") -> bool:
    """Run a shell command and return success status."""
    if description:
        print(f"\n🧪 {description}")
        print("-" * 50)
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, 
                              capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False


def main():
    """Main test runner with command line options."""
    parser = argparse.ArgumentParser(description="TDD Test Runner for InnerOS AI Integration")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--e2e", action="store_true", help="Run end-to-end tests only")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--watch", action="store_true", help="Run tests in watch mode")
    parser.add_argument("--quick", action="store_true", help="Run quick smoke tests")
    
    args = parser.parse_args()
    
    # Default to running unit tests if no specific option provided
    if not any([args.unit, args.integration, args.e2e, args.all, args.quick]):
        args.unit = True
    
    print("🚀 InnerOS TDD Test Runner")
    print("=" * 50)
    
    success = True
    
    if args.quick:
        success &= run_command(
            "python3 -m pytest tests/ -m 'unit' -v --tb=short",
            "Running quick smoke tests (unit tests only)"
        )
    
    if args.unit or args.all:
        success &= run_command(
            "python3 -m pytest tests/unit/ -v",
            "Running unit tests"
        )
    
    if args.integration or args.all:
        success &= run_command(
            "python3 -m pytest tests/integration/ -v",
            "Running integration tests"
        )
    
    if args.e2e or args.all:
        success &= run_command(
            "python3 -m pytest tests/e2e/ -v",
            "Running end-to-end tests"
        )
    
    if args.coverage or args.all:
        success &= run_command(
            "python3 -m pytest tests/ --cov=src --cov-report=html --cov-report=term",
            "Generating coverage report"
        )
        
        # Open coverage report if it exists
        coverage_path = Path("htmlcov/index.html")
        if coverage_path.exists():
            print(f"\n📊 Coverage report available at: file://{coverage_path.absolute()}")
    
    if args.watch:
        try:
            print("👀 Starting test watch mode...")
            print("Press Ctrl+C to stop")
            subprocess.run("python3 -m pytest-watch tests/", shell=True)
        except KeyboardInterrupt:
            print("\n👋 Watch mode stopped")
    
    if success:
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
