#!/usr/bin/env python3
"""
Check if MLBMOB-2799 exists and get its issue ID
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

# GraphQL query to search for test executions
graphql_url = 'https://xray.cloud.getxray.app/api/v2/graphql'
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

print("\nSearching for MLBMOB-2799...")

# First try to find the test execution by searching
query = '''
query SearchTestExecutions {
  getTestExecutions(jql: "project = MLBMOB AND issuetype = 'Test Execution' AND key = 'MLBMOB-2799'", limit: 10) {
    total
    results {
      issueId
      jira(fields: ["key", "summary", "status"])
    }
  }
}
'''

response = requests.post(graphql_url, json={'query': query}, headers=headers)

if response.status_code == 200:
    data = response.json()
    
    if 'data' in data and data['data']['getTestExecutions']:
        test_executions = data['data']['getTestExecutions']
        
        if test_executions['total'] > 0:
            test_execution = test_executions['results'][0]
            print(f"Found test execution:")
            print(f"- Key: {test_execution['jira']['key']}")
            print(f"- Summary: {test_execution['jira']['summary']}")
            print(f"- Status: {test_execution['jira']['status']['name']}")
            print(f"- Issue ID: {test_execution['issueId']}")
            
            # Save the issue ID for the next script
            with open('mlbmob_2799_issue_id.txt', 'w') as f:
                f.write(test_execution['issueId'])
            
            print(f"\nIssue ID saved to mlbmob_2799_issue_id.txt")
        else:
            print("No test execution found with key MLBMOB-2799")
    else:
        print("No data found in response")
else:
    print(f"Request failed: {response.status_code}")
    print(response.text)

# Also try a broader search to see what test executions exist
print("\nSearching for recent test executions in MLBMOB...")

query2 = '''
query SearchAllTestExecutions {
  getTestExecutions(jql: "project = MLBMOB AND issuetype = 'Test Execution'", limit: 20) {
    total
    results {
      issueId
      jira(fields: ["key", "summary", "status", "created"])
    }
  }
}
'''

response2 = requests.post(graphql_url, json={'query': query2}, headers=headers)

if response2.status_code == 200:
    data2 = response2.json()
    
    if 'data' in data2 and data2['data']['getTestExecutions']:
        test_executions = data2['data']['getTestExecutions']
        
        print(f"Found {test_executions['total']} test executions in MLBMOB project")
        print("\nRecent test executions:")
        
        for i, te in enumerate(test_executions['results'][:10]):
            print(f"{i+1:2d}. {te['jira']['key']} - {te['jira']['summary']}")
            print(f"     Status: {te['jira']['status']['name']}")
            print(f"     Issue ID: {te['issueId']}")
            print()
            
            # Check if this is the one we're looking for
            if te['jira']['key'] == 'MLBMOB-2799':
                print("*** This is MLBMOB-2799! ***")
                with open('mlbmob_2799_issue_id.txt', 'w') as f:
                    f.write(te['issueId'])
                print("Issue ID saved to mlbmob_2799_issue_id.txt")
    else:
        print("No test executions found")
else:
    print(f"Request failed: {response2.status_code}")
    print(response2.text)