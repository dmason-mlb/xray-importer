#!/usr/bin/env python3
"""
Check and potentially clean up Test Sets
"""

import os
import sys
import requests
from requests.auth import HTTPBasicAuth
import getpass

# Configuration
JIRA_BASE_URL = os.environ.get('JIRA_BASE_URL', 'https://baseball.atlassian.net')
JIRA_EMAIL = os.environ.get('JIRA_EMAIL', '')
JIRA_TOKEN = os.environ.get('ATLASSIAN_TOKEN', '')
PROJECT_KEY = 'MLBAPP'

def check_test_sets():
    """Check recently created Test Sets"""
    
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
    
    print(f"\nChecking Test Sets in project {PROJECT_KEY}...")
    print("="*60)
    
    # Query for Test Sets created today
    jql = f'project = {PROJECT_KEY} AND issuetype = "Test Set" AND created >= -1d ORDER BY created DESC'
    url = f"{JIRA_BASE_URL}/rest/api/2/search"
    
    params = {
        'jql': jql,
        'maxResults': 50,
        'fields': 'summary,created,labels,status'
    }
    
    response = session.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        test_sets = data['issues']
        
        print(f"Found {len(test_sets)} Test Sets created recently")
        print("\nTest Sets created:")
        
        auto_generated = []
        
        for ts in test_sets:
            created = ts['fields']['created']
            summary = ts['fields']['summary']
            labels = ts['fields'].get('labels', [])
            status = ts['fields']['status']['name']
            
            print(f"\n{ts['key']}: {summary}")
            print(f"  Created: {created}")
            print(f"  Status: {status}")
            print(f"  Labels: {', '.join(labels)}")
            
            if 'auto-generated-test-set' in labels:
                auto_generated.append(ts['key'])
        
        if auto_generated:
            print(f"\n\nAuto-generated Test Sets: {len(auto_generated)}")
            print("Keys: " + ", ".join(auto_generated))
            
            print("\n" + "="*60)
            print("OPTIONS TO FIX THE LOADING ISSUE:")
            print("="*60)
            print("\n1. Try clearing your browser cache and cookies for baseball.atlassian.net")
            print("\n2. Try accessing JIRA in an incognito/private browser window")
            print("\n3. Try a different browser")
            print("\n4. If the issue persists, we can delete the Test Sets:")
            print("   Run: python3 delete_test_sets.py")
            print("\n5. Contact your JIRA admin - they may need to:")
            print("   - Restart the XRAY indexing service")
            print("   - Check if there are any errors in the JIRA logs")
            print("   - Temporarily disable/re-enable XRAY")
    else:
        print(f"Error querying JIRA: {response.status_code}")

if __name__ == '__main__':
    check_test_sets()