#!/usr/bin/env python3
"""
Compare tests without steps to tests in MLBMOB-2651 test set
"""

import json

# Load the 76 tests without steps
with open('mlbmob/tests_without_steps.json', 'r') as f:
    tests_without_steps = json.load(f)

# Load the 386 tests from MLBMOB-2651
with open('mlbmob_2651_all_tests.json', 'r') as f:
    test_set_data = json.load(f)

# Extract test keys from both sources
tests_without_steps_keys = {test['jira']['key'] for test in tests_without_steps['tests']}
test_set_keys = set(test_set_data['test_keys'])

# Find tests that are in both lists
tests_in_both = tests_without_steps_keys.intersection(test_set_keys)

# Create detailed comparison
tests_in_both_details = []
for test in tests_without_steps['tests']:
    if test['jira']['key'] in tests_in_both:
        # Find the test in the test set data
        test_set_info = next((t for t in test_set_data['tests'] if t['key'] == test['jira']['key']), None)
        
        tests_in_both_details.append({
            'key': test['jira']['key'],
            'summary': test['jira']['summary'],
            'issueId': test['issueId'],
            'status': test_set_info['status'] if test_set_info else 'Unknown',
            'has_preconditions': test['preconditions']['total'] > 0
        })

# Sort by key
tests_in_both_details.sort(key=lambda x: x['key'])

# Print results
print("Comparison Results")
print("=" * 80)
print(f"Total tests without steps: {len(tests_without_steps_keys)}")
print(f"Total tests in MLBMOB-2651: {len(test_set_keys)}")
print(f"Tests in both lists: {len(tests_in_both)}")
print()

print("Tests from the 76 without steps that ARE in MLBMOB-2651:")
print("-" * 80)
for i, test in enumerate(tests_in_both_details, 1):
    print(f"{i:2d}. {test['key']}: {test['summary']}")
    print(f"    Status: {test['status']}")
    print(f"    Has Preconditions: {test['has_preconditions']}")
    print()

# Tests NOT in the test set
tests_not_in_set = tests_without_steps_keys - test_set_keys
tests_not_in_set_details = []

for test in tests_without_steps['tests']:
    if test['jira']['key'] in tests_not_in_set:
        tests_not_in_set_details.append({
            'key': test['jira']['key'],
            'summary': test['jira']['summary'],
            'issueId': test['issueId'],
            'has_preconditions': test['preconditions']['total'] > 0
        })

tests_not_in_set_details.sort(key=lambda x: x['key'])

print("\nTests from the 76 without steps that are NOT in MLBMOB-2651:")
print("-" * 80)
for i, test in enumerate(tests_not_in_set_details, 1):
    print(f"{i:2d}. {test['key']}: {test['summary']}")
    print(f"    Has Preconditions: {test['has_preconditions']}")
    print()

# Save results
results = {
    'comparison_summary': {
        'total_tests_without_steps': len(tests_without_steps_keys),
        'total_tests_in_mlbmob_2651': len(test_set_keys),
        'tests_in_both': len(tests_in_both),
        'tests_not_in_set': len(tests_not_in_set)
    },
    'tests_in_both': tests_in_both_details,
    'tests_not_in_set': tests_not_in_set_details,
    'test_keys_in_both': sorted(list(tests_in_both)),
    'test_keys_not_in_set': sorted(list(tests_not_in_set))
}

with open('comparison_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nDetailed results saved to comparison_results.json")

# Summary
print("\nSUMMARY")
print("=" * 80)
print(f"Out of 76 tests without steps:")
print(f"- {len(tests_in_both)} tests ({len(tests_in_both)/len(tests_without_steps_keys)*100:.1f}%) are in MLBMOB-2651")
print(f"- {len(tests_not_in_set)} tests ({len(tests_not_in_set)/len(tests_without_steps_keys)*100:.1f}%) are NOT in MLBMOB-2651")