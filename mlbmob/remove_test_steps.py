#!/usr/bin/env python3
"""
Remove all test steps from specified tests in Xray.
"""

import json
import requests
import os
import time
import sys
from typing import List

# Configuration
GRAPHQL_URL = "https://xray.cloud.getxray.app/api/v2/graphql"
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

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

def remove_all_steps_from_test(test_id: str, test_key: str, token: str) -> bool:
    """Remove all test steps from a test."""
    remove_all_steps_mutation = """
    mutation RemoveAllSteps($issueId: String!) {
        removeAllTestSteps(issueId: $issueId)
    }
    """
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    variables = {
        "issueId": test_id
    }
    
    try:
        response = requests.post(GRAPHQL_URL,
                               json={"query": remove_all_steps_mutation, "variables": variables},
                               headers=headers,
                               timeout=30)
        
        if response.status_code != 200:
            print(f"    HTTP Error {response.status_code}: {response.text[:200]}")
            return False
            
        result = response.json()
        
        if 'errors' in result:
            print(f"    GraphQL Error: {result['errors']}")
            return False
        
        return True
        
    except Exception as e:
        print(f"    Exception: {e}")
        return False

def main():
    """Main function to remove steps from tests."""
    # List of tests we updated (from the previous script output)
    tests_to_clean = [
        {"key": "MLBMOB-2203", "id": "1145807"},
        {"key": "MLBMOB-2202", "id": "1145806"},
        {"key": "MLBMOB-2179", "id": "1143871"},
        {"key": "MLBMOB-2178", "id": "1143869"},
        {"key": "MLBMOB-2177", "id": "1143867"},
        {"key": "MLBMOB-2176", "id": "1143831"},
        {"key": "MLBMOB-2175", "id": "1143830"},
        {"key": "MLBMOB-2174", "id": "1143828"},
        {"key": "MLBMOB-2173", "id": "1143827"},
        {"key": "MLBMOB-2172", "id": "1143819"},
        {"key": "MLBMOB-2171", "id": "1143817"},
        {"key": "MLBMOB-2170", "id": "1143435"},
        {"key": "MLBMOB-2169", "id": "1139849"},
        {"key": "MLBMOB-2168", "id": "1139847"},
        {"key": "MLBMOB-2167", "id": "1139845"},
        {"key": "MLBMOB-2166", "id": "1139844"},
        {"key": "MLBMOB-2165", "id": "1139842"},
        {"key": "MLBMOB-2109", "id": "1135488"},
        {"key": "MLBMOB-1852", "id": "1134209"},
        {"key": "MLBMOB-1851", "id": "1134206"},
        {"key": "MLBMOB-1850", "id": "1134201"},
        {"key": "MLBMOB-1849", "id": "1134195"},
        {"key": "MLBMOB-1848", "id": "1134194"},
        {"key": "MLBMOB-1246", "id": "1127229"},
        {"key": "MLBMOB-1245", "id": "1127228"}
    ]
    
    print(f"Will remove steps from {len(tests_to_clean)} tests that were incorrectly updated")
    
    # Get authentication token
    try:
        token = authenticate()
    except Exception as e:
        print(f"Error: {e}")
        return
    
    if '--no-confirm' not in sys.argv:
        print("\nTests to clean:")
        for test in tests_to_clean[:10]:
            print(f"  - {test['key']}")
        if len(tests_to_clean) > 10:
            print(f"  ... and {len(tests_to_clean) - 10} more")
            
        response = input("\nProceed with removing steps from these tests? (yes/no): ")
        if response.lower() != 'yes':
            print("Aborted.")
            return
    
    # Remove steps
    successful_removals = 0
    failed_removals = []
    
    for i, test in enumerate(tests_to_clean):
        test_id = test['id']
        test_key = test['key']
        
        print(f"\n[{i+1}/{len(tests_to_clean)}] Removing steps from {test_key}...")
        
        if remove_all_steps_from_test(test_id, test_key, token):
            successful_removals += 1
            print(f"  ✓ Successfully removed steps from {test_key}")
        else:
            failed_removals.append(test_key)
            print(f"  ✗ Failed to remove steps from {test_key}")
        
        # Rate limiting
        time.sleep(0.5)
    
    # Summary
    print(f"\n{'='*50}")
    print(f"Cleanup Summary:")
    print(f"  Successfully cleaned: {successful_removals} tests")
    print(f"  Failed to clean: {len(failed_removals)} tests")
    
    if failed_removals:
        print(f"\nFailed tests: {', '.join(failed_removals)}")

if __name__ == "__main__":
    main()