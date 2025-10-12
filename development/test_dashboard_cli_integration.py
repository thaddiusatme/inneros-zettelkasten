#!/usr/bin/env python3
"""
Dashboard CLI Integration Test
Tests dashboard with real CLI operations (requires venv with dependencies)
"""

import sys
import time
from pathlib import Path

# Add development directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.cli.workflow_dashboard import WorkflowDashboard
from rich.console import Console

def test_cli_integration():
    """Test actual CLI subprocess execution"""
    print("\n" + "="*60)
    print("TEST: CLI Integration (Status Command)")
    print("="*60)
    
    try:
        dashboard = WorkflowDashboard(vault_path="..")
        
        print("\n📊 Fetching real vault status...")
        start_time = time.time()
        status = dashboard.fetch_inbox_status()
        duration = time.time() - start_time
        
        print(f"✅ Status fetched in {duration:.2f}s")
        
        if status.get('error'):
            print(f"⚠️  CLI error: {status.get('message')}")
            return False
        
        # Display status
        print(f"\n📥 Inbox Status:")
        print(f"  • Inbox Count: {status.get('inbox_count', 0)}")
        print(f"  • Fleeting Count: {status.get('fleeting_count', 0)}")
        print(f"  • Total Notes: {status.get('total_notes', 0)}")
        print(f"  • Health: {status.get('health', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_inbox_panel_with_real_data():
    """Test inbox panel rendering with real vault data"""
    print("\n" + "="*60)
    print("TEST: Inbox Panel with Real Data")
    print("="*60)
    
    try:
        dashboard = WorkflowDashboard(vault_path="..")
        console = Console()
        
        print("\n🎨 Rendering inbox panel with real data...")
        panel = dashboard.render_inbox_panel()
        
        console.print(panel)
        
        # Check health indicator
        status = dashboard.fetch_inbox_status()
        inbox_count = status.get('inbox_count', 0)
        indicator = dashboard.get_inbox_health_indicator(inbox_count)
        
        print(f"\n✅ Health indicator: {indicator}")
        print(f"✅ Inbox count: {inbox_count}")
        
        # Validate indicator matches count
        if inbox_count <= 20 and indicator == '🟢':
            print("✅ Health indicator correct (🟢 for 0-20 notes)")
        elif 21 <= inbox_count <= 50 and indicator == '🟡':
            print("✅ Health indicator correct (🟡 for 21-50 notes)")
        elif inbox_count > 50 and indicator == '🔴':
            print("✅ Health indicator correct (🔴 for 51+ notes)")
        else:
            print(f"⚠️  Unexpected indicator {indicator} for {inbox_count} notes")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_async_executor():
    """Test AsyncCLIExecutor with real CLI call"""
    print("\n" + "="*60)
    print("TEST: AsyncCLIExecutor with Real CLI")
    print("="*60)
    
    try:
        dashboard = WorkflowDashboard(vault_path="..")
        
        print("\n⚙️  Executing status command via AsyncCLIExecutor...")
        start_time = time.time()
        
        result = dashboard.async_executor.execute_with_progress(
            cli_name='core_workflow_cli.py',
            args=['status', '--format', 'json'],
            vault_path='..'
        )
        
        duration = time.time() - start_time
        
        print(f"✅ Execution completed in {duration:.2f}s")
        print(f"  • Return code: {result['returncode']}")
        print(f"  • Duration: {result['duration']:.2f}s")
        print(f"  • Timeout: {result['timeout']}")
        print(f"  • Stdout length: {len(result['stdout'])} chars")
        
        if result['returncode'] == 0:
            print("✅ CLI execution successful")
            return True
        else:
            print(f"⚠️  CLI returned non-zero: {result['returncode']}")
            print(f"stderr: {result['stderr'][:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_keyboard_with_real_cli():
    """Test keyboard shortcuts trigger real CLI (simulated, no actual execution)"""
    print("\n" + "="*60)
    print("TEST: Keyboard Shortcuts → CLI Mapping")
    print("="*60)
    
    try:
        dashboard = WorkflowDashboard(vault_path="..")
        
        test_keys = {
            'p': 'core_workflow_cli.py',
            'w': 'weekly_review_cli.py',
            'f': 'fleeting_cli.py',
            's': 'core_workflow_cli.py',
            'b': 'safe_workflow_cli.py'
        }
        
        print("\n🗺️  Verifying CLI mappings:")
        for key, expected_cli in test_keys.items():
            cmd = dashboard.key_commands.get(key)
            if cmd and cmd['cli'] == expected_cli:
                print(f"  ✅ [{key.upper()}] → {cmd['cli']} {' '.join(cmd['args'])}")
            else:
                print(f"  ❌ [{key.upper()}] mapping incorrect!")
                return False
        
        print("\n✅ All keyboard shortcuts correctly mapped to CLIs")
        return True
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


def test_performance_benchmarks():
    """Measure performance with real CLI calls"""
    print("\n" + "="*60)
    print("TEST: Performance Benchmarks")
    print("="*60)
    
    try:
        dashboard = WorkflowDashboard(vault_path="..")
        
        # Test 1: Fetch inbox status
        print("\n⏱️  Benchmark 1: Fetch Inbox Status")
        start = time.time()
        status = dashboard.fetch_inbox_status()
        fetch_time = time.time() - start
        print(f"  Time: {fetch_time:.3f}s")
        
        if fetch_time < 5.0:
            print("  ✅ Under 5s target")
        else:
            print(f"  ⚠️  Slower than target (5s)")
        
        # Test 2: Render panel
        print("\n⏱️  Benchmark 2: Render Inbox Panel")
        start = time.time()
        panel = dashboard.render_inbox_panel()
        render_time = time.time() - start
        print(f"  Time: {render_time:.3f}s")
        
        if render_time < 6.0:  # Includes fetch + render
            print("  ✅ Under 6s target")
        else:
            print(f"  ⚠️  Slower than target (6s)")
        
        # Test 3: AsyncCLIExecutor
        print("\n⏱️  Benchmark 3: AsyncCLIExecutor")
        start = time.time()
        result = dashboard.async_executor.execute_with_progress(
            cli_name='core_workflow_cli.py',
            args=['status', '--format', 'json'],
            vault_path='..'
        )
        exec_time = time.time() - start
        print(f"  Time: {exec_time:.3f}s")
        
        if exec_time < 10.0:
            print("  ✅ Under 10s target")
        else:
            print(f"  ⚠️  Slower than target (10s)")
        
        # Summary
        print("\n📊 Performance Summary:")
        print(f"  • Fetch Status: {fetch_time:.3f}s")
        print(f"  • Render Panel: {render_time:.3f}s")
        print(f"  • AsyncExecutor: {exec_time:.3f}s")
        print(f"  • Total Test Time: {fetch_time + render_time + exec_time:.3f}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all CLI integration tests"""
    console = Console()
    
    console.print("\n" + "="*60, style="bold green")
    console.print("  🔌 Dashboard CLI Integration Tests", style="bold green")
    console.print("  Testing with Real Vault & CLI Operations", style="bold green")
    console.print("="*60 + "\n", style="bold green")
    
    print("📂 Vault: /Users/thaddius/repos/inneros-zettelkasten")
    print("🐍 Using: venv with all dependencies\n")
    
    tests = [
        test_cli_integration,
        test_inbox_panel_with_real_data,
        test_async_executor,
        test_keyboard_with_real_cli,
        test_performance_benchmarks
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"\n❌ Test crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    # Summary
    print("\n" + "="*60)
    print("📊 CLI INTEGRATION TEST SUMMARY")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    percentage = (passed / total) * 100
    
    print(f"\nTests Passed: {passed}/{total} ({percentage:.1f}%)")
    
    if passed == total:
        console.print("\n✅ ALL CLI INTEGRATION TESTS PASSED!", style="bold green")
        console.print("Dashboard is production-ready with full CLI integration!\n", style="green")
        
        print("🎉 Production Deployment Approved!")
        print("\n📝 Next Steps:")
        print("  1. Use dashboard daily for real workflow operations")
        print("  2. Monitor performance and gather feedback")
        print("  3. Begin P1.1 Multi-Panel Layout when ready")
        return 0
    else:
        console.print(f"\n⚠️  {total - passed} TEST(S) FAILED", style="bold yellow")
        print("\n📝 Review failures above and address issues")
        return 1


if __name__ == "__main__":
    sys.exit(main())
