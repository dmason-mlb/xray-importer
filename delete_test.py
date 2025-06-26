#!/usr/bin/env python3
"""
Delete a specific XRAY test issue from JIRA
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

def delete_test_issue(issue_key: str):
    """Delete a specific test issue"""
    
    # Get credentials
    global JIRA_BASE_URL, JIRA_EMAIL, JIRA_TOKEN
    
    if not JIRA_BASE_URL:
        JIRA_BASE_URL = input("Enter JIRA Base URL (e.g., https://baseball.atlassian.net): ").strip()
    
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
    
    print(f"\nAttempting to delete test issue: {issue_key}")
    print("="*60)
    
    # First, get the issue details to confirm it exists
    print(f"1. Verifying issue {issue_key} exists...")
    url = f"{JIRA_BASE_URL}/rest/api/2/issue/{issue_key}"
    response = session.get(url)
    
    if response.status_code == 404:
        print(f"❌ Issue {issue_key} not found!")
        return False
    elif response.status_code != 200:
        print(f"❌ Error fetching issue: {response.status_code}")
        print(f"Response: {response.text}")
        return False
    
    issue = response.json()
    issue_type = issue['fields']['issuetype']['name']
    summary = issue['fields']['summary']
    
    print(f"✓ Found issue: {issue_key}")
    print(f"  Type: {issue_type}")
    print(f"  Summary: {summary}")
    
    # Confirm deletion
    print("\n" + "="*60)
    print("⚠️  WARNING: This action cannot be undone!")
    print("="*60)
    confirm = input(f"\nAre you sure you want to delete {issue_key}? Type 'YES' to confirm: ")
    
    if confirm != 'YES':
        print("Deletion cancelled.")
        return False
    
    # Delete the issue
    print(f"\n2. Deleting issue {issue_key}...")
    delete_url = f"{JIRA_BASE_URL}/rest/api/2/issue/{issue_key}"
    
    # Add deleteSubtasks parameter to handle any subtasks
    params = {
        'deleteSubtasks': 'true'
    }
    
    response = session.delete(delete_url, params=params)
    
    if response.status_code == 204:
        print(f"✅ Successfully deleted {issue_key}!")
        return True
    elif response.status_code == 403:
        print(f"❌ Permission denied - you don't have permission to delete this issue")
        print("You may need 'Delete Issues' permission in the project")
    elif response.status_code == 404:
        print(f"❌ Issue {issue_key} not found (may have been already deleted)")
    else:
        print(f"❌ Failed to delete: {response.status_code}")
        print(f"Response: {response.text}")
    
    return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 delete_test.py <ISSUE_KEY>")
        print("Example: python3 delete_test.py MLBAPP-4830")
        sys.exit(1)
    
    issue_key = sys.argv[1].upper()
    
    print(f"JIRA Issue Deletion Tool")
    print(f"Target issue: {issue_key}")
    
    success = delete_test_issue(issue_key)
    
    if success:
        print(f"\n✅ Issue {issue_key} has been permanently deleted.")
    else:
        print(f"\n❌ Failed to delete issue {issue_key}")

if __name__ == '__main__':
    main()