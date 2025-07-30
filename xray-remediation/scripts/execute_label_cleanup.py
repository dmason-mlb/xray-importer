#!/usr/bin/env python3
"""
Execute the label cleanup plan using JIRA MCP tools.
This script will be run via Claude Code to leverage the MCP tools.
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime

def load_cleanup_plan():
    """Load the most recent cleanup plan"""
    logs_dir = Path(__file__).parent.parent / 'logs'
    plan_files = list(logs_dir.glob('label_cleanup_plan_*.json'))
    
    if not plan_files:
        print("❌ No cleanup plan found. Run cleanup_labels_final.py first.")
        return None
        
    # Get the most recent plan
    latest_plan = max(plan_files, key=lambda p: p.stat().st_mtime)
    print(f"Loading cleanup plan from: {latest_plan}")
    
    with open(latest_plan, 'r') as f:
        return json.load(f)

def display_plan_summary(plan):
    """Display summary of the cleanup plan"""
    tests = plan['tests_to_clean']
    print(f"\n📋 Cleanup Plan Summary")
    print(f"   Total tests to clean: {len(tests)}")
    print(f"   Created: {plan['timestamp']}")
    print(f"   Status: {plan['status']}")
    
    # Show first 3 tests as examples
    print("\n   First 3 tests:")
    for test in tests[:3]:
        print(f"   - {test['key']}: Remove {test['labels_to_remove']}")
    
    if len(tests) > 3:
        print(f"   ... and {len(tests) - 3} more tests")

def main():
    """Main execution"""
    # Load the cleanup plan
    plan = load_cleanup_plan()
    if not plan:
        return 1
        
    # Display summary
    display_plan_summary(plan)
    
    # Output the tests to be processed
    tests_to_process = plan['tests_to_clean']
    
    print("\n" + "="*80)
    print("READY FOR LABEL CLEANUP")
    print("="*80)
    print(f"Found {len(tests_to_process)} tests to update")
    print("\nThe following tests will have their test case ID labels removed:")
    
    # Create execution log
    log_file = Path(__file__).parent.parent / 'logs' / f'label_cleanup_execution_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    
    execution_data = {
        'timestamp': datetime.now().isoformat(),
        'plan_file': str(plan.get('timestamp', 'unknown')),
        'total_tests': len(tests_to_process),
        'tests': tests_to_process,
        'status': 'ready_for_execution'
    }
    
    with open(log_file, 'w') as f:
        json.dump(execution_data, f, indent=2)
    
    print(f"\n✓ Execution data saved to: {log_file}")
    print("\nUse Claude Code with JIRA MCP tools to process each test.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())