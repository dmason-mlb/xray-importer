#!/usr/bin/env python3
"""
Test updating a single XRAY test with repository path
"""

import os
import sys
import json
import requests
from requests.auth import HTTPBasicAuth

# Configuration
JIRA_BASE_URL = os.environ.get('JIRA_BASE_URL', 'https://your-domain.atlassian.net')
JIRA_EMAIL = os.environ.get('JIRA_EMAIL', '')
JIRA_TOKEN = os.environ.get('ATLASSIAN_TOKEN', '')

def test_single_update(test_key: str, repository_path: str, custom_field_id: str):
    """Test updating a single test's repository path"""
    
    session = requests.Session()
    session.auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_TOKEN)
    session.headers.update({
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    })
    
    # First, get the current test details
    print(f"\n1. Getting current details for {test_key}...")
    url = f"{JIRA_BASE_URL}/rest/api/2/issue/{test_key}"
    response = session.get(url)
    
    if response.status_code == 200:
        issue = response.json()
        print(f"   ✓ Found test: {issue['fields']['summary']}")
        current_value = issue['fields'].get(custom_field_id, '')
        print(f"   Current {custom_field_id} value: '{current_value}'")
    else:
        print(f"   ✗ Failed to get test: {response.status_code}")
        return False
    
    # Try to update the test
    print(f"\n2. Attempting to update {custom_field_id} to: {repository_path}")
    url = f"{JIRA_BASE_URL}/rest/api/2/issue/{test_key}"
    payload = {
        "fields": {
            custom_field_id: repository_path
        }
    }
    
    print(f"   Payload: {json.dumps(payload, indent=2)}")
    
    response = session.put(url, json=payload)
    
    if response.status_code == 204:
        print("   ✓ Update successful (204 No Content)")
    else:
        print(f"   ✗ Update failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    # Verify the update
    print(f"\n3. Verifying the update...")
    response = session.get(f"{JIRA_BASE_URL}/rest/api/2/issue/{test_key}")
    
    if response.status_code == 200:
        issue = response.json()
        new_value = issue['fields'].get(custom_field_id, '')
        print(f"   New {custom_field_id} value: '{new_value}'")
        
        if new_value == repository_path:
            print("   ✓ Update verified successfully!")
            return True
        else:
            print("   ✗ Value doesn't match expected")
            return False
    else:
        print(f"   ✗ Failed to verify: {response.status_code}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 test_single_update.py <TEST_KEY> [repository_path] [custom_field_id]")
        print("Example: python3 test_single_update.py MLBAPP-5177 '/MLBAPP Test Repository/Test Folder' customfield_22975")
        sys.exit(1)
    
    test_key = sys.argv[1]
    repository_path = sys.argv[2] if len(sys.argv) > 2 else "/MLBAPP Test Repository/Test Update"
    custom_field_id = sys.argv[3] if len(sys.argv) > 3 else "customfield_22975"
    
    # Validate environment
    if not JIRA_EMAIL or not JIRA_TOKEN:
        print("ERROR: Missing JIRA_EMAIL or ATLASSIAN_TOKEN environment variables")
        sys.exit(1)
    
    print(f"Testing repository path update for XRAY tests")
    print(f"JIRA URL: {JIRA_BASE_URL}")
    print(f"Test Key: {test_key}")
    print(f"Repository Path: {repository_path}")
    print(f"Custom Field ID: {custom_field_id}")
    
    success = test_single_update(test_key, repository_path, custom_field_id)
    
    if success:
        print("\n✅ SUCCESS: The custom field update method works!")
        print("You can proceed with organizing all tests.")
    else:
        print("\n❌ FAILED: The custom field update didn't work as expected.")
        print("Check the field ID or permissions.")

if __name__ == '__main__':
    main()