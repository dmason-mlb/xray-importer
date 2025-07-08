#!/usr/bin/env python3
"""
Merge test results from multiple JSON files to get complete dataset.
"""

import json
import os

def merge_results():
    """Merge test results from original mlbmob folder with current results."""
    
    # Paths to files
    original_with_steps = "../mlbmob/tests_with_steps.json"
    original_without_steps = "../mlbmob/tests_without_steps.json"
    current_with_steps = "tests_with_steps.json"
    current_without_steps = "tests_without_steps.json"
    
    # Load all data
    all_tests_with_steps = []
    all_tests_without_steps = []
    all_issue_ids = set()
    
    # Load original data if exists
    if os.path.exists(original_with_steps):
        with open(original_with_steps, 'r') as f:
            data = json.load(f)
            tests = data.get('tests', data) if isinstance(data, dict) else data
            for test in tests:
                issue_id = test.get('issueId')
                if issue_id and issue_id not in all_issue_ids:
                    all_issue_ids.add(issue_id)
                    all_tests_with_steps.append(test)
        print(f"Loaded {len(all_tests_with_steps)} tests with steps from original file")
    
    if os.path.exists(original_without_steps):
        with open(original_without_steps, 'r') as f:
            data = json.load(f)
            tests = data.get('tests', data) if isinstance(data, dict) else data
            for test in tests:
                issue_id = test.get('issueId')
                if issue_id and issue_id not in all_issue_ids:
                    all_issue_ids.add(issue_id)
                    all_tests_without_steps.append(test)
        print(f"Loaded {len(all_tests_without_steps)} tests without steps from original file")
    
    # Load current data
    if os.path.exists(current_with_steps):
        with open(current_with_steps, 'r') as f:
            data = json.load(f)
            tests = data.get('tests', [])
            added = 0
            for test in tests:
                issue_id = test.get('issueId')
                if issue_id and issue_id not in all_issue_ids:
                    all_issue_ids.add(issue_id)
                    all_tests_with_steps.append(test)
                    added += 1
        print(f"Added {added} new tests with steps from current file")
    
    if os.path.exists(current_without_steps):
        with open(current_without_steps, 'r') as f:
            data = json.load(f)
            tests = data.get('tests', [])
            added = 0
            for test in tests:
                issue_id = test.get('issueId')
                if issue_id and issue_id not in all_issue_ids:
                    all_issue_ids.add(issue_id)
                    all_tests_without_steps.append(test)
                    added += 1
        print(f"Added {added} new tests without steps from current file")
    
    # Save merged results
    with open('tests_with_steps_complete.json', 'w') as f:
        json.dump({
            "project_id": "26420",
            "total": len(all_tests_with_steps),
            "tests": all_tests_with_steps
        }, f, indent=2)
    
    with open('tests_without_steps_complete.json', 'w') as f:
        json.dump({
            "project_id": "26420",
            "total": len(all_tests_without_steps),
            "tests": all_tests_without_steps
        }, f, indent=2)
    
    print(f"\nMerge complete!")
    print(f"Total unique tests: {len(all_issue_ids)}")
    print(f"Tests with steps: {len(all_tests_with_steps)}")
    print(f"Tests without steps: {len(all_tests_without_steps)}")
    print(f"\nSaved to:")
    print(f"  - tests_with_steps_complete.json")
    print(f"  - tests_without_steps_complete.json")

if __name__ == "__main__":
    merge_results()