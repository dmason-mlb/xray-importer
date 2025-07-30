#!/usr/bin/env python3
"""
PHASE 2.1: Update Test Steps Script
Adapted from mlbmob/update_xray_tests.py to add test steps to XRAY test cases
"""

import json
import os
import requests
import sys
import time
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

def load_test_steps_data(file_path: str = 'xray_ready_test_steps.json') -> Dict[str, Any]:
    """Load and validate test steps data."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✓ Loaded {data['test_count']} tests from {file_path}")
        return data
    except FileNotFoundError:
        raise FileNotFoundError(f"Test steps file not found: {file_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in file: {e}")

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
    
    try:
        response = requests.post(GRAPHQL_URL,
                               json={"query": query, "variables": variables},
                               headers=headers,
                               timeout=30)
        
        if response.status_code != 200:
            return False
        
        result = response.json()
        if 'errors' in result:
            return False
        
        steps = result.get('data', {}).get('getTest', {}).get('steps', [])
        return len(steps) > 0
        
    except Exception:
        return False

def add_test_step(test_id: str, step: Dict[str, str], token: str) -> bool:
    """Add a single test step to a test."""
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
    
    variables = {
        "issueId": test_id,
        "action": step.get('action', ''),
        "result": step.get('result', ''),
        "data": step.get('data', '')
    }
    
    try:
        response = requests.post(GRAPHQL_URL,
                               json={"query": add_step_mutation, "variables": variables},
                               headers=headers,
                               timeout=30)
        
        if response.status_code != 200:
            print(f"    ✗ HTTP Error {response.status_code}: {response.text[:200]}")
            return False
        
        result = response.json()
        if 'errors' in result:
            print(f"    ✗ GraphQL Error: {result['errors']}")
            return False
        
        if 'data' not in result or 'addTestStep' not in result['data']:
            print(f"    ✗ Unexpected response: {result}")
            return False
        
        step_id = result['data']['addTestStep']['id']
        print(f"    ✓ Step added successfully (ID: {step_id})")
        return True
        
    except Exception as e:
        print(f"    ✗ Exception: {e}")
        return False

def add_steps_to_test(test_id: str, steps: List[Dict[str, str]], token: str) -> bool:
    """Add multiple steps to a test."""
    success_count = 0
    
    for i, step in enumerate(steps):
        print(f"      Adding step {i+1}/{len(steps)}...")
        
        if add_test_step(test_id, step, token):
            success_count += 1
        else:
            print(f"      ✗ Failed to add step {i+1}")
            # Continue with remaining steps instead of failing completely
        
        # Rate limiting: small delay between steps
        time.sleep(0.5)
    
    print(f"      ✓ Added {success_count}/{len(steps)} steps successfully")
    return success_count == len(steps)

def validate_test_step_format(step: Dict[str, str]) -> List[str]:
    """Validate step structure before API call."""
    issues = []
    
    if not step.get('action'):
        issues.append("Missing action field")
    
    if not step.get('result'):
        issues.append("Missing result field")
    
    # Check field lengths (GraphQL limits)
    if len(step.get('action', '')) > 4000:
        issues.append("Action field too long (max 4000 chars)")
    
    if len(step.get('result', '')) > 4000:
        issues.append("Result field too long (max 4000 chars)")
    
    if len(step.get('data', '')) > 4000:
        issues.append("Data field too long (max 4000 chars)")
    
    return issues

def check_update_success(test_id: str, expected_steps: int, token: str) -> bool:
    """Verify steps were added correctly."""
    query = """
    query VerifySteps($issueId: String!) {
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
            return False
        
        result = response.json()
        if 'errors' in result:
            return False
        
        steps = result.get('data', {}).get('getTest', {}).get('steps', [])
        return len(steps) == expected_steps
        
    except Exception:
        return False

def generate_progress_report(completed: int, total: int, errors: List[str]) -> str:
    """Generate real-time progress report."""
    progress = (completed / total) * 100 if total > 0 else 0
    
    report = [
        f"PROGRESS: {completed}/{total} tests processed ({progress:.1f}%)",
        f"Errors: {len(errors)}"
    ]
    
    if errors:
        report.append("Recent errors:")
        for error in errors[-3:]:  # Show last 3 errors
            report.append(f"  - {error}")
    
    return "\n".join(report)

def process_single_test(test_data: Dict[str, Any], token: str, dry_run: bool = False) -> Dict[str, Any]:
    """Process a single test case."""
    result = {
        'test_key': test_data['key'],
        'issue_id': test_data['issue_id'],
        'success': False,
        'message': '',
        'steps_added': 0,
        'steps_expected': len(test_data['steps'])
    }
    
    try:
        # Check if test already has steps
        if check_test_has_steps(test_data['issue_id'], token):
            result['message'] = "Test already has steps - skipping"
            return result
        
        # Validate step format
        validation_issues = []
        for i, step in enumerate(test_data['steps']):
            issues = validate_test_step_format(step)
            if issues:
                validation_issues.extend([f"Step {i+1}: {issue}" for issue in issues])
        
        if validation_issues:
            result['message'] = f"Validation failed: {'; '.join(validation_issues)}"
            return result
        
        if dry_run:
            result['success'] = True
            result['message'] = f"DRY RUN: Would add {len(test_data['steps'])} steps"
            result['steps_added'] = len(test_data['steps'])
            return result
        
        # Add steps to test
        if add_steps_to_test(test_data['issue_id'], test_data['steps'], token):
            # Verify steps were added
            if check_update_success(test_data['issue_id'], len(test_data['steps']), token):
                result['success'] = True
                result['message'] = f"Successfully added {len(test_data['steps'])} steps"
                result['steps_added'] = len(test_data['steps'])
            else:
                result['message'] = "Steps added but verification failed"
        else:
            result['message'] = "Failed to add steps"
        
    except Exception as e:
        result['message'] = f"Exception: {str(e)}"
    
    return result

def main():
    """Main function to update test steps."""
    print("PHASE 2.1: Update Test Steps")
    print("=" * 50)
    
    # Parse command line arguments
    dry_run = '--dry-run' in sys.argv
    single_test = None
    
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
        # Load test steps data
        print("Loading test steps data...")
        data = load_test_steps_data()
        
        # Filter for single test if requested
        tests_to_process = data['tests']
        if single_test:
            tests_to_process = [t for t in tests_to_process if t['key'] == single_test]
            if not tests_to_process:
                print(f"✗ Test {single_test} not found")
                return False
            print(f"Processing single test: {single_test}")
        
        # Authenticate
        print("Authenticating with XRAY API...")
        token = authenticate()
        
        # Process tests
        print(f"\nProcessing {len(tests_to_process)} tests...")
        results = []
        errors = []
        
        for i, test_data in enumerate(tests_to_process, 1):
            print(f"\n[{i}/{len(tests_to_process)}] Processing {test_data['key']}...")
            
            result = process_single_test(test_data, token, dry_run)
            results.append(result)
            
            if result['success']:
                print(f"    ✓ {result['message']}")
            else:
                print(f"    ✗ {result['message']}")
                errors.append(f"{result['test_key']}: {result['message']}")
            
            # Progress report
            if i % 5 == 0 or i == len(tests_to_process):
                print(f"\n{generate_progress_report(i, len(tests_to_process), errors)}")
        
        # Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = f'update_results_{timestamp}.json'
        log_file = f'update_log_{timestamp}.txt'
        
        # Save detailed results
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'dry_run': dry_run,
                'total_tests': len(tests_to_process),
                'successful_updates': sum(1 for r in results if r['success']),
                'results': results
            }, f, indent=2, ensure_ascii=False)
        
        # Generate summary report
        successful = sum(1 for r in results if r['success'])
        total_steps = sum(r['steps_added'] for r in results)
        
        summary = [
            f"UPDATE SUMMARY - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 60,
            f"Mode: {'DRY RUN' if dry_run else 'LIVE UPDATE'}",
            f"Total tests processed: {len(tests_to_process)}",
            f"Successful updates: {successful}",
            f"Failed updates: {len(tests_to_process) - successful}",
            f"Total steps added: {total_steps}",
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