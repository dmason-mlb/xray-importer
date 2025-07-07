#!/usr/bin/env python3
"""
Extract all issueIds from the tests_without_steps.json file.
"""

import json

# Read the file
with open('/Users/douglas.mason/Documents/GitHub/xray-importer/mlbmob/tests_without_steps.json', 'r') as f:
    data = json.load(f)

# Extract all issueIds
issue_ids = []
for test in data['tests']:
    issue_ids.append(test['issueId'])

# Print the array
print(f"Total tests without steps: {len(issue_ids)}")
print("\nArray of issueIds:")
print(json.dumps(issue_ids, indent=2))

# Also save to a file for convenience
with open('/Users/douglas.mason/Documents/GitHub/xray-importer/mlbmob/issue_ids_array.json', 'w') as f:
    json.dump(issue_ids, f, indent=2)