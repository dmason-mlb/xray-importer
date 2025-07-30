#!/usr/bin/env python3
"""
Bulk update labels for all remaining tests.
This script generates commands for updating all tests that need label cleanup.
"""

import json
import time
from pathlib import Path
from datetime import datetime

def load_tests_to_update():
    """Load the list of tests to update"""
    file_path = Path(__file__).parent.parent / 'logs' / 'tests_to_update.json'
    
    with open(file_path, 'r') as f:
        return json.load(f)

def get_completed_tests():
    """Return list of tests already completed"""
    # Tests we've already updated
    return ['FRAMED-1425', 'FRAMED-1424', 'FRAMED-1423', 'FRAMED-1422']

def main():
    """Main execution"""
    # Load all tests
    all_tests = load_tests_to_update()
    completed = get_completed_tests()
    
    # Filter out completed tests
    remaining_tests = [t for t in all_tests if t['key'] not in completed]
    
    print(f"Total tests: {len(all_tests)}")
    print(f"Completed: {len(completed)}")
    print(f"Remaining: {len(remaining_tests)}")
    print("\n" + "="*80)
    print("REMAINING TESTS TO UPDATE")
    print("="*80)
    
    # Create update log
    log_file = Path(__file__).parent.parent / 'logs' / f'bulk_update_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
    
    with open(log_file, 'w') as log:
        log.write(f"Bulk Label Update Log\n")
        log.write(f"Started: {datetime.now().isoformat()}\n")
        log.write(f"Total remaining: {len(remaining_tests)}\n\n")
        
        # Process in batches of 5
        batch_size = 5
        for i in range(0, len(remaining_tests), batch_size):
            batch = remaining_tests[i:i+batch_size]
            batch_num = i // batch_size + 1
            
            print(f"\nBatch {batch_num} ({len(batch)} tests):")
            log.write(f"\nBatch {batch_num}:\n")
            
            for test in batch:
                print(f"  - {test['key']}: {test['labels']}")
                log.write(f"  {test['key']}: {json.dumps(test['labels'])}\n")
    
    print(f"\n✓ Update log created: {log_file}")
    
    # Save the remaining tests for processing
    remaining_file = Path(__file__).parent.parent / 'logs' / 'remaining_tests.json'
    with open(remaining_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'completed': completed,
            'remaining': remaining_tests,
            'total_remaining': len(remaining_tests)
        }, f, indent=2)
    
    print(f"✓ Remaining tests saved to: {remaining_file}")
    
    # Show next batch to process
    if remaining_tests:
        print("\n" + "="*80)
        print("NEXT BATCH TO PROCESS (5 tests):")
        print("="*80)
        for test in remaining_tests[:5]:
            print(f"\n{test['key']}:")
            print(f"  Labels: {test['labels']}")
    
    return 0

if __name__ == "__main__":
    main()