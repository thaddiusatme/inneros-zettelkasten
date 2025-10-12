#!/usr/bin/env python3
"""
Dashboard UI Production Test
Tests dashboard UI components without requiring full CLI dependencies
"""

import sys
from pathlib import Path

# Add development directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.cli.workflow_dashboard import WorkflowDashboard
from rich.console import Console

def test_dashboard_initialization():
    """Test 1: Dashboard initializes correctly"""
    print("\n" + "="*60)
    print("TEST 1: Dashboard Initialization")
    print("="*60)
    
    try:
        dashboard = WorkflowDashboard(vault_path="..")
        print("✅ Dashboard initialized successfully")
        print(f"✅ Vault path: {dashboard.vault_path}")
        print(f"✅ Key commands: {len(dashboard.key_commands)} shortcuts configured")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


def test_keyboard_shortcuts():
    """Test 2: Keyboard shortcut configuration"""
    print("\n" + "="*60)
    print("TEST 2: Keyboard Shortcuts Configuration")
    print("="*60)
    
    try:
        dashboard = WorkflowDashboard(vault_path="..")
        
        expected_keys = ['p', 'w', 'f', 's', 'b', 'q']
        for key in expected_keys:
            if key in dashboard.key_commands:
                cmd = dashboard.key_commands[key]
                print(f"✅ [{key.upper()}] configured: {cmd.get('desc', 'N/A')}")
            else:
                print(f"❌ [{key.upper()}] missing!")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


def test_quick_actions_panel():
    """Test 3: Quick actions panel rendering"""
    print("\n" + "="*60)
    print("TEST 3: Quick Actions Panel Rendering")
    print("="*60)
    
    try:
        dashboard = WorkflowDashboard(vault_path="..")
        panel = dashboard.render_quick_actions_panel()
        
        console = Console()
        print("\n📋 Rendered Panel:")
        console.print(panel)
        
        # Check panel content
        panel_str = str(panel)
        required_keys = ['P', 'W', 'F', 'S', 'B', 'Q']
        missing = [k for k in required_keys if f'[{k}]' not in panel_str]
        
        if missing:
            print(f"\n❌ Missing shortcuts in panel: {missing}")
            return False
        else:
            print(f"\n✅ All {len(required_keys)} shortcuts displayed")
            return True
            
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_invalid_key_handling():
    """Test 4: Invalid key error handling"""
    print("\n" + "="*60)
    print("TEST 4: Invalid Key Error Handling")
    print("="*60)
    
    try:
        dashboard = WorkflowDashboard(vault_path="..")
        
        # Test invalid key
        result = dashboard.handle_key_press('x')
        
        if result.get('error'):
            print(f"✅ Invalid key detected: {result.get('message')}")
            
            # Check message quality
            msg = result.get('message', '')
            if 'Valid shortcuts' in msg or 'valid' in msg.lower():
                print("✅ Error message provides guidance")
                return True
            else:
                print("⚠️  Error message could be more helpful")
                return True
        else:
            print("❌ Invalid key should return error")
            return False
            
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


def test_quit_handling():
    """Test 5: Quit shortcut handling"""
    print("\n" + "="*60)
    print("TEST 5: Quit Shortcut")
    print("="*60)
    
    try:
        dashboard = WorkflowDashboard(vault_path="..")
        
        result = dashboard.handle_key_press('q')
        
        if result.get('exit'):
            print("✅ [Q] triggers exit correctly")
            print(f"✅ Exit result: {result}")
            return True
        else:
            print(f"❌ [Q] should trigger exit, got: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


def test_code_health():
    """Test 6: Code health metrics"""
    print("\n" + "="*60)
    print("TEST 6: Code Health Metrics")
    print("="*60)
    
    try:
        dashboard_file = Path(__file__).parent / "src/cli/workflow_dashboard.py"
        utils_file = Path(__file__).parent / "src/cli/workflow_dashboard_utils.py"
        
        dashboard_lines = len(dashboard_file.read_text().splitlines())
        utils_lines = len(utils_file.read_text().splitlines())
        
        print(f"📊 Code Statistics:")
        print(f"  • workflow_dashboard.py: {dashboard_lines} LOC")
        print(f"  • workflow_dashboard_utils.py: {utils_lines} LOC")
        print(f"  • Total: {dashboard_lines + utils_lines} LOC")
        
        # Check ADR-001 compliance
        adr_limit = 500
        if dashboard_lines <= adr_limit:
            margin = adr_limit - dashboard_lines
            percentage = (dashboard_lines / adr_limit) * 100
            print(f"\n✅ ADR-001 Compliant: {dashboard_lines}/{adr_limit} LOC ({percentage:.1f}%)")
            print(f"✅ Remaining budget: {margin} LOC ({(margin/adr_limit)*100:.1f}%)")
            return True
        else:
            print(f"\n❌ ADR-001 Violation: {dashboard_lines}/{adr_limit} LOC")
            return False
            
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


def main():
    """Run all production UI tests"""
    console = Console()
    
    console.print("\n" + "="*60, style="bold cyan")
    console.print("  🧪 Dashboard UI Production Tests", style="bold cyan")
    console.print("  Testing UI components without CLI dependencies", style="bold cyan")
    console.print("="*60 + "\n", style="bold cyan")
    
    tests = [
        test_dashboard_initialization,
        test_keyboard_shortcuts,
        test_quick_actions_panel,
        test_invalid_key_handling,
        test_quit_handling,
        test_code_health
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
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    percentage = (passed / total) * 100
    
    print(f"\nTests Passed: {passed}/{total} ({percentage:.1f}%)")
    
    if passed == total:
        console.print("\n✅ ALL TESTS PASSED - Dashboard UI is production ready!", style="bold green")
        print("\n📝 Next Steps:")
        print("  1. Install missing dependencies: pip install requests")
        print("  2. Test actual CLI integration with real operations")
        print("  3. Run full production test suite from PRODUCTION-TEST-GUIDE.md")
        return 0
    else:
        console.print(f"\n⚠️  {total - passed} TEST(S) FAILED - Review errors above", style="bold yellow")
        return 1


if __name__ == "__main__":
    sys.exit(main())
