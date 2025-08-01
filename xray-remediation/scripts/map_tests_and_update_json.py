#!/usr/bin/env python3
"""
Map existing Xray tests to JSON and update functional_tests_xray.json with JIRA keys
"""
import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir / 'xray-api'))
from auth_utils import XrayAPIClient

def map_tests_and_update_json():
    # Load the missing tests analysis
    analysis_path = Path(__file__).parent.parent / "logs" / "missing_tests_analysis.json"
    with open(analysis_path, 'r') as f:
        analysis = json.load(f)
    
    matched_tests = analysis['matched_tests']
    
    # Load the original functional tests JSON
    tests_path = Path(__file__).parent.parent / "test-data" / "functional_tests_xray.json"
    with open(tests_path, 'r') as f:
        test_data = json.load(f)
    
    print(f"=== MAPPING TESTS AND UPDATING JSON ===")
    print(f"Matched tests to process: {len(matched_tests)}")
    
    # Create a mapping of summaries to JIRA keys
    summary_to_key = {}
    for match in matched_tests:
        xray_test = match['xray_test']
        json_test = match['json_test']
        
        summary = json_test['testInfo']['summary']
        jira_key = xray_test['jira']['key']
        summary_to_key[summary] = jira_key
    
    # Update the JSON file with JIRA keys
    updated_count = 0
    for test in test_data['tests']:
        test_info = test.get('testInfo', {})
        summary = test_info.get('summary', '')
        
        if summary in summary_to_key:
            # Add JIRA key to the test
            test['jiraKey'] = summary_to_key[summary]
            updated_count += 1
            print(f"✓ Mapped: {summary} → {summary_to_key[summary]}")
            
            # Also update the label from 'functional' to 'functional_test'
            if 'labels' in test_info:
                labels = test_info['labels']
                if 'functional' in labels:
                    labels[labels.index('functional')] = 'functional_test'
        else:
            print(f"✗ Not found in Xray: {summary}")
    
    # Create backup of original file
    backup_path = tests_path.with_suffix('.json.backup_' + datetime.now().strftime('%Y%m%d_%H%M%S'))
    import shutil
    shutil.copy2(tests_path, backup_path)
    print(f"\n✓ Created backup: {backup_path}")
    
    # Save updated JSON
    with open(tests_path, 'w') as f:
        json.dump(test_data, f, indent=2)
    
    print(f"\n=== SUMMARY ===")
    print(f"Updated {updated_count} tests with JIRA keys")
    print(f"Updated functional_tests_xray.json")
    
    # Save mapping for reference
    mapping_output = {
        'timestamp': datetime.now().isoformat(),
        'summary_to_key': summary_to_key,
        'updated_count': updated_count
    }
    
    mapping_path = Path(__file__).parent.parent / "logs" / "test_key_mapping.json"
    with open(mapping_path, 'w') as f:
        json.dump(mapping_output, f, indent=2)
    
    print(f"✓ Saved mapping to: {mapping_path}")

if __name__ == "__main__":
    map_tests_and_update_json()