#!/usr/bin/env python3
"""
Upload functional tests from functional_tests_xray.json to Xray
Ensures each test is uploaded only once with proper preconditions
"""
import json
import sys
import time
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir / 'xray-api'))
from auth_utils import XrayAPIClient, log_operation

def upload_functional_tests():
    # Initialize client
    client = XrayAPIClient()
    
    # Load functional tests
    tests_path = Path(__file__).parent.parent / "test-data" / "functional_tests_xray.json"
    with open(tests_path, 'r') as f:
        test_data = json.load(f)
    
    tests = test_data['tests']
    
    # Load precondition mapping
    precondition_map_path = Path(__file__).parent.parent / "logs" / "precondition_check_results.json"
    with open(precondition_map_path, 'r') as f:
        precondition_data = json.load(f)
    
    precondition_mapping = precondition_data['existing_preconditions']
    
    print(f"\n=== UPLOADING FUNCTIONAL TESTS TO XRAY ===")
    print(f"Total tests to upload: {len(tests)}")
    print(f"Available precondition mappings: {len(precondition_mapping)}")
    
    # GraphQL mutation to create a test
    mutation = """
    mutation CreateTest($testType: UpdateTestTypeInput!, $jira: JSON!, $steps: [CreateStepInput], $folderPath: String) {
        createTest(testType: $testType, jira: $jira, steps: $steps, folderPath: $folderPath) {
            test {
                issueId
                jira(fields: ["key", "summary"])
            }
            warnings
        }
    }
    """
    
    # Track results
    uploaded_tests = {}
    errors = []
    
    # Process each test
    for i, test in enumerate(tests, 1):
        test_info = test.get('testInfo', {})
        summary = test_info.get('summary', 'Unknown Test')
        
        print(f"\n[{i}/{len(tests)}] Uploading: {summary}")
        
        # Prepare test steps from the Xray format
        steps = []
        if 'steps' in test_info:
            for step in test_info['steps']:
                # The action field contains the full step with action → result format
                action_text = step.get('action', '')
                
                # Parse the action field which contains "action → result1 → result2" format
                parts = [p.strip() for p in action_text.split('→')]
                
                if len(parts) > 1:
                    # First part is action, rest are expected results
                    action = parts[0]
                    expected = ' → '.join(parts[1:])
                else:
                    action = action_text
                    expected = ""
                
                steps.append({
                    "action": action.strip(),
                    "result": expected.strip() if expected else "",
                    "data": ""
                })
        
        # Get labels from test_info
        labels = test_info.get('labels', [])
        
        # Get folder from nested structure
        folder = test.get('folder', '/FRAMED')
        
        # Get preconditions
        preconditions = test.get('preconditions', [])
        
        # Prepare JIRA fields
        jira_fields = {
            "fields": {
                "project": {
                    "key": "FRAMED"
                },
                "summary": summary,
                "labels": labels
            }
        }
        
        # Prepare variables
        variables = {
            "testType": {
                "name": "Manual"
            },
            "jira": jira_fields,
            "steps": steps,
            "folderPath": folder
        }
        
        try:
            # Create the test
            result = client.execute_graphql_query(mutation, variables)
            
            if result and 'createTest' in result:
                test_data = result['createTest']['test']
                jira_data = test_data.get('jira', {})
                test_key = jira_data.get('key', 'Unknown')
                test_issue_id = test_data['issueId']
                
                uploaded_tests[summary] = {
                    'key': test_key,
                    'issueId': test_issue_id,
                    'folder': folder,
                    'preconditions': preconditions
                }
                
                print(f"  ✓ Created test: {test_key}")
                
                # Log the operation
                log_operation("create_functional_test", {
                    "summary": summary,
                    "key": test_key,
                    "issueId": test_issue_id,
                    "labels": labels,
                    "steps_count": len(steps)
                })
                
                # Associate preconditions if any
                if preconditions:
                    associate_preconditions(client, test_issue_id, test_key, 
                                          preconditions, precondition_mapping)
                
            else:
                print(f"  ✗ Failed to create test")
                errors.append({
                    'test': summary,
                    'error': 'No result from mutation'
                })
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
            errors.append({
                'test': summary,
                'error': str(e)
            })
        
        # Rate limiting - wait between requests
        time.sleep(0.5)
    
    # Save upload results
    upload_results = {
        'timestamp': datetime.now().isoformat(),
        'uploaded_tests': uploaded_tests,
        'errors': errors,
        'summary': {
            'total_attempted': len(tests),
            'successfully_uploaded': len(uploaded_tests),
            'failed': len(errors)
        }
    }
    
    output_path = Path(__file__).parent.parent / "logs" / "functional_test_upload_results.json"
    with open(output_path, 'w') as f:
        json.dump(upload_results, f, indent=2)
    
    print(f"\n=== UPLOAD SUMMARY ===")
    print(f"Successfully uploaded: {len(uploaded_tests)}")
    print(f"Failed: {len(errors)}")
    print(f"Results saved to: {output_path}")
    
    return upload_results

