#!/usr/bin/env python3
"""
Discover XRAY custom fields available in JIRA
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
PROJECT_KEY = 'MLBAPP'

def discover_all_fields():
    """Get all fields available in JIRA"""
    print("Discovering all available fields...")
    
    session = requests.Session()
    session.auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_TOKEN)
    session.headers.update({
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    })
    
    url = f"{JIRA_BASE_URL}/rest/api/2/field"
    response = session.get(url)
    
    if response.status_code == 200:
        fields = response.json()
        
        # Categorize fields
        xray_fields = []
        test_fields = []
        custom_fields = []
        
        for field in fields:
            field_name = field.get('name', '')
            field_id = field.get('id', '')
            
            # Check for XRAY-related fields
            if 'xray' in field_name.lower():
                xray_fields.append(field)
            elif 'test' in field_name.lower():
                test_fields.append(field)
            elif field_id.startswith('customfield_'):
                custom_fields.append(field)
        
        # Print findings
        print("\n" + "="*60)
        print("XRAY-RELATED FIELDS:")
        print("="*60)
        for field in xray_fields:
            print(f"ID: {field['id']}")
            print(f"Name: {field['name']}")
            print(f"Type: {field.get('schema', {}).get('type', 'unknown')}")
            print("-"*60)
        
        print("\n" + "="*60)
        print("TEST-RELATED FIELDS:")
        print("="*60)
        for field in test_fields:
            print(f"ID: {field['id']}")
            print(f"Name: {field['name']}")
            print(f"Type: {field.get('schema', {}).get('type', 'unknown')}")
            print("-"*60)
        
        # Save all custom fields to file
        with open('all_custom_fields.json', 'w') as f:
            json.dump(custom_fields, f, indent=2)
        print(f"\nSaved all {len(custom_fields)} custom fields to all_custom_fields.json")
        
        # Look for repository path specifically
        print("\n" + "="*60)
        print("SEARCHING FOR REPOSITORY PATH FIELD:")
        print("="*60)
        for field in fields:
            if any(keyword in field['name'].lower() for keyword in ['repository', 'path', 'folder']):
                print(f"Potential match: {field['id']} - {field['name']}")

def check_test_fields():
    """Check fields from an actual test issue"""
    print("\n\nChecking fields from existing test issue...")
    
    session = requests.Session()
    session.auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_TOKEN)
    session.headers.update({
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    })
    
    # Get one test
    jql = f'project = {PROJECT_KEY} AND issuetype = "Xray Test" ORDER BY created DESC'
    url = f"{JIRA_BASE_URL}/rest/api/2/search"
    params = {
        'jql': jql,
        'maxResults': 1,
        'expand': 'names'
    }
    
    response = session.get(url, params=params)
    if response.status_code == 200 and response.json()['total'] > 0:
        test = response.json()['issues'][0]
        test_key = test['key']
        
        print(f"\nFound test: {test_key}")
        print("="*60)
        
        # Get the test with all fields
        url = f"{JIRA_BASE_URL}/rest/api/2/issue/{test_key}"
        response = session.get(url)
        
        if response.status_code == 200:
            issue = response.json()
            fields = issue['fields']
            
            # Look for custom fields with values
            print("\nCUSTOM FIELDS WITH VALUES:")
            print("="*60)
            for field_id, value in fields.items():
                if field_id.startswith('customfield_') and value is not None:
                    # Get field name from names expansion
                    field_name = "Unknown"
                    print(f"Field ID: {field_id}")
                    print(f"Value: {value}")
                    print("-"*60)
        
        # Get editmeta
        url = f"{JIRA_BASE_URL}/rest/api/2/issue/{test_key}/editmeta"
        response = session.get(url)
        
        if response.status_code == 200:
            editmeta = response.json()
            fields = editmeta.get('fields', {})
            
            print("\n\nEDITABLE XRAY/TEST FIELDS:")
            print("="*60)
            for field_id, field_info in fields.items():
                field_name = field_info.get('name', '')
                if any(keyword in field_name.lower() for keyword in ['xray', 'test', 'repository', 'path', 'folder']):
                    print(f"Field ID: {field_id}")
                    print(f"Name: {field_name}")
                    print(f"Required: {field_info.get('required', False)}")
                    print(f"Type: {field_info.get('schema', {}).get('type', 'unknown')}")
                    print("-"*60)

def main():
    # Validate environment
    if not JIRA_EMAIL or not JIRA_TOKEN:
        print("ERROR: Missing JIRA_EMAIL or ATLASSIAN_TOKEN environment variables")
        sys.exit(1)
    
    print(f"Connecting to: {JIRA_BASE_URL}")
    print(f"Project: {PROJECT_KEY}")
    print()
    
    # Discover fields
    discover_all_fields()
    check_test_fields()
    
    print("\n\nNOTE: Look for field IDs that might be Test Repository Path")
    print("Common names: 'Test Repository Path', 'Test Repo Path', 'Folder', etc.")
    print("\nOnce you find the correct field ID, use it with organize_xray_tests.py")

if __name__ == '__main__':
    main()