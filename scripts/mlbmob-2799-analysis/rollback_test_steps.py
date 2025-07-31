#!/usr/bin/env python3
"""
PHASE 3: Rollback Test Steps Script
Uses backup data to restore original test states and remove added steps
"""

import json
import os
import requests
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configuration
GRAPHQL_URL = "https://xray.cloud.getxray.app/api/v2/graphql"
AUTH_ENDPOINT = "https://xray.cloud.getxray.app/api/v2/authenticate"

def authenticate() -> str:
    """Authenticate with Xray API and get JWT token."""
    # Get credentials from environment variables
    client_id = os.environ.get('XRAY_CLIENT_ID') or os.environ.get('XRAY_CLIENT')
    client_secret = os.environ.get('XRAY_CLIENT_SECRET') or os.environ.get('XRAY_SECRET')
    
    if not client_id or not client_secret:
        raise ValueError("Missing XRAY_CLIENT_ID/XRAY_CLIENT or XRAY_CLIENT_SECRET/XRAY_SECRET environment variables")
    
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

def load_backup_data(backup_file: str = None) -> Dict[str, Any]:
    """Load backup data from specified file or find the latest backup."""
    if not backup_file:
        # Find the latest backup file
        backup_files = [f for f in os.listdir('.') if f.startswith('test_backup_') and f.endswith('.json')]
        if not backup_files:
            raise FileNotFoundError("No backup files found")
        backup_file = max(backup_files)
    
    try:
        with open(backup_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✓ Loaded backup data from {backup_file}")
        return data
    except FileNotFoundError:
        raise FileNotFoundError(f"Backup file not found: {backup_file}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in backup file: {e}")

def get_current_test_steps(test_id: str, token: str) -> List[Dict[str, Any]]:
    """Get current test steps from XRAY."""
    query = """
    query GetCurrentSteps($issueId: String!) {
        getTest(issueId: $issueId) {
            steps {
                id
                action
                result
                data
            }
        }
    }
    """
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    variables = {"issueId": test_id}
    
    try:
        response = requests.post(GRAPHQL_URL,
                               json={"query": query, "variables": variables},
                               headers=headers,
                               timeout=30)
        
        if response.status_code != 200:
            print(f"    ✗ HTTP Error {response.status_code}: {response.text[:200]}")
            return []
        
        result = response.json()
        if 'errors' in result:
            print(f"    ✗ GraphQL Error: {result['errors']}")
            return []
        
        if 'data' not in result or not result['data']['getTest']:
            print(f"    ✗ No test data found")
            return []
        
        return result['data']['getTest'].get('steps', [])
        
    except Exception as e:
        print(f"    ✗ Exception: {e}")
        return []

def remove_test_step(test_id: str, step_id: str, token: str) -> bool:
    """Remove a single test step."""
    remove_mutation = """
    mutation RemoveTestStep($issueId: String!, $stepId: String!) {
        removeTestStep(issueId: $issueId, stepId: $stepId) {
            id
        }
    }
    """
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    variables = {
        "issueId": test_id,
        "stepId": step_id
    }
    
    try:
        response = requests.post(GRAPHQL_URL,
                               json={"query": remove_mutation, "variables": variables},
                               headers=headers,
                               timeout=30)
        
        if response.status_code != 200:
            print(f"    ✗ HTTP Error {response.status_code}: {response.text[:200]}")
            return False
        
        result = response.json()
        if 'errors' in result:
            print(f"    ✗ GraphQL Error: {result['errors']}")
            return False
        
        if 'data' not in result or 'removeTestStep' not in result['data']:
            print(f"    ✗ Unexpected response: {result}")
            return False
        
        return True
        
    except Exception as e:
        print(f"    ✗ Exception: {e}")
        return False

def rollback_test_steps(test_id: str, backup_steps: List[Dict[str, Any]], token: str) -> bool:
    """Rollback test to its original state."""
    # Get current steps
    current_steps = get_current_test_steps(test_id, token)
    
    if not current_steps:
        print(f"    ✓ No steps to remove")
        return True
    
    # Remove all current steps
    print(f"    Removing {len(current_steps)} current steps...")
    removed_count = 0
    
    for step in current_steps:
        if remove_test_step(test_id, step['id'], token):
            removed_count += 1
        else:
            print(f"    ✗ Failed to remove step {step['id']}")
    
    if removed_count == len(current_steps):
        print(f"    ✓ Successfully removed {removed_count} steps")
        return True
    else:
        print(f"    ⚠️  Removed {removed_count}/{len(current_steps)} steps")
        return False

def verify_rollback(test_id: str, expected_steps: int, token: str) -> bool:
    """Verify that rollback was successful."""
    current_steps = get_current_test_steps(test_id, token)
    actual_steps = len(current_steps)
    
    if actual_steps == expected_steps:
        print(f"    ✓ Rollback verified: {actual_steps} steps (expected {expected_steps})")
        return True
    else:
        print(f"    ✗ Rollback failed: {actual_steps} steps (expected {expected_steps})")
        return False

def process_single_rollback(test_data: Dict[str, Any], token: str, dry_run: bool = False) -> Dict[str, Any]:
    """Process rollback for a single test case."""
    result = {
        'test_key': test_data['key'],
        'issue_id': test_data['issue_id'],
        'success': False,
        'message': '',
        'steps_removed': 0,
        'backup_available': test_data['backup_successful']
    }
    
    try:
        if not test_data['backup_successful']:
            result['message'] = "No backup available for this test"
            return result
        
        # Get expected final state from backup
        backup_steps = test_data['current_data']['steps']
        expected_steps = len(backup_steps)
        
        if dry_run:
            current_steps = get_current_test_steps(test_data['issue_id'], token)
            result['success'] = True
            result['message'] = f"DRY RUN: Would remove {len(current_steps)} steps, restore to {expected_steps} steps"
            result['steps_removed'] = len(current_steps)
            return result
        
        # Perform rollback
        if rollback_test_steps(test_data['issue_id'], backup_steps, token):
            # Verify rollback
            if verify_rollback(test_data['issue_id'], expected_steps, token):
                result['success'] = True
                result['message'] = f"Successfully rolled back to {expected_steps} steps"
                result['steps_removed'] = len(get_current_test_steps(test_data['issue_id'], token))
            else:
                result['message'] = "Rollback completed but verification failed"
        else:
            result['message'] = "Failed to rollback steps"
        
    except Exception as e:
        result['message'] = f"Exception: {str(e)}"
    
    return result

def main():
    """Main function to rollback test steps."""
    print("PHASE 3: Rollback Test Steps")
    print("=" * 50)
    
    # Parse command line arguments
    dry_run = '--dry-run' in sys.argv
    backup_file = None
    single_test = None
    
    if '--backup' in sys.argv:
        try:
            backup_index = sys.argv.index('--backup') + 1
            backup_file = sys.argv[backup_index]
        except (IndexError, ValueError):
            print("✗ --backup requires a backup file name")
            return False
    
    if '--test' in sys.argv:
        try:
            test_index = sys.argv.index('--test') + 1
            single_test = sys.argv[test_index]
        except (IndexError, ValueError):
            print("✗ --test requires a test key (e.g., --test MLBMOB-1567)")
            return False
    
    if dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
    
    try:
        # Load backup data
        print("Loading backup data...")
        backup_data = load_backup_data(backup_file)
        
        # Filter for single test if requested
        tests_to_process = backup_data['tests']
        if single_test:
            tests_to_process = [t for t in tests_to_process if t['key'] == single_test]
            if not tests_to_process:
                print(f"✗ Test {single_test} not found in backup")
                return False
            print(f"Processing single test: {single_test}")
        
        # Authenticate
        print("Authenticating with XRAY API...")
        token = authenticate()
        
        # Process rollbacks
        print(f"\nProcessing {len(tests_to_process)} tests...")
        results = []
        errors = []
        
        for i, test_data in enumerate(tests_to_process, 1):
            print(f"\n[{i}/{len(tests_to_process)}] Rolling back {test_data['key']}...")
            
            result = process_single_rollback(test_data, token, dry_run)
            results.append(result)
            
            if result['success']:
                print(f"    ✓ {result['message']}")
            else:
                print(f"    ✗ {result['message']}")
                errors.append(f"{result['test_key']}: {result['message']}")
        
        # Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = f'rollback_results_{timestamp}.json'
        log_file = f'rollback_log_{timestamp}.txt'
        
        # Save detailed results
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'dry_run': dry_run,
                'backup_file': backup_file or 'latest',
                'total_tests': len(tests_to_process),
                'successful_rollbacks': sum(1 for r in results if r['success']),
                'results': results
            }, f, indent=2, ensure_ascii=False)
        
        # Generate summary report
        successful = sum(1 for r in results if r['success'])
        total_removed = sum(r['steps_removed'] for r in results)
        
        summary = [
            f"ROLLBACK SUMMARY - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 60,
            f"Mode: {'DRY RUN' if dry_run else 'LIVE ROLLBACK'}",
            f"Backup file: {backup_file or 'latest'}",
            f"Total tests processed: {len(tests_to_process)}",
            f"Successful rollbacks: {successful}",
            f"Failed rollbacks: {len(tests_to_process) - successful}",
            f"Total steps removed: {total_removed}",
            "",
            "RESULTS:",
        ]
        
        for result in results:
            status = "✓" if result['success'] else "✗"
            summary.append(f"{status} {result['test_key']}: {result['message']}")
        
        if errors:
            summary.extend(["", "ERRORS:", ""])
            summary.extend(errors)
        
        # Save and display summary
        summary_text = "\n".join(summary)
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(summary_text)
        
        print(f"\n{summary_text}")
        print(f"\n✓ Results saved to: {results_file}")
        print(f"✓ Log saved to: {log_file}")
        
        return successful == len(tests_to_process)
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)