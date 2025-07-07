#!/usr/bin/env python3
"""
Fetch all tests from Xray project 26420 and sort them by whether they have steps.
"""

import json
import requests
import os
import time
from typing import Dict, List, Any

# Configuration
GRAPHQL_URL = "https://xray.cloud.getxray.app/api/v2/graphql"
PROJECT_ID = "26420"
BATCH_SIZE = 100
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# GraphQL query
QUERY = """
query Getexpandedtests($projectId: String, $limit: Int!, $start: Int) {
    getExpandedTests(projectId: $projectId, limit: $limit, start: $start) {
        total
        results {
            issueId
            jira (fields: ["summary", "key", "description"])
            steps {
                data
                action
                result
            }
            preconditions (limit: 100, start: 0) {
                total
                results {
                    issueId
                    projectId
                    definition
                }
            }
        }
    }
}
"""

def authenticate():
    """Authenticate with Xray API and get JWT token."""
    AUTH_ENDPOINT = "https://xray.cloud.getxray.app/api/v2/authenticate"
    
    # Get credentials from environment variables
    client_id = os.environ.get('XRAY_CLIENT')
    client_secret = os.environ.get('XRAY_SECRET')
    
    if not client_id or not client_secret:
        raise ValueError("Missing XRAY_CLIENT or XRAY_SECRET environment variables")
    
    auth_data = {
        "client_id": client_id,
        "client_secret": client_secret
    }
    
    try:
        response = requests.post(AUTH_ENDPOINT, json=auth_data)
        response.raise_for_status()
        token = response.text.strip('"')
        print("✓ Successfully authenticated with Xray API")
        return token
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to authenticate: {e}")

def fetch_tests_batch(start: int, token: str) -> Dict[str, Any]:
    """Fetch a batch of tests from Xray."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    variables = {
        "projectId": PROJECT_ID,
        "limit": BATCH_SIZE,
        "start": start
    }
    
    payload = {
        "query": QUERY,
        "variables": variables
    }
    
    print(f"  Sending request for batch starting at {start}...")
    response = requests.post(GRAPHQL_URL, json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    
    result = response.json()
    if 'data' in result and 'getExpandedTests' in result['data']:
        batch_count = len(result['data']['getExpandedTests']['results'])
        print(f"  Received {batch_count} tests in this batch")
    
    return result

def main():
    """Main function to fetch all tests and sort them."""
    print(f"Starting to fetch tests from project {PROJECT_ID}...")
    
    # Get authentication token
    try:
        token = authenticate()
    except Exception as e:
        print(f"Error: {e}")
        return
    
    # Initialize collections
    tests_with_steps = []
    tests_without_steps = []
    
    # Fetch first batch to get total count
    print("Fetching first batch to determine total count...")
    first_response = fetch_tests_batch(0, token)
    
    if 'errors' in first_response:
        print(f"GraphQL errors: {first_response['errors']}")
        return
    
    total_tests = first_response['data']['getExpandedTests']['total']
    print(f"Total tests to fetch: {total_tests}")
    
    # Process first batch
    results = first_response.get('data', {}).get('getExpandedTests', {}).get('results', [])
    print(f"Processing {len(results)} tests from first batch...")
    
    for test in results:
        if test.get('steps') and len(test['steps']) > 0:
            tests_with_steps.append(test)
        else:
            tests_without_steps.append(test)
    
    # Fetch remaining batches
    for start in range(BATCH_SIZE, total_tests, BATCH_SIZE):
        print(f"Fetching tests {start} to {min(start + BATCH_SIZE, total_tests)}...")
        
        try:
            response = fetch_tests_batch(start, token)
            
            if 'errors' in response:
                print(f"GraphQL errors at batch starting {start}: {response['errors']}")
                continue
            
            # Process batch
            results = response.get('data', {}).get('getExpandedTests', {}).get('results', [])
            print(f"  Processing {len(results)} tests from this batch...")
            
            for test in results:
                if test.get('steps') and len(test['steps']) > 0:
                    tests_with_steps.append(test)
                else:
                    tests_without_steps.append(test)
            
            # Small delay to avoid rate limiting
            time.sleep(5)
                    
        except Exception as e:
            print(f"Error fetching batch at start={start}: {e}")
            continue
    
    # Save results
    with_steps_file = os.path.join(OUTPUT_DIR, 'tests_with_steps.json')
    without_steps_file = os.path.join(OUTPUT_DIR, 'tests_without_steps.json')
    
    print("\nSaving results...")
    
    with open(with_steps_file, 'w') as f:
        json.dump({
            "total": len(tests_with_steps),
            "tests": tests_with_steps
        }, f, indent=2)
    
    with open(without_steps_file, 'w') as f:
        json.dump({
            "total": len(tests_without_steps),
            "tests": tests_without_steps
        }, f, indent=2)
    
    # Print summary
    print(f"\nSummary:")
    print(f"Total tests fetched: {len(tests_with_steps) + len(tests_without_steps)}")
    print(f"Tests with steps: {len(tests_with_steps)}")
    print(f"Tests without steps: {len(tests_without_steps)}")
    print(f"\nResults saved to:")
    print(f"  - {with_steps_file}")
    print(f"  - {without_steps_file}")

if __name__ == "__main__":
    main()