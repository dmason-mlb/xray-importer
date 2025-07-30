#!/usr/bin/env python3
"""
Analyze which tests need folder organization.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "xray-api"))

from auth_utils import XrayAPIClient

def main():
    client = XrayAPIClient()
    token = client.get_auth_token()
    
    query = """
    query GetTests($jql: String!, $limit: Int!) {
        getTests(jql: $jql, limit: $limit) {
            total
            results {
                issueId
                jira(fields: ["key", "summary", "labels"])
                folder {
                    path
                }
            }
        }
    }
    """
    
    response = client.execute_graphql_query(query, {"jql": "project = FRAMED", "limit": 100})
    tests = response['getTests']['results']
    
    print(f"Total tests in FRAMED project: {len(tests)}")
    
    # Analyze folder status
    root_tests = []
    organized_tests = []
    
    for test in tests:
        folder_path = test.get('folder', {}).get('path', '') if test.get('folder') else ''
        if not folder_path or folder_path == '/' or folder_path == '':
            root_tests.append(test)
        else:
            organized_tests.append(test)
    
    print(f"\nTests in root folder: {len(root_tests)}")
    print(f"Tests already organized: {len(organized_tests)}")
    
    # Check for test ID labels
    tests_with_ids = []
    tests_without_ids = []
    
    for test in root_tests:
        labels = test['jira'].get('labels', [])
        has_test_id = any(l.startswith('API-') or l.startswith('FUNC-') for l in labels)
        if has_test_id:
            tests_with_ids.append(test)
        else:
            tests_without_ids.append(test)
    
    print(f"\nRoot tests WITH test ID labels: {len(tests_with_ids)}")
    print(f"Root tests WITHOUT test ID labels: {len(tests_without_ids)}")
    
    # Show some examples
    if tests_with_ids:
        print("\nExamples of tests that CAN be organized:")
        for test in tests_with_ids[:5]:
            labels = test['jira'].get('labels', [])
            test_id = next((l for l in labels if l.startswith('API-') or l.startswith('FUNC-')), None)
            print(f"  {test['jira']['key']}: {test['jira']['summary'][:40]}...")
            print(f"    Test ID: {test_id}")
    
    if tests_without_ids:
        print("\nExamples of tests WITHOUT test ID labels (cannot be auto-organized):")
        for test in tests_without_ids[:10]:
            print(f"  {test['jira']['key']}: {test['jira']['summary'][:40]}...")
            print(f"    Labels: {test['jira'].get('labels', [])}")
    
    # Show already organized tests
    if organized_tests:
        print("\nExamples of already organized tests:")
        for test in organized_tests[:5]:
            print(f"  {test['jira']['key']}: {test['jira']['summary'][:40]}...")
            print(f"    Folder: {test['folder']['path']}")

if __name__ == "__main__":
    main()