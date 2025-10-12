#!/usr/bin/env python3
"""
Test Dashboard with Actual Vault Data

Shows what your real vault would look like with working CLI integration
"""

import sys
import json
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).parent))

from src.cli.workflow_dashboard import WorkflowDashboard


def test_actual_vault():
    """Test with actual vault counts (manually collected)"""
    
    print("\n" + "="*60)
    print("📊 YOUR ACTUAL VAULT STATUS")
    print("="*60 + "\n")
    
    # Your real vault counts (from find commands)
    actual_status = {
        "workflow_status": {
            "inbox_count": 97,        # knowledge/Inbox/*.md
            "fleeting_count": 0,      # Fleeting Notes/*.md
            "permanent_count": 142,   # Estimated
            "literature_count": 18    # Estimated
        },
        "ai_features": {
            "summarization": True,
            "connections": True,
            "tagging": True
        },
        "recommendations": [
            "⚠️  CRITICAL: 97 inbox notes need processing",
            "📝 Consider batch processing to clear backlog",
            "🎯 Target: Get inbox below 20 notes for 🟢 status"
        ]
    }
    
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = Mock(
            returncode=0,
            stdout=json.dumps(actual_status),
            stderr=""
        )
        
        dashboard = WorkflowDashboard(vault_path=".")
        
        print("Dashboard View:")
        print("-" * 60 + "\n")
        dashboard.display()
        
        print("\n" + "-" * 60)
        print("\nHealth Analysis:")
        print(f"  Current Status: 🔴 RED (97 notes > 51)")
        print(f"  To reach 🟡 Yellow: Process 47 notes (down to 50)")
        print(f"  To reach 🟢 Green: Process 77 notes (down to 20)")
        
        print("\n" + "-" * 60)
        print("\nRecommendations:")
        for i, rec in enumerate(actual_status["recommendations"], 1):
            print(f"  {i}. {rec}")
    
    print("\n" + "="*60)
    print("✅ Actual vault status displayed!")
    print("="*60 + "\n")


def show_comparison_table():
    """Show health indicator reference table"""
    print("\n" + "="*60)
    print("📋 HEALTH INDICATOR REFERENCE")
    print("="*60 + "\n")
    
    print("┌─────────────┬──────────────┬────────────────────────┐")
    print("│  Indicator  │  Note Range  │  Status                │")
    print("├─────────────┼──────────────┼────────────────────────┤")
    print("│  🟢 Green   │    0-20      │  Healthy / Maintained  │")
    print("│  🟡 Yellow  │   21-50      │  Attention Needed      │")
    print("│  🔴 Red     │    51+       │  Critical / Backlog    │")
    print("└─────────────┴──────────────┴────────────────────────┘")
    
    print("\n📊 Your Position:")
    print(f"  Current: 97 notes (🔴 RED)")
    print(f"  Target:  20 notes (🟢 GREEN)")
    print(f"  Delta:   -77 notes to process")
    
    print("\n" + "="*60 + "\n")


if __name__ == '__main__':
    show_comparison_table()
    test_actual_vault()
