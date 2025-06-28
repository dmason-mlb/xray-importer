#!/usr/bin/env python3
"""
Quick check for migration labels in XRAY tests
"""

import os
import sys
import requests
from requests.auth import HTTPBasicAuth
import getpass

# Configuration
JIRA_BASE_URL = os.environ.get('JIRA_BASE_URL', '')
JIRA_EMAIL = os.environ.get('JIRA_EMAIL', '')
JIRA_TOKEN = os.environ.get('ATLASSIAN_TOKEN', '')
PROJECT_KEY = 'MLBAPP'

# Labels to check
MIGRATION_LABELS = [
    'imported-from-csv',
    'rerun-import', 
    'testrails-migration',
    'IMPORTED-FROM-CSV',
    'RERUN-IMPORT',
    'TESTRAILS-MIGRATION'
]

def check_migration_labels():
    """Check for migration labels"""
    
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
    
    print(f"\nChecking for migration labels in project {PROJECT_KEY}...")
    print("="*60)
    
    url = f"{JIRA_BASE_URL}/rest/api/2/search"
    
    # Check each label
    total_with_migration_labels = 0
    label_counts = {}
    
    for label in MIGRATION_LABELS:
        jql = f'project = {PROJECT_KEY} AND issuetype = "Xray Test" AND labels = "{label}"'
        params = {
            'jql': jql,
            'maxResults': 0
        }
        
        response = session.get(url, params=params)
        if response.status_code == 200:
            count = response.json()['total']
            if count > 0:
                label_counts[label] = count
                total_with_migration_labels += count
                print(f"'{label}': {count} tests")
    
    # Get a sample test to see all its labels
    print("\n" + "="*60)
    print("SAMPLE TEST WITH MIGRATION LABELS:")
    print("="*60)
    
    if label_counts:
        # Get first label with count > 0
        sample_label = list(label_counts.keys())[0]
        jql = f'project = {PROJECT_KEY} AND issuetype = "Xray Test" AND labels = "{sample_label}"'
        params = {
            'jql': jql,
            'maxResults': 1,
            'fields': 'summary,labels'
        }
        
        response = session.get(url, params=params)
        if response.status_code == 200 and response.json()['issues']:
            issue = response.json()['issues'][0]
            print(f"\nTest: {issue['key']} - {issue['fields']['summary']}")
            print(f"All labels: {issue['fields']['labels']}")
    
    print("\n" + "="*60)
    print(f"TOTAL: Found {total_with_migration_labels} test occurrences with migration labels")
    print("(Note: A single test may have multiple migration labels)")
    print("="*60)
    
    # Check unique tests
    all_labels_condition = ' OR '.join([f'labels = "{label}"' for label in MIGRATION_LABELS if label in label_counts])
    if all_labels_condition:
        jql = f'project = {PROJECT_KEY} AND issuetype = "Xray Test" AND ({all_labels_condition})'
        params = {
            'jql': jql,
            'maxResults': 0
        }
        response = session.get(url, params=params)
        if response.status_code == 200:
            unique_count = response.json()['total']
            print(f"\nUnique tests with migration labels: {unique_count}")

if __name__ == '__main__':
    check_migration_labels()