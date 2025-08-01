#!/usr/bin/env python3
"""
Update all functional tests to use 'functional_test' label instead of 'functional'
Uses GraphQL to update labels
"""
import json
import sys
import time
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir / 'xray-api'))
from auth_utils import XrayAPIClient, log_operation

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
    
    # GraphQL mutation to update test
    mutation = """
    mutation UpdateTest($issueId: String!, $fields: JSON!) {
        updateTest(issueId: $issueId, test: $fields) {
            issueId
            jira(fields: ["key", "labels"])
            warnings
        }
    }
    """
    
    update_results = []
    
    # First, get issueIds for all tests
    print("\n=== GETTING ISSUE IDS ===")
    issue_id_map = {}
    
    query = """
    query GetTestByKey($jql: String!) {
        getTests(jql: $jql, limit: 1) {
            results {
                issueId
                jira(fields: ["key", "labels"])
            }
        }
    }
    """
    
    for key in jira_keys:
        variables = {
            "jql": f"key = {key}"
        }
        
        try:
            result = client.execute_graphql_query(query, variables)
            if result and 'getTests' in result and result['getTests']['results']:
                test_data_result = result['getTests']['results'][0]
                issue_id = test_data_result['issueId']
                current_labels = test_data_result['jira'].get('labels', [])
                issue_id_map[key] = {
                    'issueId': issue_id,
                    'currentLabels': current_labels
                }
                print(f"✓ {key}: Issue ID {issue_id}, Labels: {current_labels}")
            else:
                print(f"✗ {key}: Not found")
        except Exception as e:
            print(f"✗ {key}: Error - {e}")
    
    print(f"\n=== UPDATING LABELS ===")
    
    for i, key in enumerate(jira_keys, 1):
        if key not in issue_id_map:
            print(f"\n[{i}/{len(jira_keys)}] Skipping {key} - no issue ID")
            continue
            
        issue_info = issue_id_map[key]
        issue_id = issue_info['issueId']
        current_labels = issue_info['currentLabels']
        
        print(f"\n[{i}/{len(jira_keys)}] Updating {key}...")
        print(f"  Current labels: {current_labels}")
        
        # Check if update needed
        if 'functional' not in current_labels:
            print(f"  ✓ Already has correct labels")
            update_results.append({
                'key': key,
                'status': 'skipped',
                'labels': current_labels
            })
            continue
        
        # Update labels
        new_labels = []
        for label in current_labels:
            if label == 'functional':
                new_labels.append('functional_test')
            else:
                new_labels.append(label)
        
        # Prepare update
        update_fields = {
            "fields": {
                "labels": new_labels
            }
        }
        
        variables = {
            "issueId": issue_id,
            "fields": update_fields
        }
        
        try:
            result = client.execute_graphql_query(mutation, variables)
            
            if result and 'updateTest' in result:
                updated_labels = result['updateTest']['jira'].get('labels', [])
                print(f"  ✓ Updated labels to: {updated_labels}")
                update_results.append({
                    'key': key,
                    'status': 'updated',
                    'old_labels': current_labels,
                    'new_labels': updated_labels
                })
                
                # Log operation
                log_operation("update_functional_label", {
                    "key": key,
                    "issueId": issue_id,
                    "old_labels": current_labels,
                    "new_labels": updated_labels
                })
            else:
                print(f"  ✗ Failed to update")
                update_results.append({
                    'key': key,
                    'status': 'error',
                    'error': 'No result from mutation'
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