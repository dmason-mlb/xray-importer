#!/usr/bin/env python3
"""
Create the 2 missing functional tests in Xray
"""
import json
import sys
import html
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir / 'xray-api'))
from auth_utils import XrayAPIClient, log_operation

def clean_step_text(text):
    """Clean HTML entities and arrow artifacts from step text"""
    # Decode HTML entities
    text = html.unescape(text)
    
    # Replace arrow variants with clean arrow
    text = text.replace('&rarr;', ' → ')
    text = text.replace('&nbsp;', ' ')
    text = text.replace('  ', ' ')  # Multiple spaces to single
    
    return text.strip()

def parse_step_with_result(action_text):
    """Parse step text and extract action and expected result"""
    action_text = clean_step_text(action_text)
    
    # Split by arrow to get action and results
    parts = [p.strip() for p in action_text.split('→')]
    
    if len(parts) > 1:
        # First part is action, rest are expected results
        action = parts[0]
        expected = ' → '.join(parts[1:])
    else:
        # No arrow found, try to infer expected result
        action = action_text
        expected = infer_expected_result(action)
    
    return action, expected

def infer_expected_result(action):
    """Infer expected result based on action context"""
    action_lower = action.lower()
    
    if 'tap' in action_lower or 'click' in action_lower:
        return "Action is performed successfully"
    elif 'wait' in action_lower:
        return "System responds within expected time"
    elif 'verify' in action_lower or 'check' in action_lower:
        return "Verification passes"
    elif 'navigate' in action_lower:
        return "Navigation completes successfully"
    elif 'display' in action_lower or 'show' in action_lower:
        return "Content displays correctly"
    else:
        return "Expected behavior occurs"

def create_missing_tests():
    client = XrayAPIClient()
    
    # Load the functional tests data
    tests_path = Path(__file__).parent.parent / "test-data" / "functional_tests_xray.json"
    with open(tests_path, 'r') as f:
        test_data = json.load(f)
    
    # Find the missing tests
    missing_tests = []
    for test in test_data['tests']:
        if 'jiraKey' not in test:
            missing_tests.append(test)
    
    print(f"=== CREATING MISSING TESTS ===")
    print(f"Found {len(missing_tests)} tests to create")
    
    # GraphQL mutation to create a test
    mutation = """
    mutation CreateTest($testType: UpdateTestTypeInput!, $jira: JSON!, $steps: [CreateStepInput]) {
        createTest(testType: $testType, jira: $jira, steps: $steps) {
            test {
                issueId
                jira(fields: ["key", "summary"])
            }
            warnings
        }
    }
    """
    
    created_tests = []
    
    for test in missing_tests:
        test_info = test.get('testInfo', {})
        summary = test_info.get('summary', 'Unknown Test')
        
        print(f"\nCreating: {summary}")
        
        # Prepare test steps with proper cleaning
        steps = []
        if 'steps' in test_info:
            for step in test_info['steps']:
                action_text = step.get('action', '')
                action, expected = parse_step_with_result(action_text)
                
                steps.append({
                    "action": action,
                    "result": expected,
                    "data": ""
                })
        
        # Update labels to use functional_test instead of functional
        labels = test_info.get('labels', [])
        if 'functional' in labels:
            labels[labels.index('functional')] = 'functional_test'
        
        # Determine priority based on labels
        priority = "Medium"  # Default
        if 'critical' in labels:
            priority = "Critical"
        elif 'high' in labels:
            priority = "High"
        elif 'low' in labels:
            priority = "Low"
        
        # Prepare JIRA fields
        jira_fields = {
            "fields": {
                "project": {
                    "key": "FRAMED"
                },
                "summary": summary,
                "labels": labels,
                "priority": {
                    "name": priority
                }
            }
        }
        
        # Prepare variables
        variables = {
            "testType": {
                "name": "Manual"
            },
            "jira": jira_fields,
            "steps": steps
        }
        
        try:
            result = client.execute_graphql_query(mutation, variables)
            
            if result and 'createTest' in result:
                test_data_result = result['createTest']['test']
                jira_data = test_data_result.get('jira', {})
                test_key = jira_data.get('key', 'Unknown')
                test_issue_id = test_data_result['issueId']
                
                created_tests.append({
                    'summary': summary,
                    'key': test_key,
                    'issueId': test_issue_id
                })
                
                print(f"  ✓ Created test: {test_key}")
                
                # Update the test in JSON with the JIRA key
                test['jiraKey'] = test_key
                
                # Log the operation
                log_operation("create_missing_functional_test", {
                    "summary": summary,
                    "key": test_key,
                    "issueId": test_issue_id,
                    "labels": labels,
                    "priority": priority,
                    "steps_count": len(steps)
                })
                
            else:
                print(f"  ✗ Failed to create test")
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    # Save updated JSON with new JIRA keys
    if created_tests:
        with open(tests_path, 'w') as f:
            json.dump(test_data, f, indent=2)
        
        print(f"\n✓ Updated functional_tests_xray.json with new JIRA keys")
    
    # Save creation results
    results = {
        'timestamp': datetime.now().isoformat(),
        'created_tests': created_tests
    }
    
    output_path = Path(__file__).parent.parent / "logs" / "missing_tests_created.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n=== SUMMARY ===")
    print(f"Successfully created: {len(created_tests)} tests")
    for test in created_tests:
        print(f"  - {test['key']}: {test['summary']}")
    print(f"\nResults saved to: {output_path}")

if __name__ == "__main__":
    create_missing_tests()