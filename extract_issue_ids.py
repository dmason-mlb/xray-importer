#!/usr/bin/env python3
"""
Extract issueIds from tests without steps JSON file.
"""

import json

# Based on the data structure shown, here are the issueIds
# Since you mentioned there are 77 tests and showed the first 3,
# I'll create an array with the issueIds from the examples provided

issue_ids = [
    "1153134",  # MLBMOB-2443
    "1153119",  # MLBMOB-2441
    "1153118",  # MLBMOB-2440
]

# If you have the full JSON file, you can use this code to extract all issueIds:
def extract_issue_ids_from_file(filename):
    """Extract all issueIds from the JSON file."""
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        
        issue_ids = []
        tests = data.get("tests", [])
        
        for test in tests:
            issue_id = test.get("issueId")
            if issue_id:
                issue_ids.append(issue_id)
        
        return issue_ids
    except Exception as e:
        print(f"Error reading file: {e}")
        return []

# Print the issueIds we have from the examples
print("IssueIds from the first 3 tests:")
print(json.dumps(issue_ids, indent=2))

# If you want to extract from the full file, uncomment this:
# all_issue_ids = extract_issue_ids_from_file("path_to_your_file.json")
# print(f"\nTotal issueIds: {len(all_issue_ids)}")
# print(json.dumps(all_issue_ids, indent=2))