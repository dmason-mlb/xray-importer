#!/usr/bin/env python3
"""
Analyze preconditions from functional tests JSON
"""
import json
from collections import Counter
from pathlib import Path

def analyze_preconditions():
    # Load the functional tests JSON
    json_path = Path(__file__).parent.parent / "test-data" / "functional_tests_xray.json"
    
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # Extract all preconditions
    all_preconditions = []
    precondition_to_tests = {}
    
    for test in data['tests']:
        test_id = test.get('testId', 'Unknown')
        test_summary = test['testInfo']['summary']
        preconditions = test['testInfo'].get('preconditions', [])
        
        for precondition in preconditions:
            all_preconditions.append(precondition)
            if precondition not in precondition_to_tests:
                precondition_to_tests[precondition] = []
            precondition_to_tests[precondition].append({
                'testId': test_id,
                'summary': test_summary
            })
    
    # Count unique preconditions and their usage
    precondition_counts = Counter(all_preconditions)
    
    # Print analysis
    print(f"\n=== PRECONDITION ANALYSIS ===")
    print(f"Total tests: {len(data['tests'])}")
    print(f"Total preconditions (including duplicates): {len(all_preconditions)}")
    print(f"Unique preconditions: {len(precondition_counts)}")
    
    print(f"\n=== UNIQUE PRECONDITIONS WITH USAGE ===")
    for idx, (precondition, count) in enumerate(sorted(precondition_counts.items(), key=lambda x: -x[1]), 1):
        print(f"\n{idx}. \"{precondition}\"")
        print(f"   Usage count: {count}")
        print(f"   Used by tests:")
        for test in precondition_to_tests[precondition][:3]:  # Show first 3 tests
            print(f"   - {test['testId']}: {test['summary']}")
        if len(precondition_to_tests[precondition]) > 3:
            print(f"   ... and {len(precondition_to_tests[precondition]) - 3} more tests")
    
    # Save precondition mapping for later use
    output_data = {
        'unique_preconditions': list(precondition_counts.keys()),
        'precondition_counts': dict(precondition_counts),
        'precondition_to_tests': precondition_to_tests
    }
    
    output_path = Path(__file__).parent.parent / "logs" / "precondition_analysis.json"
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n=== SAVED ANALYSIS TO: {output_path} ===")
    
    return output_data

if __name__ == "__main__":
    analyze_preconditions()