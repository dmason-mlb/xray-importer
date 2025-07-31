#!/usr/bin/env python3
"""
Get all tests in MLBMOB-2799 test execution with pagination and test step analysis
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get XRAY credentials from environment variables
XRAY_CLIENT = os.getenv('XRAY_CLIENT_ID')
XRAY_SECRET = os.getenv('XRAY_CLIENT_SECRET')

if not XRAY_CLIENT or not XRAY_SECRET:
    raise ValueError("XRAY_CLIENT_ID and XRAY_CLIENT_SECRET must be set in environment variables or .env file")

# Get authentication token
auth_url = 'https://xray.cloud.getxray.app/api/v2/authenticate'
auth_data = {
    'client_id': XRAY_CLIENT,
    'client_secret': XRAY_SECRET
}

print("Authenticating with XRAY...")
auth_response = requests.post(auth_url, json=auth_data)

if auth_response.status_code != 200:
    print(f"Authentication failed: {auth_response.status_code}")
    print(auth_response.text)
    exit(1)

token = auth_response.text.strip('"')
print("Authentication successful!")

# GraphQL query to get tests in the test execution
graphql_url = 'https://xray.cloud.getxray.app/api/v2/graphql'
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

# Get all tests with pagination
all_tests = []
start = 0
limit = 100
total_tests = None

print("\nGetting tests in MLBMOB-2799...")

while True:
    query = f'''
    query GetTestExecutionTests {{
      getTestExecution(issueId: "1158502") {{
        issueId
        jira(fields: ["key", "summary"])
        tests(start: {start}, limit: {limit}) {{
          total
          results {{
            issueId
            testType {{
              name
            }}
            steps {{
              id
              data
              action
              result
            }}
            jira(fields: ["key", "summary", "status", "labels"])
          }}
        }}
      }}
    }}
    '''
    
    response = requests.post(graphql_url, json={'query': query}, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        
        if 'data' in data and data['data']['getTestExecution']:
            test_execution = data['data']['getTestExecution']
            
            if start == 0:
                print(f"\nTest Execution: {test_execution['jira']['key']} - {test_execution['jira']['summary']}")
                total_tests = test_execution['tests']['total']
                print(f"Total tests in test execution: {total_tests}")
            
            # Add tests from this batch
            batch_tests = test_execution['tests']['results']
            all_tests.extend(batch_tests)
            
            print(f"Fetched tests {start + 1} to {start + len(batch_tests)} of {total_tests}")
            
            # Check if we have all tests
            if len(all_tests) >= total_tests:
                break
            
            # Move to next batch
            start += limit
        else:
            print("No data found in response")
            break
    else:
        print(f"Request failed: {response.status_code}")
        print(response.text)
        break

# Process and analyze results
if all_tests:
    print(f"\n\nFound {len(all_tests)} tests in MLBMOB-2799")
    print("-" * 80)
    
    test_keys = []
    test_details = []
    tests_without_steps = []
    tests_with_steps = []
    
    for i, test in enumerate(all_tests, 1):
        test_key = test['jira']['key']
        test_summary = test['jira']['summary']
        test_status = test['jira']['status']['name'] if 'status' in test['jira'] else 'Unknown'
        test_labels = test['jira'].get('labels', [])
        test_type = test['testType']['name'] if 'testType' in test else 'Unknown'
        steps = test.get('steps', [])
        
        test_detail = {
            'key': test_key,
            'summary': test_summary,
            'status': test_status,
            'labels': test_labels,
            'testType': test_type,
            'stepCount': len(steps),
            'steps': steps
        }
        
        test_keys.append(test_key)
        test_details.append(test_detail)
        
        # Categorize by step presence
        if not steps:
            tests_without_steps.append(test_detail)
        else:
            tests_with_steps.append(test_detail)
        
        # Print first 20 and last 10 for brevity
        if i <= 20 or i > len(all_tests) - 10:
            step_info = f"({len(steps)} steps)" if steps else "(NO STEPS)"
            print(f"{i:3d}. {test_key}: {test_summary} {step_info}")
            print(f"      Status: {test_status}, Type: {test_type}")
            if test_labels:
                print(f"      Labels: {', '.join(test_labels)}")
            print()
        elif i == 21:
            print("... (showing first 20 and last 10 tests) ...\n")
    
    # Save complete results
    result_data = {
        'test_execution': 'MLBMOB-2799',
        'test_execution_summary': test_execution['jira']['summary'],
        'total_tests': len(test_keys),
        'tests_with_steps': len(tests_with_steps),
        'tests_without_steps': len(tests_without_steps),
        'test_keys': test_keys,
        'all_tests': test_details
    }
    
    with open('mlbmob_2799_all_tests.json', 'w') as f:
        json.dump(result_data, f, indent=2)
    
    # Save tests without steps
    with open('mlbmob_2799_tests_without_steps.json', 'w') as f:
        json.dump(tests_without_steps, f, indent=2)
    
    # Save tests with steps
    with open('mlbmob_2799_tests_with_steps.json', 'w') as f:
        json.dump(tests_with_steps, f, indent=2)
    
    print(f"\nAnalysis Summary:")
    print(f"- Total tests: {len(test_keys)}")
    print(f"- Tests with steps: {len(tests_with_steps)}")
    print(f"- Tests without steps: {len(tests_without_steps)}")
    print(f"- Percentage without steps: {(len(tests_without_steps) / len(test_keys) * 100):.1f}%")
    
    print(f"\nFiles saved:")
    print(f"- mlbmob_2799_all_tests.json (complete results)")
    print(f"- mlbmob_2799_tests_without_steps.json ({len(tests_without_steps)} tests)")
    print(f"- mlbmob_2799_tests_with_steps.json ({len(tests_with_steps)} tests)")
    
    # Save just the test keys for easier comparison
    with open('mlbmob_2799_test_keys.txt', 'w') as f:
        for key in test_keys:
            f.write(f"{key}\n")
    
    print(f"- mlbmob_2799_test_keys.txt (test keys only)")
    
    # Summary statistics
    status_counts = {}
    type_counts = {}
    for test in test_details:
        status = test['status']
        test_type = test['testType']
        status_counts[status] = status_counts.get(status, 0) + 1
        type_counts[test_type] = type_counts.get(test_type, 0) + 1
    
    print("\nTest Status Summary:")
    for status, count in sorted(status_counts.items()):
        print(f"- {status}: {count}")
    
    print("\nTest Type Summary:")
    for test_type, count in sorted(type_counts.items()):
        print(f"- {test_type}: {count}")
    
    # Show examples of tests without steps
    if tests_without_steps:
        print(f"\nFirst {min(10, len(tests_without_steps))} tests without steps:")
        for i, test in enumerate(tests_without_steps[:10]):
            print(f"  {i+1}. {test['key']} - {test['summary']}")
            print(f"     Type: {test['testType']}, Status: {test['status']}")