#!/usr/bin/env python3
"""
Find which test has coverable issues in extra-info-response.json
"""

import json

# Read the file
with open('/Users/douglas.mason/Documents/GitHub/xray-importer/mlbmob/extra-info-response.json', 'r') as f:
    data = json.load(f)

# Find tests array
def find_tests(obj):
    """Recursively find the tests array in the JSON structure."""
    if isinstance(obj, list):
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
    # Find test with coverable issues
    for test in tests:
        if 'coverableIssues' in test and 'results' in test['coverableIssues']:
            if len(test['coverableIssues']['results']) > 0:
                print(f"Test with coverable issues:")
                print(f"  Issue ID: {test['issueId']}")
                print(f"  JIRA Key: {test['jira']['key']}")
                print(f"  Summary: {test['jira']['summary']}")
                print(f"  Total coverable issues: {test['coverableIssues']['total']}")
                print(f"\nCoverable issues details:")
                for issue in test['coverableIssues']['results']:
                    print(f"  - {json.dumps(issue, indent=4)}")
                break
else:
    print("Could not find tests array")