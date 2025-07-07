#!/usr/bin/env python3
"""
Fetch remaining tests from Xray project 26420 (tests 1600-1919).
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

def fetch_tests_batch(start: int, token: str, retries: int = 3) -> Dict[str, Any]:
    """Fetch a batch of tests from Xray with retries."""
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
    
    for attempt in range(retries):
        try:
            print(f"  Attempt {attempt + 1}: Sending request for batch starting at {start}...")
            response = requests.post(GRAPHQL_URL, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            if 'data' in result and 'getExpandedTests' in result['data']:
                batch_count = len(result['data']['getExpandedTests']['results'])
                print(f"  Received {batch_count} tests in this batch")
            
            return result
        except Exception as e:
            print(f"  Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                wait_time = (attempt + 1) * 2
                print(f"  Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
            else:
                raise

def main():
    """Main function to fetch remaining tests."""
    print("Fetching remaining tests from project 26420...")
    
    # Get authentication token
    try:
        token = authenticate()
    except Exception as e:
        print(f"Error: {e}")
        return
    
    # Load existing results
    with_steps_file = os.path.join(OUTPUT_DIR, 'tests_with_steps.json')
    without_steps_file = os.path.join(OUTPUT_DIR, 'tests_without_steps.json')
    
    with open(with_steps_file, 'r') as f:
        existing_with_steps = json.load(f)
        tests_with_steps = existing_with_steps['tests']
    
    with open(without_steps_file, 'r') as f:
        existing_without_steps = json.load(f)
        tests_without_steps = existing_without_steps['tests']
    
    print(f"Loaded {len(tests_with_steps)} tests with steps and {len(tests_without_steps)} tests without steps")
    
    # Fetch remaining batches (1300-1919)
    remaining_starts = [1300, 1400, 1500, 1600, 1700, 1800, 1900]
    
    for start in remaining_starts:
        print(f"\nFetching tests {start} to {min(start + BATCH_SIZE, 1919)}...")
        
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
            
            # Delay to avoid rate limiting
            time.sleep(1)
                    
        except Exception as e:
            print(f"Failed to fetch batch at start={start} after all retries: {e}")
            continue
    
    # Save updated results
    print("\nSaving updated results...")
    
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
    print(f"\nFinal Summary:")
    print(f"Total tests: {len(tests_with_steps) + len(tests_without_steps)}")
    print(f"Tests with steps: {len(tests_with_steps)}")
    print(f"Tests without steps: {len(tests_without_steps)}")

if __name__ == "__main__":
    main()