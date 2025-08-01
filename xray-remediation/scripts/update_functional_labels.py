#!/usr/bin/env python3
"""
Update all functional tests to use 'functional_test' label instead of 'functional'
"""
import json
import sys
import time
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir / 'xray-api'))
from auth_utils import XrayAPIClient

def update_functional_labels():
    client = XrayAPIClient()
    
    # Load the functional tests data to get all JIRA keys
    tests_path = Path(__file__).parent.parent / "test-data" / "functional_tests_xray.json"
    with open(tests_path, 'r') as f:
        test_data = json.load(f)
    
    # Extract all JIRA keys
    jira_keys = []
    for test in test_data['tests']:
        if 'jiraKey' in test:
            jira_keys.append(test['jiraKey'])
    
    print(f"=== UPDATING FUNCTIONAL LABELS ===")
    print(f"Total tests to update: {len(jira_keys)}")
    
    # JIRA REST API endpoint for updating issues
    update_results = []
    
    for i, key in enumerate(jira_keys, 1):
        print(f"\n[{i}/{len(jira_keys)}] Updating {key}...")
        
        try:
            # First get current issue details
            issue_url = f"https://xray.cloud.getxray.app/rest/api/2/issue/{key}"
            headers = {
                'Authorization': f'Bearer {client.token}',
                'Content-Type': 'application/json'
            }
            
            # Get current labels
            response = client.session.get(issue_url, headers=headers)
            response.raise_for_status()
            issue_data = response.json()
            
            current_labels = issue_data.get('fields', {}).get('labels', [])
            print(f"  Current labels: {current_labels}")
            
            # Update labels
            new_labels = []
            for label in current_labels:
                if label == 'functional':
                    new_labels.append('functional_test')
                else:
                    new_labels.append(label)
            
            # Only update if changes needed
            if 'functional' in current_labels:
                update_data = {
                    "fields": {
                        "labels": new_labels
                    }
                }
                
                # Update issue
                update_response = client.session.put(issue_url, json=update_data, headers=headers)
                update_response.raise_for_status()
                
                print(f"  ✓ Updated labels to: {new_labels}")
                update_results.append({
                    'key': key,
                    'status': 'updated',
                    'old_labels': current_labels,
                    'new_labels': new_labels
                })
            else:
                print(f"  ✓ Already has correct labels")
                update_results.append({
                    'key': key,
                    'status': 'skipped',
                    'labels': current_labels
                })
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            update_results.append({
                'key': key,
                'status': 'error',
                'error': str(e)
            })
        
        # Rate limiting
        time.sleep(0.5)
    
    # Save results
    results = {
        'timestamp': datetime.now().isoformat(),
        'total_tests': len(jira_keys),
        'results': update_results,
        'summary': {
            'updated': len([r for r in update_results if r['status'] == 'updated']),
            'skipped': len([r for r in update_results if r['status'] == 'skipped']),
            'errors': len([r for r in update_results if r['status'] == 'error'])
        }
    }
    
    output_path = Path(__file__).parent.parent / "logs" / "label_update_results.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n=== SUMMARY ===")
    print(f"Updated: {results['summary']['updated']}")
    print(f"Skipped: {results['summary']['skipped']}")
    print(f"Errors: {results['summary']['errors']}")
    print(f"\nResults saved to: {output_path}")

if __name__ == "__main__":
    update_functional_labels()