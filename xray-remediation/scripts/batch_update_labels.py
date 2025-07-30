#!/usr/bin/env python3
"""
Batch update labels for all tests in the cleanup plan.
This script processes the tests and generates the JIRA update commands.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

def load_execution_data():
    """Load the most recent execution data"""
    logs_dir = Path(__file__).parent.parent / 'logs'
    exec_files = list(logs_dir.glob('label_cleanup_execution_*.json'))
    
    if not exec_files:
        print("❌ No execution data found.")
        return None
        
    # Get the most recent file
    latest_file = max(exec_files, key=lambda p: p.stat().st_mtime)
    print(f"Loading execution data from: {latest_file}")
    
    with open(latest_file, 'r') as f:
        return json.load(f)

def generate_update_script(tests):
    """Generate a script with all JIRA update commands"""
    script_lines = [
        "#!/bin/bash",
        "# Label cleanup script - Updates all test labels",
        f"# Generated: {datetime.now().isoformat()}",
        f"# Total tests: {len(tests)}",
        "",
        "# This script contains the JIRA update commands for all tests",
        "# Execute with Claude Code using JIRA MCP tools",
        "",
    ]
    
    # Add update commands for each test
    for i, test in enumerate(tests, 1):
        script_lines.append(f"# Test {i}/{len(tests)}: {test['key']}")
        script_lines.append(f"# Removing: {test['labels_to_remove']}")
        
        # Create the update command
        new_labels_json = json.dumps(test['new_labels'])
        script_lines.append(f"echo 'Updating {test['key']}...'")
        script_lines.append(f"# New labels: {new_labels_json}")
        script_lines.append("")
    
    return "\n".join(script_lines)

def save_batch_results(tests):
    """Save batch processing results"""
    results_file = Path(__file__).parent.parent / 'logs' / f'label_cleanup_batch_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    
    batch_data = {
        'timestamp': datetime.now().isoformat(),
        'total_tests': len(tests),
        'batch_size': 10,  # Process in batches of 10
        'batches': []
    }
    
    # Create batches
    for i in range(0, len(tests), 10):
        batch = tests[i:i+10]
        batch_data['batches'].append({
            'batch_number': i // 10 + 1,
            'tests': batch,
            'test_keys': [t['key'] for t in batch]
        })
    
    with open(results_file, 'w') as f:
        json.dump(batch_data, f, indent=2)
    
    print(f"\n✓ Batch data saved to: {results_file}")
    return batch_data

def main():
    """Main execution"""
    # Load execution data
    data = load_execution_data()
    if not data:
        return 1
    
    tests = data['tests']
    print(f"\n📋 Processing {len(tests)} tests for label cleanup")
    
    # Generate update script
    script_content = generate_update_script(tests)
    script_file = Path(__file__).parent.parent / 'logs' / f'label_cleanup_commands_{datetime.now().strftime("%Y%m%d_%H%M%S")}.sh'
    
    with open(script_file, 'w') as f:
        f.write(script_content)
    
    print(f"✓ Update script saved to: {script_file}")
    
    # Save batch processing data
    batch_data = save_batch_results(tests)
    
    print(f"\n📊 Batch Processing Summary:")
    print(f"   Total tests: {batch_data['total_tests']}")
    print(f"   Number of batches: {len(batch_data['batches'])}")
    print(f"   Batch size: {batch_data['batch_size']}")
    
    print("\n" + "="*80)
    print("READY TO EXECUTE")
    print("="*80)
    print("The tests have been organized into batches for processing.")
    print("Use the JIRA MCP tools to update each batch of tests.")
    
    # Show first batch as example
    first_batch = batch_data['batches'][0]
    print(f"\nFirst batch ({len(first_batch['tests'])} tests):")
    for test in first_batch['tests'][:3]:
        print(f"  - {test['key']}: {test['summary'][:50]}...")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())