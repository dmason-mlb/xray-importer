#!/usr/bin/env python3
"""
List all organizational labels and their test counts
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

def list_organizational_labels():
    """List all organizational labels and their usage"""
    
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
    
    print(f"\nFetching organizational labels for project {PROJECT_KEY}...")
    print("="*60)
    
    # Get all tests with organizational labels
    # Note: JQL doesn't support wildcards in labels, so we need to get all tests and filter
    jql = f'project = {PROJECT_KEY} AND issuetype = "Xray Test" AND labels is not EMPTY'
    url = f"{JIRA_BASE_URL}/rest/api/2/search"
    
    all_labels = {}
    start_at = 0
    max_results = 100
    total_tests = 0
    
    while True:
        params = {
            'jql': jql,
            'startAt': start_at,
            'maxResults': max_results,
            'fields': 'labels,summary'
        }
        
        response = session.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            issues = data.get('issues', [])
            total_tests = data.get('total', 0)
            
            # Extract organizational labels
            for issue in issues:
                labels = issue['fields'].get('labels', [])
                for label in labels:
                    if label.startswith('surface-') or label.startswith('feature-'):
                        if label not in all_labels:
                            all_labels[label] = {
                                'count': 0,
                                'sample_tests': []
                            }
                        all_labels[label]['count'] += 1
                        
                        # Keep first 3 examples
                        if len(all_labels[label]['sample_tests']) < 3:
                            all_labels[label]['sample_tests'].append({
                                'key': issue['key'],
                                'summary': issue['fields']['summary'][:60] + '...' if len(issue['fields']['summary']) > 60 else issue['fields']['summary']
                            })
            
            if len(issues) < max_results:
                break
            
            start_at += max_results
        else:
            print(f"Error querying JIRA: {response.status_code}")
            return
    
    print(f"Total tests with organizational labels: {total_tests}")
    print(f"Unique organizational labels: {len(all_labels)}")
    
    # Sort labels
    surface_labels = sorted([(k, v) for k, v in all_labels.items() if k.startswith('surface-')], 
                           key=lambda x: x[1]['count'], reverse=True)
    feature_labels = sorted([(k, v) for k, v in all_labels.items() if k.startswith('feature-')], 
                           key=lambda x: x[1]['count'], reverse=True)
    
    # Display surface labels
    print("\n" + "="*60)
    print("SURFACE LABELS (Primary categorization)")
    print("="*60)
    for label, info in surface_labels:
        print(f"\n{label}: {info['count']} tests")
        print("  Sample tests:")
        for test in info['sample_tests']:
            print(f"    - {test['key']}: {test['summary']}")
    
    # Display feature labels
    print("\n" + "="*60)
    print("FEATURE LABELS (Secondary categorization)")
    print("="*60)
    for label, info in feature_labels:
        print(f"\n{label}: {info['count']} tests")
        if info['count'] > 20:  # Only show samples for larger groups
            print("  Sample tests:")
            for test in info['sample_tests']:
                print(f"    - {test['key']}: {test['summary']}")
    
    # Summary statistics
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Surface labels: {len(surface_labels)}")
    print(f"Feature labels: {len(feature_labels)}")
    print(f"Total unique labels: {len(all_labels)}")
    
    # Coverage check
    surface_total = sum(info['count'] for _, info in surface_labels)
    print(f"\nTests with surface labels: {surface_total}")
    print(f"Average tests per feature: {sum(info['count'] for _, info in feature_labels) / len(feature_labels) if feature_labels else 0:.1f}")

if __name__ == '__main__':
    list_organizational_labels()