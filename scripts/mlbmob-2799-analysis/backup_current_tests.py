#!/usr/bin/env python3
"""
PHASE 1.2: Backup Current Test States
Queries and saves current state of all 11 test cases before modification
"""

import json
import os
import requests
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configuration
GRAPHQL_URL = "https://xray.cloud.getxray.app/api/v2/graphql"
AUTH_ENDPOINT = "https://xray.cloud.getxray.app/api/v2/authenticate"

def authenticate() -> str:
    """Authenticate with Xray API and get JWT token."""
    # Get credentials from environment variables
    client_id = os.environ.get('XRAY_CLIENT_ID') or os.environ.get('XRAY_CLIENT')
    client_secret = os.environ.get('XRAY_CLIENT_SECRET') or os.environ.get('XRAY_SECRET')
    
    if not client_id or not client_secret:
        raise ValueError("Missing XRAY_CLIENT_ID/XRAY_CLIENT or XRAY_CLIENT_SECRET/XRAY_SECRET environment variables")
    
    auth_data = {
        "client_id": client_id,
        "client_secret": client_secret
    }
    
    try:
        response = requests.post(AUTH_ENDPOINT, json=auth_data)
        response.raise_for_status()
        token = response.text.strip('"')
        print("✓ Successfully authenticated with Xray API")
        return token
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to authenticate: {e}")

def get_test_details(issue_id: str, token: str) -> Optional[Dict[str, Any]]:
    """Get complete test details from XRAY."""
    query = """
    query GetTestDetails($issueId: String!) {
        getTest(issueId: $issueId) {
            issueId
            testType {
                name
                kind
            }
            steps {
                id
                data
                action
                result
            }
            jira(fields: ["key", "summary", "description", "status", "labels", "priority", "assignee", "created", "updated"])
        }
    }
    """
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    variables = {"issueId": issue_id}
    
    try:
        response = requests.post(GRAPHQL_URL,
                               json={"query": query, "variables": variables},
                               headers=headers,
                               timeout=30)
        
        if response.status_code != 200:
            print(f"    ✗ HTTP Error {response.status_code}: {response.text[:200]}")
            return None
        
        result = response.json()
        if 'errors' in result:
            print(f"    ✗ GraphQL Error: {result['errors']}")
            return None
        
        if 'data' not in result or not result['data']['getTest']:
            print(f"    ✗ No test data found")
            return None
        
        return result['data']['getTest']
        
    except Exception as e:
        print(f"    ✗ Exception: {e}")
        return None

def load_test_list() -> List[Dict[str, str]]:
    """Load the list of tests to backup from transformed data."""
    try:
        with open('xray_ready_test_steps.json', 'r') as f:
            data = json.load(f)
        
        test_list = []
        for test in data['tests']:
            test_list.append({
                'key': test['key'],
                'issue_id': test['issue_id'],
                'summary': test['summary']
            })
        
        return test_list
        
    except FileNotFoundError:
        print("✗ xray_ready_test_steps.json not found")
        print("  Run transform_confluence_data.py first")
        return []
    except Exception as e:
        print(f"✗ Error loading test list: {e}")
        return []

def generate_backup_report(backup_data: Dict[str, Any]) -> str:
    """Generate a detailed backup report."""
    report = []
    report.append("XRAY TEST BACKUP REPORT")
    report.append("=" * 50)
    report.append(f"Backup Date: {backup_data['backup_info']['timestamp']}")
    report.append(f"Total Tests: {backup_data['backup_info']['total_tests']}")
    report.append(f"Successful Backups: {backup_data['backup_info']['successful_backups']}")
    report.append(f"Failed Backups: {backup_data['backup_info']['failed_backups']}")
    report.append("")
    
    if backup_data['backup_info']['failed_backups'] > 0:
        report.append("FAILED BACKUPS:")
        for failure in backup_data['backup_info']['failures']:
            report.append(f"- {failure}")
        report.append("")
    
    report.append("BACKUP DETAILS:")
    for test in backup_data['tests']:
        if test['backup_successful']:
            report.append(f"✓ {test['key']}: {test['summary']}")
            report.append(f"  Issue ID: {test['issue_id']}")
            report.append(f"  Current Steps: {len(test['current_data']['steps'])}")
            report.append(f"  Current Status: {test['current_data']['jira']['status']['name']}")
        else:
            report.append(f"✗ {test['key']}: BACKUP FAILED")
            report.append(f"  Error: {test['error']}")
        report.append("")
    
    return "\n".join(report)

def main():
    """Main function to backup current test states."""
    print("PHASE 1.2: Backup Current Test States")
    print("=" * 50)
    
    # Load test list
    print("Loading test list...")
    test_list = load_test_list()
    if not test_list:
        return False
    
    print(f"Found {len(test_list)} tests to backup")
    
    # Authenticate
    try:
        token = authenticate()
    except Exception as e:
        print(f"✗ Authentication failed: {e}")
        return False
    
    # Backup each test
    print("\nBacking up current test states...")
    backup_data = {
        'backup_info': {
            'timestamp': datetime.now().isoformat(),
            'total_tests': len(test_list),
            'successful_backups': 0,
            'failed_backups': 0,
            'failures': []
        },
        'tests': []
    }
    
    for i, test_info in enumerate(test_list, 1):
        print(f"[{i}/{len(test_list)}] Backing up {test_info['key']}...")
        
        test_backup = {
            'key': test_info['key'],
            'issue_id': test_info['issue_id'],
            'summary': test_info['summary'],
            'backup_successful': False,
            'current_data': None,
            'error': None
        }
        
        current_data = get_test_details(test_info['issue_id'], token)
        if current_data:
            test_backup['current_data'] = current_data
            test_backup['backup_successful'] = True
            backup_data['backup_info']['successful_backups'] += 1
            print(f"    ✓ Backup successful")
        else:
            test_backup['error'] = "Failed to retrieve test data"
            backup_data['backup_info']['failed_backups'] += 1
            backup_data['backup_info']['failures'].append(f"{test_info['key']}: Failed to retrieve test data")
            print(f"    ✗ Backup failed")
        
        backup_data['tests'].append(test_backup)
    
    # Save backup data
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'test_backup_{timestamp}.json'
    report_file = f'backup_report_{timestamp}.txt'
    
    print(f"\nSaving backup data to {backup_file}...")
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, indent=2, ensure_ascii=False)
    
    # Generate and save report
    print(f"Generating backup report...")
    report = generate_backup_report(backup_data)
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    # Display summary
    print(f"\n✓ Backup completed!")
    print(f"✓ Total tests: {backup_data['backup_info']['total_tests']}")
    print(f"✓ Successful backups: {backup_data['backup_info']['successful_backups']}")
    print(f"✓ Failed backups: {backup_data['backup_info']['failed_backups']}")
    print(f"✓ Backup saved to: {backup_file}")
    print(f"✓ Report saved to: {report_file}")
    
    if backup_data['backup_info']['failed_backups'] > 0:
        print(f"\n⚠️  {backup_data['backup_info']['failed_backups']} backups failed")
        print("   Check backup report for details")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)