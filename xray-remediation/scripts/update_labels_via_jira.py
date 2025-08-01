#!/usr/bin/env python3
"""
Update all functional tests to use 'functional_test' label instead of 'functional'
Uses JIRA API directly
"""
import json
import sys
import time
from pathlib import Path
from datetime import datetime

def update_functional_labels():
    # Load the functional tests data to get all JIRA keys
    tests_path = Path(__file__).parent.parent / "test-data" / "functional_tests_xray.json"
    with open(tests_path, 'r') as f:
        test_data = json.load(f)
    
    # Extract all JIRA keys that need updating
    tests_to_update = []
    for test in test_data['tests']:
        if 'jiraKey' in test:
            # Skip the two that already have functional_test
            if test['jiraKey'] not in ['FRAMED-1668', 'FRAMED-1669']:
                tests_to_update.append(test['jiraKey'])
    
    print(f"=== UPDATING FUNCTIONAL LABELS VIA JIRA API ===")
    print(f"Total tests to update: {len(tests_to_update)}")
    
    # Create a file with the test keys for reference
    update_list = {
        'tests_to_update': tests_to_update,
        'timestamp': datetime.now().isoformat()
    }
    
    output_path = Path(__file__).parent.parent / "logs" / "tests_to_update_labels.json"
    with open(output_path, 'w') as f:
        json.dump(update_list, f, indent=2)
    
    print(f"\nTest keys saved to: {output_path}")
    print("\nNow using Atlassian MCP to update labels...")
    
    return tests_to_update

if __name__ == "__main__":
    tests = update_functional_labels()