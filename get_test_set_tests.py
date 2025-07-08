#!/usr/bin/env python3
"""
Get tests in MLBMOB-2651 test set
"""

import os
import requests
import json

# Get authentication token
auth_url = 'https://xray.cloud.getxray.app/api/v2/authenticate'
auth_data = {
    'client_id': os.getenv('XRAY_CLIENT_ID'),
    'client_secret': os.getenv('XRAY_CLIENT_SECRET')
}

auth_response = requests.post(auth_url, json=auth_data)
if auth_response.status_code != 200:
    print(f'Authentication failed: {auth_response.status_code}')
    exit(1)

token = auth_response.text.strip('"')

# GraphQL query to get tests in the test set
graphql_url = 'https://xray.cloud.getxray.app/api/v2/graphql'
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

query = '''
query GetTestSetTests {
  getTestSet(issueId: "1155028") {
    tests(limit: 100) {
      total
      results {
        issueId
        jira(fields: ["key", "summary"])
      }
    }
  }
}
'''

response = requests.post(graphql_url, json={'query': query}, headers=headers)
if response.status_code == 200:
    data = response.json()
    if 'data' in data and data['data']['getTestSet']:
        test_set = data['data']['getTestSet']
        print(f'Total tests in MLBMOB-2651: {test_set["tests"]["total"]}')
        print('\nTests in the Test Set:')
        
        # Save test keys for comparison
        test_keys = []
        for test in test_set['tests']['results']:
            test_key = test["jira"]["key"]
            test_keys.append(test_key)
            print(f'- {test_key}: {test["jira"]["summary"]}')
        
        # Save to file for further processing
        with open('mlbmob_2651_tests.json', 'w') as f:
            json.dump(test_keys, f, indent=2)
        
        print(f'\nTotal: {len(test_keys)} tests')
    else:
        print('No data found')
        print(json.dumps(data, indent=2))
else:
    print(f'Request failed: {response.status_code}')
    print(response.text)