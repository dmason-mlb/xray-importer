#!/usr/bin/env python3
"""
Complete the label cleanup for all remaining tests.
This script generates a summary of all tests that need to be updated.
"""

import json
from pathlib import Path
from datetime import datetime

def load_remaining_tests():
    """Load the remaining tests"""
    file_path = Path(__file__).parent.parent / 'logs' / 'remaining_tests.json'
    
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Update completed list
    completed = ['FRAMED-1425', 'FRAMED-1424', 'FRAMED-1423', 'FRAMED-1422', 
                 'FRAMED-1421', 'FRAMED-1420', 'FRAMED-1419', 'FRAMED-1418', 'FRAMED-1417']
    
    # Filter out newly completed tests
    remaining = [t for t in data['remaining'] if t['key'] not in completed]
    
    return completed, remaining

def save_progress(completed, remaining):
    """Save current progress"""
    progress_file = Path(__file__).parent.parent / 'logs' / f'label_cleanup_progress_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    
    with open(progress_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'completed_count': len(completed),
            'completed_tests': completed,
            'remaining_count': len(remaining),
            'remaining_tests': [t['key'] for t in remaining],
            'next_batch': remaining[:10] if remaining else []
        }, f, indent=2)
    
    return progress_file

def main():
    """Main execution"""
    completed, remaining = load_remaining_tests()
    
    print(f"📊 Label Cleanup Progress")
    print(f"   Completed: {len(completed)} tests")
    print(f"   Remaining: {len(remaining)} tests")
    print(f"   Progress: {len(completed)}/47 ({len(completed)/47*100:.1f}%)")
    
    # Save progress
    progress_file = save_progress(completed, remaining)
    print(f"\n✓ Progress saved to: {progress_file}")
    
    if remaining:
        print("\n" + "="*80)
        print("NEXT 10 TESTS TO PROCESS:")
        print("="*80)
        
        for i, test in enumerate(remaining[:10], 1):
            print(f"\n{i}. {test['key']}:")
            print(f"   Labels: {test['labels']}")
        
        # Create a simple batch file for the next 10
        batch_file = Path(__file__).parent.parent / 'logs' / 'next_batch.json'
        with open(batch_file, 'w') as f:
            json.dump(remaining[:10], f, indent=2)
        
        print(f"\n✓ Next batch saved to: {batch_file}")
    else:
        print("\n✅ All tests have been processed!")
    
    return 0

if __name__ == "__main__":
    main()