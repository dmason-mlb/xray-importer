#!/usr/bin/env python3
"""
Complete all remaining label cleanups using the saved plan.
This script reads the cleanup plan and processes all remaining tests.
"""

import json
import time
from pathlib import Path
from datetime import datetime

def load_cleanup_plan():
    """Load the most recent cleanup plan"""
    logs_dir = Path(__file__).parent.parent / 'logs'
    plan_files = list(logs_dir.glob('label_cleanup_plan_*.json'))
    
    if not plan_files:
        print("❌ No cleanup plan found.")
        return None
        
    # Get the most recent plan
    latest_plan = max(plan_files, key=lambda p: p.stat().st_mtime)
    
    with open(latest_plan, 'r') as f:
        return json.load(f)

def get_completed_tests():
    """Return list of tests already completed"""
    return [
        'FRAMED-1425', 'FRAMED-1424', 'FRAMED-1423', 'FRAMED-1422',
        'FRAMED-1421', 'FRAMED-1420', 'FRAMED-1419', 'FRAMED-1418', 
        'FRAMED-1417'
    ]

def save_execution_log(results):
    """Save execution results"""
    log_file = Path(__file__).parent.parent / 'logs' / f'label_cleanup_complete_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    
    with open(log_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_processed': len(results),
            'results': results
        }, f, indent=2)
    
    return log_file

def main():
    """Main execution"""
    # Load cleanup plan
    plan = load_cleanup_plan()
    if not plan:
        return 1
    
    # Get completed tests
    completed = get_completed_tests()
    
    # Filter tests to process
    all_tests = plan['tests_to_clean']
    remaining = [t for t in all_tests if t['key'] not in completed]
    
    print(f"📊 Label Cleanup Status")
    print(f"   Total tests: {len(all_tests)}")
    print(f"   Completed: {len(completed)}")
    print(f"   Remaining: {len(remaining)}")
    
    if not remaining:
        print("\n✅ All tests have been processed!")
        return 0
    
    print("\n" + "="*80)
    print("TESTS TO PROCESS")
    print("="*80)
    
    results = []
    
    # Group by batch for easier processing
    batch_size = 10
    for i in range(0, len(remaining), batch_size):
        batch = remaining[i:i+batch_size]
        batch_num = i // batch_size + 1
        
        print(f"\nBatch {batch_num} ({len(batch)} tests):")
        for test in batch:
            print(f"  {test['key']}: Remove {test['labels_to_remove']}")
            results.append({
                'key': test['key'],
                'new_labels': test['new_labels'],
                'batch': batch_num
            })
    
    # Save execution plan
    log_file = save_execution_log(results)
    print(f"\n✓ Execution plan saved to: {log_file}")
    
    # Output commands for processing
    print("\n" + "="*80)
    print("READY FOR EXECUTION")
    print("="*80)
    print(f"Use JIRA MCP tools to update {len(remaining)} tests")
    print("Each test needs: mcp__mcp-atlassian__jira_update_issue")
    
    return 0

if __name__ == "__main__":
    main()