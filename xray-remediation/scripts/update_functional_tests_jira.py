#!/usr/bin/env python3
"""
Update functional tests via JIRA REST API:
1. Update labels from 'functional' to 'functional_test'
2. Set priorities based on label hierarchy
"""
import os
import json
import sys
import time
import requests
from pathlib import Path
from datetime import datetime
from requests.auth import HTTPBasicAuth

def get_jira_auth():
    """Get JIRA authentication from environment variables"""
    email = os.environ.get('JIRA_EMAIL')
    api_token = os.environ.get('JIRA_API_TOKEN')
    
    if not email or not api_token:
        raise ValueError("JIRA_EMAIL and JIRA_API_TOKEN environment variables must be set")
    
    return HTTPBasicAuth(email, api_token)

def get_jira_base_url():
    """Get JIRA base URL from environment variable"""
    base_url = os.environ.get('JIRA_BASE_URL', 'https://jira.mlbinfra.com')
    return base_url.rstrip('/')

def determine_priority(labels):
    """Determine priority based on labels"""
    if 'critical' in labels:
        return 'Critical'
    elif 'high' in labels:
        return 'High'
    elif 'low' in labels:
        return 'Low'
    else:
        return 'Medium'  # Default

def update_issue_labels_and_priority(issue_key, new_labels, priority):
    """Update issue labels and priority via JIRA REST API"""
    base_url = get_jira_base_url()
    auth = get_jira_auth()
    
    # Prepare update data
    update_data = {
        "fields": {
            "labels": new_labels
        }
    }
    
    # Add priority if it needs updating
    if priority:
        # Get priority ID
        priority_url = f"{base_url}/rest/api/2/priority"
        response = requests.get(priority_url, auth=auth)
        response.raise_for_status()
        priorities = response.json()
        
        priority_id = None
        for p in priorities:
            if p['name'] == priority:
                priority_id = p['id']
                break
        
        if priority_id:
            update_data['fields']['priority'] = {"id": priority_id}
    
    # Update the issue
    url = f"{base_url}/rest/api/2/issue/{issue_key}"
    response = requests.put(url, json=update_data, auth=auth)
    
    if response.status_code == 204:
        return True, "Updated successfully"
    else:
        return False, f"Error {response.status_code}: {response.text}"

def main():
    # Load test keys to update
    tests_file = Path(__file__).parent.parent / "logs" / "tests_to_update_labels.json"
    with open(tests_file, 'r') as f:
        test_data = json.load(f)
    
    tests_to_update = test_data['tests_to_update']
    
    print(f"=== UPDATING FUNCTIONAL TESTS VIA JIRA API ===")
    print(f"Total tests to update: {len(tests_to_update)}")
    
    # Results tracking
    results = {
        'timestamp': datetime.now().isoformat(),
        'total_tests': len(tests_to_update),
        'updated': [],
        'errors': []
    }
    
    # Process each test
    for i, test_key in enumerate(tests_to_update, 1):
        print(f"\n[{i}/{len(tests_to_update)}] Processing {test_key}...")
        
        try:
            # Get current issue details
            base_url = get_jira_base_url()
            auth = get_jira_auth()
            url = f"{base_url}/rest/api/2/issue/{test_key}?fields=labels,priority"
            
            response = requests.get(url, auth=auth)
            response.raise_for_status()
            issue = response.json()
            
            current_labels = issue['fields']['labels']
            current_priority = issue['fields']['priority']['name'] if issue['fields']['priority'] else 'None'
            
            print(f"  Current labels: {current_labels}")
            print(f"  Current priority: {current_priority}")
            
            # Update labels
            new_labels = []
            for label in current_labels:
                if label == 'functional':
                    new_labels.append('functional_test')
                else:
                    new_labels.append(label)
            
            # Determine new priority
            expected_priority = determine_priority(new_labels)
            priority_update = expected_priority if current_priority != expected_priority else None
            
            print(f"  New labels: {new_labels}")
            if priority_update:
                print(f"  New priority: {priority_update}")
            
            # Apply updates
            success, message = update_issue_labels_and_priority(test_key, new_labels, priority_update)
            
            if success:
                print(f"  ✓ {message}")
                results['updated'].append({
                    'key': test_key,
                    'labels_updated': 'functional' in current_labels,
                    'priority_updated': priority_update is not None,
                    'new_priority': priority_update
                })
            else:
                print(f"  ✗ {message}")
                results['errors'].append({
                    'key': test_key,
                    'error': message
                })
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
            results['errors'].append({
                'key': test_key,
                'error': str(e)
            })
        
        # Rate limiting
        time.sleep(0.5)
    
    # Save results
    output_path = Path(__file__).parent.parent / "logs" / f"jira_update_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Summary
    print(f"\n=== SUMMARY ===")
    print(f"Total tests processed: {len(tests_to_update)}")
    print(f"Successfully updated: {len(results['updated'])}")
    print(f"Errors: {len(results['errors'])}")
    
    if results['errors']:
        print("\nFailed updates:")
        for error in results['errors']:
            print(f"  - {error['key']}: {error['error']}")
    
    print(f"\nResults saved to: {output_path}")

if __name__ == "__main__":
    main()