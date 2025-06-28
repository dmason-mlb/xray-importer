#!/usr/bin/env python3
"""
Find the correct Test Set issue type for MLBAPP project
"""

import os
import sys
import requests
from requests.auth import HTTPBasicAuth
import getpass
import json

# Configuration
JIRA_BASE_URL = os.environ.get('JIRA_BASE_URL', '')
JIRA_EMAIL = os.environ.get('JIRA_EMAIL', '')
JIRA_TOKEN = os.environ.get('ATLASSIAN_TOKEN', '')
PROJECT_KEY = 'MLBAPP'

def find_test_set_issue_type():
    """Find Test Set issue type in project"""
    
    # Get credentials
    global JIRA_BASE_URL, JIRA_EMAIL, JIRA_TOKEN
    
    # Set default values for non-interactive mode
    if not JIRA_BASE_URL:
        JIRA_BASE_URL = 'https://baseball.atlassian.net'
    
    if not JIRA_EMAIL:
        print("ERROR: Missing JIRA_EMAIL environment variable")
        sys.exit(1)
    
    if not JIRA_TOKEN:
        print("ERROR: Missing ATLASSIAN_TOKEN environment variable")
        sys.exit(1)
    
    session = requests.Session()
    session.auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_TOKEN)
    session.headers.update({
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    })
    
    print(f"\nSearching for Test Set issue type...")
    print("="*60)
    
    # Method 1: Get all issue types
    print("\n1. All available issue types:")
    url = f"{JIRA_BASE_URL}/rest/api/2/issuetype"
    response = session.get(url)
    
    if response.status_code == 200:
        issue_types = response.json()
        for issue_type in issue_types:
            if 'test' in issue_type['name'].lower() or 'xray' in issue_type['name'].lower():
                print(f"   ID: {issue_type['id']}, Name: {issue_type['name']}, Subtask: {issue_type.get('subtask', False)}")
    
    # Method 2: Get project-specific issue types
    print(f"\n2. Issue types available in project {PROJECT_KEY}:")
    url = f"{JIRA_BASE_URL}/rest/api/2/project/{PROJECT_KEY}"
    response = session.get(url)
    
    if response.status_code == 200:
        project_data = response.json()
        issue_types = project_data.get('issueTypes', [])
        
        test_set_found = False
        for issue_type in issue_types:
            if 'test' in issue_type['name'].lower() or 'xray' in issue_type['name'].lower():
                print(f"   ID: {issue_type['id']}, Name: {issue_type['name']}, Subtask: {issue_type.get('subtask', False)}")
                if issue_type['name'] == 'Test Set':
                    test_set_found = True
                    print(f"   ✅ Found Test Set: ID = {issue_type['id']}")
        
        if not test_set_found:
            print("\n   ⚠️  Test Set issue type not found in project")
            print("   Available issue types:")
            for issue_type in issue_types:
                print(f"   - {issue_type['name']} (ID: {issue_type['id']})")
    
    # Method 3: Search for existing Test Sets
    print(f"\n3. Searching for existing Test Sets in {PROJECT_KEY}:")
    jql = f'project = {PROJECT_KEY} AND issuetype = "Test Set"'
    url = f"{JIRA_BASE_URL}/rest/api/2/search"
    params = {
        'jql': jql,
        'maxResults': 1
    }
    
    response = session.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['total'] > 0:
            issue = data['issues'][0]
            issue_type = issue['fields']['issuetype']
            print(f"   Found existing Test Set: {issue['key']}")
            print(f"   Issue Type ID: {issue_type['id']}")
            print(f"   Issue Type Name: {issue_type['name']}")
        else:
            print("   No existing Test Sets found")
    
    # Method 4: Check createmeta for the project
    print(f"\n4. Checking createmeta for project {PROJECT_KEY}:")
    url = f"{JIRA_BASE_URL}/rest/api/2/issue/createmeta"
    params = {
        'projectKeys': PROJECT_KEY,
        'expand': 'projects.issuetypes.fields'
    }
    
    response = session.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        projects = data.get('projects', [])
        
        if projects:
            project = projects[0]
            issue_types = project.get('issuetypes', [])
            
            print(f"   Issue types you can create in {PROJECT_KEY}:")
            for issue_type in issue_types:
                if 'test' in issue_type['name'].lower() or 'xray' in issue_type['name'].lower():
                    print(f"   - {issue_type['name']} (ID: {issue_type['id']})")

if __name__ == '__main__':
    find_test_set_issue_type()