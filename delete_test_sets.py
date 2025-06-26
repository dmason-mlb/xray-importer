#!/usr/bin/env python3
"""
Delete the auto-generated Test Sets to fix loading issues
"""

import os
import sys
import time
import requests
from requests.auth import HTTPBasicAuth
import getpass

# Configuration
JIRA_BASE_URL = os.environ.get('JIRA_BASE_URL', 'https://baseball.atlassian.net')
JIRA_EMAIL = os.environ.get('JIRA_EMAIL', '')
JIRA_TOKEN = os.environ.get('ATLASSIAN_TOKEN', '')
PROJECT_KEY = 'MLBAPP'

def delete_test_sets(dry_run=True):
    """Delete auto-generated Test Sets"""
    
    # Get credentials
    global JIRA_EMAIL, JIRA_TOKEN
    
    if not JIRA_EMAIL:
        JIRA_EMAIL = input("Enter JIRA Email: ").strip()
    
    if not JIRA_TOKEN:
        JIRA_TOKEN = getpass.getpass("Enter ATLASSIAN API Token: ").strip()
    
    session = requests.Session()
    session.auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_TOKEN)
    session.headers.update({
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    })
    
    print(f"\nFinding auto-generated Test Sets...")
    print("="*60)
    
    # Query for auto-generated Test Sets
    jql = f'project = {PROJECT_KEY} AND issuetype = "Test Set" AND labels = "auto-generated-test-set"'
    url = f"{JIRA_BASE_URL}/rest/api/2/search"
    
    params = {
        'jql': jql,
        'maxResults': 50,
        'fields': 'summary,labels'
    }
    
    response = session.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        test_sets = data['issues']
        
        print(f"Found {len(test_sets)} auto-generated Test Sets")
        
        if not test_sets:
            print("No auto-generated Test Sets found to delete")
            return
        
        if dry_run:
            print("\n[DRY RUN] Would delete the following Test Sets:")
            for ts in test_sets:
                print(f"  - {ts['key']}: {ts['fields']['summary']}")
            
            print(f"\nTo actually delete these {len(test_sets)} Test Sets, run:")
            print("python3 delete_test_sets.py --confirm")
        else:
            print(f"\n⚠️  WARNING: About to delete {len(test_sets)} Test Sets!")
            print("This action cannot be undone.")
            
            confirm = input("\nType 'DELETE' to confirm: ")
            if confirm != 'DELETE':
                print("Deletion cancelled.")
                return
            
            deleted = 0
            failed = 0
            
            for ts in test_sets:
                key = ts['key']
                summary = ts['fields']['summary']
                
                delete_url = f"{JIRA_BASE_URL}/rest/api/2/issue/{key}"
                del_response = session.delete(delete_url)
                
                if del_response.status_code == 204:
                    print(f"✓ Deleted {key}: {summary}")
                    deleted += 1
                else:
                    print(f"✗ Failed to delete {key}: {del_response.status_code}")
                    failed += 1
                
                # Small delay to avoid overwhelming the server
                time.sleep(0.2)
            
            print(f"\n{'='*60}")
            print(f"Deletion complete:")
            print(f"  Deleted: {deleted}")
            print(f"  Failed: {failed}")
            print(f"{'='*60}")
            
            if deleted > 0:
                print("\n✅ Test Sets have been deleted.")
                print("\nNext steps:")
                print("1. Try refreshing the Testing Board")
                print("2. Clear your browser cache if needed")
                print("3. The board should now load properly")
    else:
        print(f"Error querying JIRA: {response.status_code}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Delete auto-generated Test Sets')
    parser.add_argument('--confirm', action='store_true', help='Actually delete the Test Sets')
    
    args = parser.parse_args()
    
    delete_test_sets(dry_run=not args.confirm)

if __name__ == '__main__':
    main()