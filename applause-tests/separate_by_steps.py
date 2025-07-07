#!/usr/bin/env python3
"""
Script to separate tests based on whether they have test steps.
Creates two files: tests_with_steps.json and tests_without_steps.json
"""

import json
import os

def separate_tests_by_steps():
    """Read combined_responses.json and separate tests by step presence."""
    
    # Read the combined file
    combined_path = os.path.join(os.path.dirname(__file__), "combined_responses.json")
    
    try:
        with open(combined_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("✗ combined_responses.json not found. Run combine_responses.py first.")
        return
    except Exception as e:
        print(f"✗ Error reading combined file: {e}")
        return
    
    # Initialize structures for both categories
    tests_with_steps = {
        "data": {
            "getExpandedTests": {
                "total": 0,
                "results": []
            }
        }
    }
    
    tests_without_steps = {
        "data": {
            "getExpandedTests": {
                "total": 0,
                "results": []
            }
        }
    }
    
    # Process each test
    all_tests = data["data"]["getExpandedTests"]["results"]
    
    for test in all_tests:
        steps = test.get("steps", [])
        
        if steps and len(steps) > 0:
            # Test has steps
            tests_with_steps["data"]["getExpandedTests"]["results"].append(test)
        else:
            # Test has no steps
            tests_without_steps["data"]["getExpandedTests"]["results"].append(test)
    
    # Update totals
    tests_with_steps["data"]["getExpandedTests"]["total"] = len(tests_with_steps["data"]["getExpandedTests"]["results"])
    tests_without_steps["data"]["getExpandedTests"]["total"] = len(tests_without_steps["data"]["getExpandedTests"]["results"])
    
    # Save files
    with_steps_path = os.path.join(os.path.dirname(__file__), "tests_with_steps.json")
    without_steps_path = os.path.join(os.path.dirname(__file__), "tests_without_steps.json")
    
    with open(with_steps_path, 'w') as f:
        json.dump(tests_with_steps, f, indent=2)
    
    with open(without_steps_path, 'w') as f:
        json.dump(tests_without_steps, f, indent=2)
    
    print(f"✓ Files created successfully:")
    print(f"  - tests_with_steps.json: {tests_with_steps['data']['getExpandedTests']['total']} tests")
    print(f"  - tests_without_steps.json: {tests_without_steps['data']['getExpandedTests']['total']} tests")
    
    # Print summary of tests without steps
    if tests_without_steps["data"]["getExpandedTests"]["total"] > 0:
        print(f"\nTests without steps:")
        for test in tests_without_steps["data"]["getExpandedTests"]["results"]:
            key = test["jira"]["key"]
            summary = test["jira"]["summary"]
            folder_path = test["folder"]["path"]
            print(f"  • {key} - {summary}")
            print(f"    Folder: {folder_path}")

if __name__ == "__main__":
    separate_tests_by_steps()