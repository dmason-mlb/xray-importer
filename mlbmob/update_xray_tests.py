#!/usr/bin/env python3
"""
Update Xray tests with proposed changes (preconditions and/or steps).
"""

import json
import requests
import os
import time
import sys
from typing import Dict, List, Any

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

def create_precondition(definition: str, token: str) -> str:
    """Create a precondition and return its ID."""
    create_mutation = """
    mutation CreatePrecondition($definition: String!, $summary: String!, $projectKey: String!) {
        createPrecondition(
            preconditionType: { name: "Manual" }
            definition: $definition
            jira: {
                fields: { 
                    summary: $summary, 
                    project: { key: $projectKey } 
                }
            }
        ) {
            precondition {
                issueId
            }
            warnings
        }
    }
    """
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Create a summary from the first line of the definition
    summary = definition.split('\n')[0][:100]  # Max 100 chars for summary
    
    variables = {
        "definition": definition,
        "summary": summary,
        "projectKey": "MLBMOB"
    }
    
    response = requests.post(GRAPHQL_URL,
                           json={"query": create_mutation, "variables": variables},
                           headers=headers,
                           timeout=30)
    
    if response.status_code != 200:
        raise Exception(f"HTTP Error {response.status_code}: {response.text[:200]}")
    
    result = response.json()
    if 'errors' in result:
        raise Exception(f"GraphQL Error: {result['errors']}")
    
    if 'data' not in result or 'createPrecondition' not in result['data']:
        raise Exception(f"Unexpected response structure: {result}")
    
    if 'warnings' in result['data']['createPrecondition'] and result['data']['createPrecondition']['warnings']:
        print(f"      Warning: {result['data']['createPrecondition']['warnings']}")
    
    return result['data']['createPrecondition']['precondition']['issueId']

def add_preconditions_to_test(test_id: str, precondition_ids: List[str], token: str):
    """Add preconditions to a test."""
    add_mutation = """
    mutation AddPreconditions($testId: String!, $preconditionIds: [String!]!) {
        addPreconditionsToTest(issueId: $testId, preconditionIssueIds: $preconditionIds) {
            addedPreconditions
            warning
        }
    }
    """
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    variables = {
        "testId": test_id,
        "preconditionIds": precondition_ids
    }
    
    response = requests.post(GRAPHQL_URL,
                           json={"query": add_mutation, "variables": variables},
                           headers=headers,
                           timeout=30)
    
    if response.status_code != 200:
        raise Exception(f"HTTP Error {response.status_code}: {response.text[:200]}")
    
    result = response.json()
    if 'errors' in result:
        raise Exception(f"GraphQL Error: {result['errors']}")
    
    if 'data' not in result or 'addPreconditionsToTest' not in result['data']:
        raise Exception(f"Unexpected response structure: {result}")
    
    if 'warning' in result['data']['addPreconditionsToTest'] and result['data']['addPreconditionsToTest']['warning']:
        print(f"      Warning: {result['data']['addPreconditionsToTest']['warning']}")
    
    added_count = result['data']['addPreconditionsToTest'].get('addedPreconditions', 0)
    if added_count == 0:
        raise Exception("No preconditions were added - they may already exist on the test")

def check_test_has_steps(test_id: str, token: str) -> bool:
    """Check if a test already has steps."""
    query = """
    query CheckSteps($issueId: String!) {
        getTest(issueId: $issueId) {
            steps {
                id
            }
        }
    }
    """
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    variables = {"issueId": test_id}
    
    response = requests.post(GRAPHQL_URL,
                           json={"query": query, "variables": variables},
                           headers=headers)
    
    if response.status_code != 200:
        return False
    
    result = response.json()
    if 'errors' in result:
        return False
    
    steps = result.get('data', {}).get('getTest', {}).get('steps', [])
    return len(steps) > 0

