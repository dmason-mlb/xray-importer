#!/usr/bin/env python3
"""Extract test ID to JIRA key mapping from FRAMED assessment."""

import json
import os

def extract_mapping():
    """Extract mapping of test IDs to JIRA keys."""
    assessment_file = os.path.join(
        os.path.dirname(__file__),
        '../backups/FRAMED_BASIC_ASSESSMENT_20250716_213912.json'
    )
    
    with open(assessment_file, 'r') as f:
        data = json.load(f)
    
    mapping = {}
    for test in data['raw_tests_data']['getTests']['results']:
        labels = test['jira']['labels']
        jira_key = test['jira']['key']
        
        # Find the API test ID label
        for label in labels:
            if label.startswith('API-') and any(c.isdigit() for c in label):
                mapping[label] = jira_key
                break
    
    # Sort by test ID
    sorted_mapping = dict(sorted(mapping.items()))
    
    print("Test ID to JIRA Key Mapping:")
    print("=" * 40)
    for test_id, jira_key in sorted_mapping.items():
        print(f"{test_id} -> {jira_key}")
    
    return sorted_mapping

if __name__ == "__main__":
    mapping = extract_mapping()
    
    # Save mapping to file
    output_file = os.path.join(
        os.path.dirname(__file__),
        '../test_id_to_jira_mapping.json'
    )
    
    with open(output_file, 'w') as f:
        json.dump(mapping, f, indent=2)
    
    print(f"\nMapping saved to: {output_file}")
    print(f"Total mappings: {len(mapping)}")