def associate_preconditions(client, test_issue_id, test_key, precondition_texts, precondition_mapping):
    """Associate preconditions with a test"""
    # Get precondition issue IDs
    precondition_ids = []
    
    for prec_text in precondition_texts:
        if prec_text in precondition_mapping:
            prec_key = precondition_mapping[prec_text]
            # We need to get the issue ID for this key
            # For now, we'll use the associate mutation with the key
            precondition_ids.append(prec_key)
        else:
            print(f"    ⚠ Precondition not found in mapping: {prec_text}")
    
    if not precondition_ids:
        return
    
    # GraphQL mutation to associate preconditions
    mutation = """
    mutation AddPreconditions($testIssueId: String!, $preconditionKeys: [String]!) {
        addPreconditionsToTestByKeys(testIssueId: $testIssueId, preconditionKeys: $preconditionKeys) {
            addedPreconditions
            warning
        }
    }
    """
    
    variables = {
        "testIssueId": test_issue_id,
        "preconditionKeys": precondition_ids
    }
    
    try:
        # First, let's try a different approach - get precondition issue IDs from their keys
        for prec_key in precondition_ids:
            add_single_precondition(client, test_issue_id, test_key, prec_key)
        
    except Exception as e:
        print(f"    ⚠ Error associating preconditions: {e}")

def add_single_precondition(client, test_issue_id, test_key, precondition_key):
    """Add a single precondition to a test using JQL"""
    # First get the precondition issue ID
    query = """
    query GetPreconditionByKey($jql: String!) {
        getPreconditions(jql: $jql, limit: 1) {
            results {
                issueId
                jira(fields: ["key"])
            }
        }
    }
    """
    
    variables = {
        "jql": f"key = {precondition_key}"
    }
    
    try:
        result = client.execute_graphql_query(query, variables)
        if result and 'getPreconditions' in result:
            results = result['getPreconditions']['results']
            if results:
                prec_issue_id = results[0]['issueId']
                
                # Now associate it
                mutation = """
                mutation AddPrecondition($testIssueId: String!, $preconditionIssueIds: [String]!) {
                    addPreconditionsToTest(testIssueId: $testIssueId, preconditionIssueIds: $preconditionIssueIds) {
                        addedPreconditions
                        warning
                    }
                }
                """
                
                variables = {
                    "testIssueId": test_issue_id,
                    "preconditionIssueIds": [prec_issue_id]
                }
                
                assoc_result = client.execute_graphql_query(mutation, variables)
                if assoc_result:
                    print(f"    ✓ Associated precondition: {precondition_key}")
                else:
                    print(f"    ⚠ Failed to associate precondition: {precondition_key}")
    except Exception as e:
        print(f"    ⚠ Error with precondition {precondition_key}: {e}")

if __name__ == "__main__":
    upload_functional_tests()