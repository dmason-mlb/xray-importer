#!/usr/bin/env python3
"""
Check which fields are editable on an XRAY test issue
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

def check_editable_fields(test_key: str):
    """Check editable fields for a test issue"""
    
    session = requests.Session()
    session.auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_TOKEN)
    session.headers.update({
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    })
    
    print(f"Checking editable fields for {test_key}...")
    
    # Get editmeta
    url = f"{JIRA_BASE_URL}/rest/api/2/issue/{test_key}/editmeta"
    response = session.get(url)
    
    if response.status_code == 200:
        editmeta = response.json()
        fields = editmeta.get('fields', {})
        
        print(f"\nFound {len(fields)} editable fields")
        
        # Look for repository/path/folder related fields
        print("\n" + "="*60)
        print("POTENTIAL REPOSITORY/PATH FIELDS:")
        print("="*60)
        
        found_repo_fields = False
        for field_id, field_info in fields.items():
            field_name = field_info.get('name', '')
            if any(keyword in field_name.lower() for keyword in ['repo', 'path', 'folder', 'test', 'xray']):
                print(f"\nField ID: {field_id}")
                print(f"Name: {field_name}")
                print(f"Type: {field_info.get('schema', {}).get('type', 'unknown')}")
                print(f"Required: {field_info.get('required', False)}")
                if 'allowedValues' in field_info:
                    print(f"Has allowed values: Yes ({len(field_info['allowedValues'])} options)")
                found_repo_fields = True
        
        if not found_repo_fields:
            print("No repository/path related fields found in editable fields")
        
        # Save all fields for analysis
        with open('editable_fields.json', 'w') as f:
            json.dump(fields, f, indent=2)
        print(f"\n\nSaved all editable fields to editable_fields.json")
        
        # List all custom fields
        print("\n" + "="*60)
        print("ALL CUSTOM FIELDS (first 20):")
        print("="*60)
        count = 0
        for field_id, field_info in fields.items():
            if field_id.startswith('customfield_'):
                print(f"{field_id} - {field_info.get('name', 'Unknown')}")
                count += 1
                if count >= 20:
                    break
        
    else:
        print(f"Failed to get editmeta: {response.status_code}")
        print(f"Response: {response.text}")

def main():
    test_key = sys.argv[1] if len(sys.argv) > 1 else "MLBAPP-5177"
    
    # Validate environment
    if not JIRA_EMAIL or not JIRA_TOKEN:
        print("ERROR: Missing JIRA_EMAIL or ATLASSIAN_TOKEN environment variables")
        sys.exit(1)
    
    print(f"JIRA URL: {JIRA_BASE_URL}")
    print(f"Test Key: {test_key}")
    print()
    
    check_editable_fields(test_key)

if __name__ == '__main__':
    main()