#!/usr/bin/env python3
"""
Get tests in MLBMOB-2651 test set using XRAY API
"""

import os
import requests
import json

# Debug authentication
print("Checking XRAY credentials...")
client_id = os.getenv('XRAY_CLIENT_ID')
client_secret = os.getenv('XRAY_CLIENT_SECRET')

if not client_id or not client_secret:
    print("ERROR: XRAY credentials not found in environment")
    exit(1)

print(f"Client ID starts with: {client_id[:10]}...")
print(f"Client Secret length: {len(client_secret)}")

# Get authentication token
auth_url = 'https://xray.cloud.getxray.app/api/v2/authenticate'
auth_data = {
    'client_id': client_id,
    'client_secret': client_secret
}

print("\nAuthenticating with XRAY...")
auth_response = requests.post(auth_url, json=auth_data)
print(f"Auth response status: {auth_response.status_code}")

if auth_response.status_code != 200:
    print(f"Auth response: {auth_response.text}")
    # Try with different auth endpoint
    print("\nTrying alternative auth method...")
    auth_response = requests.post(auth_url, data=json.dumps(auth_data), headers={'Content-Type': 'application/json'})
    print(f"Auth response status: {auth_response.status_code}")
    if auth_response.status_code != 200:
        print(f"Auth response: {auth_response.text}")
        exit(1)

token = auth_response.text.strip('"')
print(f"Token received (first 20 chars): {token[:20]}...")

# Try to get the test set first
print("\nGetting test set details...")
graphql_url = 'https://xray.cloud.getxray.app/api/v2/graphql'
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

# First, let's search for the test set by key
search_query = '''
query SearchTestSet {
  getTestSets(jql: "key = MLBMOB-2651", limit: 1) {
    total
    results {
      issueId
      jira(fields: ["key", "summary", "status"])
    }
  }
}
'''

print("Searching for MLBMOB-2651...")
response = requests.post(graphql_url, json={'query': search_query}, headers=headers)
print(f"Response status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(json.dumps(data, indent=2))
    
    if 'data' in data and data['data']['getTestSets'] and data['data']['getTestSets']['total'] > 0:
        issue_id = data['data']['getTestSets']['results'][0]['issueId']
        print(f"\nFound test set with issueId: {issue_id}")
        
        # Now get the tests in this test set
        test_query = f'''
        query GetTestSetTests {{
          getTestSet(issueId: "{issue_id}") {{
            issueId
            jira(fields: ["key", "summary"])
            tests(limit: 100) {{
              total
              results {{
                issueId
                jira(fields: ["key", "summary", "status"])
              }}
            }}
          }}
        }}
        '''
        
        print("\nGetting tests in the test set...")
        test_response = requests.post(graphql_url, json={'query': test_query}, headers=headers)
        
        if test_response.status_code == 200:
            test_data = test_response.json()
            if 'data' in test_data and test_data['data']['getTestSet']:
                test_set = test_data['data']['getTestSet']
                print(f"\nTest Set: {test_set['jira']['key']} - {test_set['jira']['summary']}")
                print(f"Total tests: {test_set['tests']['total']}")
                
                # Save test keys
                test_keys = []
                print("\nTests in the set:")
                for i, test in enumerate(test_set['tests']['results'], 1):
                    test_key = test['jira']['key']
                    test_keys.append(test_key)
                    print(f"{i}. {test_key}: {test['jira']['summary']}")
                
                # Save to file
                with open('mlbmob_2651_tests.json', 'w') as f:
                    json.dump({
                        'test_set': 'MLBMOB-2651',
                        'total': len(test_keys),
                        'tests': test_keys
                    }, f, indent=2)
                
                print(f"\nSaved {len(test_keys)} test keys to mlbmob_2651_tests.json")
        else:
            print(f"Failed to get tests: {test_response.status_code}")
            print(test_response.text)
else:
    print(f"Search failed: {response.text}")