def add_steps_to_test(test_id: str, steps: List[Dict[str, str]], token: str):
    """Add steps to a test."""
    add_step_mutation = """
    mutation AddTestStep($issueId: String!, $action: String, $result: String, $data: String) {
        addTestStep(
            issueId: $issueId, 
            step: {
                action: $action,
                result: $result,
                data: $data
            }
        ) {
            id
        }
    }
    """
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    for i, step in enumerate(steps):
        print(f"      Adding step {i+1}/{len(steps)}...")
        
        variables = {
            "issueId": test_id,
            "action": step.get('action', ''),
            "result": step.get('result', ''),
            "data": step.get('data', '')
        }
        
        response = requests.post(GRAPHQL_URL,
                               json={"query": add_step_mutation, "variables": variables},
                               headers=headers,
                               timeout=30)
        
        if response.status_code != 200:
            raise Exception(f"HTTP Error {response.status_code}: {response.text[:200]}")
            
        result = response.json()
        if 'errors' in result:
            raise Exception(f"GraphQL Error: {result['errors']}")

def main():
    """Main function to update tests in Xray."""
    # Check for flags
    dry_run = '--dry-run' in sys.argv
    limit = None
    for i, arg in enumerate(sys.argv):
        if arg == '--limit' and i + 1 < len(sys.argv):
            try:
                limit = int(sys.argv[i + 1])
            except ValueError:
                print(f"Invalid limit value: {sys.argv[i + 1]}")
                return
    
    # Load proposed changes
    input_file = os.path.join(OUTPUT_DIR, 'proposed_xray_updates.json')
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found")
        print("Run create_proposed_changes.py first")
        return
    
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    updates = data['updates']
    if limit:
        updates = updates[:limit]
    
    print(f"Loaded {len(updates)} test updates")
    print(f"  - {len([u for u in updates if u['update_type'] == 'steps_and_preconditions'])} with steps and preconditions")
    print(f"  - {len([u for u in updates if u['update_type'] == 'preconditions_only'])} with preconditions only")
    
    if dry_run:
        print("\n*** DRY RUN MODE ***")
        print("\nSample updates:")
        for update in updates[:5]:
            print(f"\n{update['key']} ({update['update_type']}):")
            if update['preconditions']:
                print(f"  Preconditions: {update['preconditions'][0]['definition'][:80]}...")
            if update['steps']:
                print(f"  Steps: {len(update['steps'])}")
                print(f"    Action: {update['steps'][0]['action'][:60]}...")
                if update['steps'][0].get('result'):
                    print(f"    Result: {update['steps'][0]['result'][:60]}...")
        return
    
    # Get authentication token
    try:
        token = authenticate()
    except Exception as e:
        print(f"Error: {e}")
        return
    
    # Confirm before proceeding
    if '--no-confirm' not in sys.argv:
        response = input(f"\nProceed with updating {len(updates)} tests? (yes/no): ")
        if response.lower() != 'yes':
            print("Aborted.")
            return
    
    # Update tests
    successful = 0
    failed = []
    
    for i, update in enumerate(updates):
        test_id = update['issueId']
        test_key = update['key']
        
        print(f"\n[{i+1}/{len(updates)}] Updating {test_key}...")
        
        try:
            # Add preconditions if any
            if update['preconditions']:
                print(f"    Creating and adding {len(update['preconditions'])} precondition(s)...")
                precondition_ids = []
                for precond in update['preconditions']:
                    precond_id = create_precondition(precond['definition'], token)
                    precondition_ids.append(precond_id)
                
                add_preconditions_to_test(test_id, precondition_ids, token)
                print(f"    ✓ Added preconditions")
            
            # Add steps if any
            if update['steps']:
                # Check if test already has steps
                if check_test_has_steps(test_id, token):
                    print(f"    ⚠️  Test already has steps, skipping step addition")
                else:
                    add_steps_to_test(test_id, update['steps'], token)
                    print(f"    ✓ Added {len(update['steps'])} step(s)")
            
            successful += 1
            
        except Exception as e:
            print(f"    ✗ Error: {e}")
            failed.append(test_key)
        
        # Rate limiting
        time.sleep(0.5)
    
    # Summary
    print(f"\n{'='*50}")
    print(f"Update Summary:")
    print(f"  Successfully updated: {successful} tests")
    print(f"  Failed to update: {len(failed)} tests")
    
    if failed:
        print(f"\nFailed tests: {', '.join(failed[:10])}")
        if len(failed) > 10:
            print(f"  ... and {len(failed) - 10} more")

if __name__ == "__main__":
    main()