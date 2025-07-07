#!/usr/bin/env python3
"""
Analyze extra-info-response.json to count non-empty results and non-null fields.
"""

import json

# Read the file
with open('/Users/douglas.mason/Documents/GitHub/xray-importer/mlbmob/extra-info-response.json', 'r') as f:
    data = json.load(f)

# Initialize counters
preconditions_non_empty = 0
test_sets_non_empty = 0
test_plans_non_empty = 0
coverable_issues_non_empty = 0
dataset_non_null = 0
scenario_type_non_null = 0

# Get the tests array (need to find the right path in the JSON structure)
# Based on the example, it seems tests are in an array somewhere in the data
def find_tests(obj):
    """Recursively find the tests array in the JSON structure."""
    if isinstance(obj, list):
        # Check if this looks like a tests array
        if len(obj) > 0 and isinstance(obj[0], dict) and 'issueId' in obj[0]:
            return obj
    elif isinstance(obj, dict):
        for key, value in obj.items():
            result = find_tests(value)
            if result is not None:
                return result
    return None

tests = find_tests(data)

if tests:
    print(f"Found {len(tests)} tests to analyze\n")
    
    # Analyze each test
    for test in tests:
        # Check preconditions
        if 'preconditions' in test and 'results' in test['preconditions']:
            if len(test['preconditions']['results']) > 0:
                preconditions_non_empty += 1
        
        # Check testSets
        if 'testSets' in test and 'results' in test['testSets']:
            if len(test['testSets']['results']) > 0:
                test_sets_non_empty += 1
        
        # Check testPlans
        if 'testPlans' in test and 'results' in test['testPlans']:
            if len(test['testPlans']['results']) > 0:
                test_plans_non_empty += 1
        
        # Check coverableIssues
        if 'coverableIssues' in test and 'results' in test['coverableIssues']:
            if len(test['coverableIssues']['results']) > 0:
                coverable_issues_non_empty += 1
        
        # Check dataset
        if 'dataset' in test and test['dataset'] is not None:
            dataset_non_null += 1
        
        # Check scenarioType
        if 'scenarioType' in test and test['scenarioType'] is not None:
            scenario_type_non_null += 1
    
    # Print results
    print("Non-empty 'results' fields:")
    print(f"  - preconditions: {preconditions_non_empty}")
    print(f"  - testSets: {test_sets_non_empty}")
    print(f"  - testPlans: {test_plans_non_empty}")
    print(f"  - coverableIssues: {coverable_issues_non_empty}")
    print()
    print("Non-null fields:")
    print(f"  - dataset: {dataset_non_null}")
    print(f"  - scenarioType: {scenario_type_non_null}")
    
    # Also print some examples if found
    print("\nExamples of non-empty results:")
    
    example_count = 0
    for test in tests:
        if example_count >= 3:
            break
            
        if 'testSets' in test and 'results' in test['testSets'] and len(test['testSets']['results']) > 0:
            print(f"\nTest {test['jira']['key']} has {test['testSets']['total']} test set(s):")
            for ts in test['testSets']['results'][:2]:  # Show first 2
                print(f"  - {ts['jira']['key']}: {ts['jira']['summary']}")
            example_count += 1

else:
    print("Could not find tests array in the JSON structure")
    print("JSON structure keys:", list(data.keys()) if isinstance(data, dict) else "Not a dict")