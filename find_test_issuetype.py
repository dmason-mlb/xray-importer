#!/usr/bin/env python3
"""
Find the Test issue type ID for MLBAPP project
"""

import requests
from requests.auth import HTTPBasicAuth
import json
import os

JIRA_BASE_URL = os.environ.get('JIRA_BASE_URL')
JIRA_EMAIL = os.environ.get('JIRA_EMAIL')
JIRA_TOKEN = os.environ.get('ATLASSIAN_TOKEN')

session = requests.Session()
session.auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_TOKEN)
session.headers.update({
    'Accept': 'application/json',
    'Content-Type': 'application/json'
})

# Method 1: Try to get project metadata
print("Method 1: Checking project metadata...")
try:
    url = f"{JIRA_BASE_URL}/rest/api/2/project/MLBAPP"
    response = session.get(url)
    if response.status_code == 200:
        project = response.json()
        print(f"Project found: {project.get('name', 'MLBAPP')}")
        if 'issueTypes' in project:
            print("\nIssue types in MLBAPP project:")
            for it in project['issueTypes']:
                print(f"  - {it['name']} (id: {it['id']})")
                if 'Test' in it['name']:
                    print(f"    ^^^ Found Test issue type! ID: {it['id']}")
except Exception as e:
    print(f"Method 1 failed: {e}")

# Method 2: Try create metadata
print("\n\nMethod 2: Checking create metadata...")
try:
    url = f"{JIRA_BASE_URL}/rest/api/2/issue/createmeta"
    params = {
        'projectKeys': 'MLBAPP',
        'expand': 'projects.issuetypes'
    }
    response = session.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        for project in data.get('projects', []):
            if project['key'] == 'MLBAPP':
                print(f"\nIssue types available for creation in MLBAPP:")
                for it in project.get('issuetypes', []):
                    print(f"  - {it['name']} (id: {it['id']})")
                    if 'Test' in it['name']:
                        print(f"    ^^^ Found Test issue type! ID: {it['id']}")
except Exception as e:
    print(f"Method 2 failed: {e}")

# Method 3: Try to get all issue types
print("\n\nMethod 3: Checking all issue types...")
try:
    url = f"{JIRA_BASE_URL}/rest/api/2/issuetype"
    response = session.get(url)
    if response.status_code == 200:
        issue_types = response.json()
        print("\nAll issue types containing 'Test':")
        for it in issue_types:
            if 'Test' in it.get('name', ''):
                print(f"  - {it['name']} (id: {it['id']}, scope: {it.get('scope', {}).get('type', 'GLOBAL')})")
except Exception as e:
    print(f"Method 3 failed: {e}")

# Method 4: Search for existing Test issues in any project
print("\n\nMethod 4: Looking for existing Test issues...")
try:
    jql = 'issuetype = "Test" ORDER BY created DESC'
    url = f"{JIRA_BASE_URL}/rest/api/2/search"
    params = {
        'jql': jql,
        'maxResults': 1,
        'fields': 'issuetype,project'
    }
    response = session.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['total'] > 0:
            issue = data['issues'][0]
            it = issue['fields']['issuetype']
            proj = issue['fields']['project']
            print(f"Found Test issue {issue['key']} in project {proj['key']}")
            print(f"Test issue type ID: {it['id']}")
            print(f"Test issue type name: {it['name']}")
except Exception as e:
    print(f"Method 4 failed: {e}")