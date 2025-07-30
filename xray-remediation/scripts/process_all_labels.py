#!/usr/bin/env python3
"""
Process all label updates from the batch file.
Outputs the list of tests to update for Claude Code to process.
"""

import json
from pathlib import Path

def load_batch_data():
    """Load the most recent batch data"""
    logs_dir = Path(__file__).parent.parent / 'logs'
    batch_files = list(logs_dir.glob('label_cleanup_batch_*.json'))
    
    if not batch_files:
        print("❌ No batch data found.")
        return None
        
    # Get the most recent file
    latest_file = max(batch_files, key=lambda p: p.stat().st_mtime)
    
    with open(latest_file, 'r') as f:
        return json.load(f)

def main():
    """Main execution"""
    # Load batch data
    data = load_batch_data()
    if not data:
        return 1
    
    # Collect all tests from all batches
    all_tests = []
    for batch in data['batches']:
        all_tests.extend(batch['tests'])
    
    print(f"Total tests to process: {len(all_tests)}")
    print("\nTests ready for label cleanup:")
    print("="*80)
    
    # Output in a format that's easy to process
    for i, test in enumerate(all_tests, 1):
        print(f"\n{i}. {test['key']}")
        print(f"   Current: {test['current_labels']}")
        print(f"   New: {test['new_labels']}")
    
    # Save a simple list for processing
    simple_list = []
    for test in all_tests:
        simple_list.append({
            'key': test['key'],
            'labels': test['new_labels']
        })
    
    output_file = Path(__file__).parent.parent / 'logs' / 'tests_to_update.json'
    with open(output_file, 'w') as f:
        json.dump(simple_list, f, indent=2)
    
    print(f"\n✓ Simple update list saved to: {output_file}")
    print(f"Total: {len(simple_list)} tests")
    
    return 0

if __name__ == "__main__":
    main()