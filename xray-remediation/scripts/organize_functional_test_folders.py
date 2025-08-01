#!/usr/bin/env python3
"""
Organize functional tests into folders in Xray Test Repository
"""
import json
import sys
from pathlib import Path
from collections import defaultdict

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir / 'xray-api'))
from auth_utils import XrayAPIClient

def organize_test_folders():
    client = XrayAPIClient()
    
    # Load the functional tests data to get folder structure
    tests_path = Path(__file__).parent.parent / "test-data" / "functional_tests_xray.json"
    with open(tests_path, 'r') as f:
        test_data = json.load(f)
    
    # Build folder structure from test data
    folder_structure = defaultdict(list)
    for test in test_data['tests']:
        test_info = test.get('testInfo', {})
        summary = test_info.get('summary', '')
        folder_path = test.get('folder', '/FRAMED')
        folder_structure[folder_path].append(summary)
    
    print(f"\n=== FUNCTIONAL TEST FOLDER STRUCTURE ===")
    print(f"Total folders: {len(folder_structure)}")
    
    for folder, tests in sorted(folder_structure.items()):
        print(f"\n{folder}: {len(tests)} tests")
        for test in tests[:3]:  # Show first 3 tests
            print(f"  - {test}")
        if len(tests) > 3:
            print(f"  ... and {len(tests) - 3} more")
    
    # Now let's check if we need to move any tests
    # First, get all the uploaded tests
    query = """
    query GetFunctionalTests($jql: String!, $limit: Int!) {
        getTests(jql: $jql, limit: $limit) {
            total
            results {
                issueId
                jira(fields: ["key", "summary"])
                folder {
                    path
                }
            }
        }
    }
    """
    
    # Get tests created today with functional label
    variables = {
        "jql": "project = FRAMED AND created >= '2025-08-01' AND labels = functional",
        "limit": 100
    }
    
    try:
        result = client.execute_graphql_query(query, variables)
        
        if result and 'getTests' in result:
            tests = result['getTests']['results']
            
            print(f"\n=== CHECKING TEST FOLDER ASSIGNMENTS ===")
            print(f"Total functional tests found: {len(tests)}")
            
            # Group by current folder
            current_folders = defaultdict(list)
            for test in tests:
                folder_path = test.get('folder', {}).get('path', 'No folder')
                current_folders[folder_path].append({
                    'key': test['jira']['key'],
                    'summary': test['jira']['summary'],
                    'issueId': test['issueId']
                })
            
            print(f"\nCurrent folder distribution:")
            for folder, test_list in sorted(current_folders.items()):
                print(f"\n{folder}: {len(test_list)} tests")
            
            # Check if any tests need to be moved
            tests_to_move = []
            
            for test in tests:
                summary = test['jira']['summary']
                current_folder = test.get('folder', {}).get('path', '')
                
                # Find the intended folder from our test data
                intended_folder = None
                for folder, test_summaries in folder_structure.items():
                    if summary in test_summaries:
                        intended_folder = folder
                        break
                
                if intended_folder and intended_folder != current_folder:
                    tests_to_move.append({
                        'key': test['jira']['key'],
                        'summary': summary,
                        'issueId': test['issueId'],
                        'current_folder': current_folder,
                        'intended_folder': intended_folder
                    })
            
            if tests_to_move:
                print(f"\n=== TESTS NEEDING FOLDER UPDATES ===")
                print(f"Found {len(tests_to_move)} tests that need to be moved")
                
                for test in tests_to_move[:5]:  # Show first 5
                    print(f"\n{test['key']}: {test['summary']}")
                    print(f"  Current: {test['current_folder']}")
                    print(f"  Should be: {test['intended_folder']}")
                
                if len(tests_to_move) > 5:
                    print(f"\n... and {len(tests_to_move) - 5} more")
                
                # Actually move the tests
                move_tests_to_folders(client, tests_to_move)
            else:
                print(f"\n✓ All tests are already in their correct folders!")
                
    except Exception as e:
        print(f"Error: {e}")

def move_tests_to_folders(client, tests_to_move):
    """Move tests to their intended folders"""
    print(f"\n=== MOVING TESTS TO CORRECT FOLDERS ===")
    
    # GraphQL mutation to update test folder
    mutation = """
    mutation UpdateTestFolder($issueId: String!, $folderPath: String!) {
        updateTestFolder(issueId: $issueId, folderPath: $folderPath)
    }
    """
    
    success_count = 0
    error_count = 0
    
    for test in tests_to_move:
        print(f"\nMoving {test['key']} to {test['intended_folder']}...")
        
        variables = {
            "issueId": test['issueId'],
            "folderPath": test['intended_folder']
        }
        
        try:
            result = client.execute_graphql_query(mutation, variables)
            if result:
                print(f"  ✓ Moved successfully")
                success_count += 1
            else:
                print(f"  ✗ Failed to move")
                error_count += 1
        except Exception as e:
            print(f"  ✗ Error: {e}")
            error_count += 1
    
    print(f"\n=== FOLDER ORGANIZATION SUMMARY ===")
    print(f"Successfully moved: {success_count}")
    print(f"Failed: {error_count}")

if __name__ == "__main__":
    organize_test_folders()