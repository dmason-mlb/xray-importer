#!/usr/bin/env python3
"""
Get tests in MLBMOB-2651 test set and compare with Confluence doc 4932862074
"""

import os
import requests
import json

# Set XRAY credentials
XRAY_CLIENT = "6F50E2F905F54387AE31CFD9C912BFB0"
XRAY_SECRET = "7182cbb2529baf5cb0f71854f5b0e71692683c92ee6c8e5ce6fbbdde478dfc14"

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

# Get tests in MLBMOB-2651 (issueId: 1155028)
query = '''
query GetTestSetTests {
  getTestSet(issueId: "1155028") {
    issueId
    jira(fields: ["key", "summary"])
    tests(limit: 500) {
      total
      results {
        issueId
        jira(fields: ["key", "summary", "status", "labels"])
      }
    }
  }
}
'''

print("\nGetting tests in MLBMOB-2651...")
response = requests.post(graphql_url, json={'query': query}, headers=headers)

if response.status_code == 200:
    data = response.json()
    
    if 'data' in data and data['data']['getTestSet']:
        test_set = data['data']['getTestSet']
        print(f"\nTest Set: {test_set['jira']['key']} - {test_set['jira']['summary']}")
        print(f"Total tests in test set: {test_set['tests']['total']}")
        
        # Collect test keys
        test_keys_in_set = []
        print("\nTests in MLBMOB-2651:")
        print("-" * 80)
        
        for i, test in enumerate(test_set['tests']['results'], 1):
            test_key = test['jira']['key']
            test_summary = test['jira']['summary']
            test_status = test['jira']['status']['name'] if 'status' in test['jira'] else 'Unknown'
            test_keys_in_set.append(test_key)
            
            print(f"{i:3d}. {test_key}: {test_summary}")
            print(f"      Status: {test_status}")
            if 'labels' in test['jira'] and test['jira']['labels']:
                print(f"      Labels: {', '.join(test['jira']['labels'])}")
            print()
        
        # Save results
        result_data = {
            'test_set': 'MLBMOB-2651',
            'test_set_summary': test_set['jira']['summary'],
            'total_tests': len(test_keys_in_set),
            'test_keys': test_keys_in_set,
            'tests': [
                {
                    'key': test['jira']['key'],
                    'summary': test['jira']['summary'],
                    'status': test['jira']['status']['name'] if 'status' in test['jira'] else 'Unknown',
                    'labels': test['jira'].get('labels', [])
                }
                for test in test_set['tests']['results']
            ]
        }
        
        with open('mlbmob_2651_test_set.json', 'w') as f:
            json.dump(result_data, f, indent=2)
        
        print(f"\nTotal tests found: {len(test_keys_in_set)}")
        print(f"Results saved to mlbmob_2651_test_set.json")
        
        # Print summary
        print("\nSummary:")
        print(f"- Test Set: MLBMOB-2651")
        print(f"- Name: {test_set['jira']['summary']}")
        print(f"- Total Tests: {len(test_keys_in_set)}")
        
    else:
        print("No data found in response")
        print(json.dumps(data, indent=2))
else:
    print(f"Request failed: {response.status_code}")
    print(response.text)