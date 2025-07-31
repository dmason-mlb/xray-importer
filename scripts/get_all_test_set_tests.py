#!/usr/bin/env python3
"""
Get all tests in MLBMOB-2651 test set with pagination
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

# GraphQL query to get tests in the test set
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

print("\nGetting tests in MLBMOB-2651...")

while True:
    query = f'''
    query GetTestSetTests {{
      getTestSet(issueId: "1155028") {{
        issueId
        jira(fields: ["key", "summary"])
        tests(start: {start}, limit: {limit}) {{
          total
          results {{
            issueId
            jira(fields: ["key", "summary", "status", "labels"])
          }}
        }}
      }}
    }}
    '''
    
    response = requests.post(graphql_url, json={'query': query}, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        
        if 'data' in data and data['data']['getTestSet']:
            test_set = data['data']['getTestSet']
            
            if start == 0:
                print(f"\nTest Set: {test_set['jira']['key']} - {test_set['jira']['summary']}")
                total_tests = test_set['tests']['total']
                print(f"Total tests in test set: {total_tests}")
            
            # Add tests from this batch
            batch_tests = test_set['tests']['results']
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

# Process and display results
if all_tests:
    print(f"\n\nFound {len(all_tests)} tests in MLBMOB-2651")
    print("-" * 80)
    
    test_keys = []
    test_details = []
    
    for i, test in enumerate(all_tests, 1):
        test_key = test['jira']['key']
        test_summary = test['jira']['summary']
        test_status = test['jira']['status']['name'] if 'status' in test['jira'] else 'Unknown'
        test_labels = test['jira'].get('labels', [])
        
        test_keys.append(test_key)
        test_details.append({
            'key': test_key,
            'summary': test_summary,
            'status': test_status,
            'labels': test_labels
        })
        
        # Print first 20 and last 10 for brevity
        if i <= 20 or i > len(all_tests) - 10:
            print(f"{i:3d}. {test_key}: {test_summary}")
            print(f"      Status: {test_status}")
            if test_labels:
                print(f"      Labels: {', '.join(test_labels)}")
            print()
        elif i == 21:
            print("... (showing first 20 and last 10 tests) ...\n")
    
    # Save complete results
    result_data = {
        'test_set': 'MLBMOB-2651',
        'test_set_summary': test_set['jira']['summary'],
        'total_tests': len(test_keys),
        'test_keys': test_keys,
        'tests': test_details
    }
    
    with open('mlbmob_2651_all_tests.json', 'w') as f:
        json.dump(result_data, f, indent=2)
    
    print(f"\nTotal tests found: {len(test_keys)}")
    print(f"Complete results saved to mlbmob_2651_all_tests.json")
    
    # Save just the test keys for easier comparison
    with open('mlbmob_2651_test_keys.txt', 'w') as f:
        for key in test_keys:
            f.write(f"{key}\n")
    
    print(f"Test keys saved to mlbmob_2651_test_keys.txt")
    
    # Summary statistics
    status_counts = {}
    for test in test_details:
        status = test['status']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print("\nTest Status Summary:")
    for status, count in sorted(status_counts.items()):
        print(f"- {status}: {count}")