#!/usr/bin/env python3
"""
Test XRAY GraphQL API connection
"""

import requests
import os
import base64
import json

JIRA_EMAIL = os.environ.get('JIRA_EMAIL')
JIRA_TOKEN = os.environ.get('ATLASSIAN_TOKEN')
XRAY_GRAPHQL_URL = 'https://xray.cloud.getxray.app/api/v2/graphql'

# Create basic auth
credentials = f"{JIRA_EMAIL}:{JIRA_TOKEN}"
basic_auth = base64.b64encode(credentials.encode()).decode()

headers = {
    'Authorization': f'Basic {basic_auth}',
    'Content-Type': 'application/json'
}

# Test query to get test info
query = """
query GetTest($issueId: String!) {
    getTest(issueId: $issueId) {
        issueId
        projectId
        testType {
            name
            kind
        }
        steps {
            id
            action
            result
            data
        }
    }
}
"""

variables = {
    'issueId': 'MLBAPP-3771'  # The test you manually added steps to
}

print(f"Testing XRAY GraphQL API...")
print(f"URL: {XRAY_GRAPHQL_URL}")
print(f"Query: Getting test steps for MLBAPP-3771")

response = requests.post(
    XRAY_GRAPHQL_URL,
    json={'query': query, 'variables': variables},
    headers=headers
)

print(f"\nResponse Status: {response.status_code}")
if response.status_code == 200:
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
else:
    print(f"Error: {response.text}")