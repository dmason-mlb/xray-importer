#!/usr/bin/env python3
"""
Check available XRAY issue types in MLBAPP project
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

def check_xray_issue_types():
    """Check XRAY issue types available in project"""
    
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
    
    print(f"\nChecking XRAY issue types in project {PROJECT_KEY}...")
    print("="*60)
    
    # Get project info including issue types
    url = f"{JIRA_BASE_URL}/rest/api/2/project/{PROJECT_KEY}"
    response = session.get(url)
    
    if response.status_code == 200:
        project_data = response.json()
        issue_types = project_data.get('issueTypes', [])
        
        print(f"\nAll issue types in {PROJECT_KEY}:")
        xray_types = []
        
        for issue_type in sorted(issue_types, key=lambda x: x['name']):
            print(f"  - {issue_type['name']} (ID: {issue_type['id']})")
            
            # Check for XRAY-related issue types
            name_lower = issue_type['name'].lower()
            if any(keyword in name_lower for keyword in ['test', 'xray', 'execution', 'plan', 'precondition']):
                xray_types.append(issue_type)
        
        if xray_types:
            print(f"\n\nXRAY-related issue types found:")
            print("="*60)
            for issue_type in xray_types:
                print(f"\nName: {issue_type['name']}")
                print(f"ID: {issue_type['id']}")
                print(f"Description: {issue_type.get('description', 'No description')}")
                print(f"Subtask: {issue_type.get('subtask', False)}")
        
        # Check if we can create Test Sets by searching for existing ones
        print(f"\n\nChecking for existing XRAY entities...")
        print("="*60)
        
        xray_searches = [
            ("Test Set", 'issuetype = "Test Set"'),
            ("Test Plan", 'issuetype = "Test Plan"'),
            ("Test Execution", 'issuetype = "Test Execution"'),
            ("Test", 'issuetype = "Test" OR issuetype = "Xray Test"'),
        ]
        
        search_url = f"{JIRA_BASE_URL}/rest/api/2/search"
        
        for entity_name, jql_part in xray_searches:
            jql = f'project = {PROJECT_KEY} AND {jql_part}'
            params = {
                'jql': jql,
                'maxResults': 1
            }
            
            response = session.get(search_url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data['total'] > 0:
                    issue = data['issues'][0]
                    issue_type = issue['fields']['issuetype']
                    print(f"\n✅ {entity_name} exists in project:")
                    print(f"   Example: {issue['key']}")
                    print(f"   Issue Type ID: {issue_type['id']}")
                    print(f"   Issue Type Name: {issue_type['name']}")
                else:
                    print(f"\n❌ No {entity_name} found in project")
    
    else:
        print(f"Error accessing project: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == '__main__':
    check_xray_issue_types()