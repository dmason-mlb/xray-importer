#!/usr/bin/env python3
"""
Check the current status of XRAY test labeling
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

def check_labeling_status():
    """Check current labeling status of XRAY tests"""
    
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
    
    print(f"\nChecking labeling status for project {PROJECT_KEY}...")
    print("="*60)
    
    # Query 1: Total imported tests
    jql1 = f'project = {PROJECT_KEY} AND issuetype = "Xray Test" AND labels = "imported-from-csv"'
    url = f"{JIRA_BASE_URL}/rest/api/2/search"
    params = {
        'jql': jql1,
        'maxResults': 0  # Just get count
    }
    
    response = session.get(url, params=params)
    if response.status_code == 200:
        total_imported = response.json()['total']
        print(f"Total imported tests: {total_imported}")
    else:
        print(f"Error querying JIRA: {response.status_code}")
        return
    
    # Query 2: Tests with surface labels
    jql2 = f'project = {PROJECT_KEY} AND issuetype = "Xray Test" AND labels = "imported-from-csv" AND (labels = "surface-home" OR labels = "surface-news" OR labels = "surface-core")'
    params['jql'] = jql2
    
    response = session.get(url, params=params)
    if response.status_code == 200:
        labeled_count = response.json()['total']
        print(f"Tests with organizational labels: {labeled_count}")
        print(f"Tests remaining to label: {total_imported - labeled_count}")
        print(f"Progress: {labeled_count}/{total_imported} ({labeled_count/total_imported*100:.1f}%)")
    
    # Query 3: Distribution by surface
    print("\n" + "="*60)
    print("SURFACE LABEL DISTRIBUTION:")
    print("="*60)
    
    for surface in ['surface-home', 'surface-news', 'surface-core']:
        jql = f'project = {PROJECT_KEY} AND issuetype = "Xray Test" AND labels = "{surface}"'
        params['jql'] = jql
        response = session.get(url, params=params)
        if response.status_code == 200:
            count = response.json()['total']
            print(f"{surface}: {count} tests")
    
    # Query 4: Top feature labels
    print("\n" + "="*60)
    print("TOP FEATURE LABELS:")
    print("="*60)
    
    feature_labels = [
        'feature-analytics', 'feature-video', 'feature-authentication',
        'feature-mixed-feed', 'feature-headline-stack', 'feature-team-snapshot',
        'feature-standings', 'feature-player', 'feature-stories',
        'feature-advertising', 'feature-configuration', 'feature-accessibility'
    ]
    
    label_counts = []
    for label in feature_labels:
        jql = f'project = {PROJECT_KEY} AND issuetype = "Xray Test" AND labels = "{label}"'
        params['jql'] = jql
        response = session.get(url, params=params)
        if response.status_code == 200:
            count = response.json()['total']
            if count > 0:
                label_counts.append((label, count))
    
    # Sort by count and display
    label_counts.sort(key=lambda x: x[1], reverse=True)
    for label, count in label_counts[:10]:
        print(f"{label}: {count} tests")
    
    print("\n" + "="*60)
    
    # Show sample of unlabeled tests
    print("\nSample of tests that still need labeling:")
    jql_unlabeled = f'project = {PROJECT_KEY} AND issuetype = "Xray Test" AND labels = "imported-from-csv" AND labels NOT IN ("surface-home", "surface-news", "surface-core")'
    params = {
        'jql': jql_unlabeled,
        'maxResults': 5,
        'fields': 'summary'
    }
    
    response = session.get(url, params=params)
    if response.status_code == 200:
        issues = response.json()['issues']
        for issue in issues:
            print(f"- {issue['key']}: {issue['fields']['summary']}")
    
    print("\n✅ Status check complete!")

if __name__ == '__main__':
    check_labeling_status()