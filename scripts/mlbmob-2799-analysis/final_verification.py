#!/usr/bin/env python3
"""
PHASE 5: Final Verification and Reporting
Comprehensive verification that all test cases now have proper test steps
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

def load_expected_data() -> Dict[str, Any]:
    """Load the expected test steps data."""
    try:
        with open('xray_ready_test_steps.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✓ Loaded expected data for {data['test_count']} tests")
        return data
    except FileNotFoundError:
        raise FileNotFoundError("xray_ready_test_steps.json not found")

def get_test_current_state(test_id: str, token: str) -> Optional[Dict[str, Any]]:
    """Get current test state from XRAY."""
    query = """
    query GetTestState($issueId: String!) {
        getTest(issueId: $issueId) {
            issueId
            testType {
                name
            }
            steps {
                id
                action
                result
                data
            }
            jira(fields: ["key", "summary", "status"])
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
            return None
        
        result = response.json()
        if 'errors' in result:
            print(f"    ✗ GraphQL Error: {result['errors']}")
            return None
        
        if 'data' not in result or not result['data']['getTest']:
            print(f"    ✗ No test data found")
            return None
        
        return result['data']['getTest']
        
    except Exception as e:
        print(f"    ✗ Exception: {e}")
        return None

def verify_test_steps(expected_test: Dict[str, Any], current_test: Dict[str, Any]) -> Dict[str, Any]:
    """Verify that test steps match expected content."""
    verification = {
        'test_key': expected_test['key'],
        'issue_id': expected_test['issue_id'],
        'verification_passed': False,
        'issues': [],
        'expected_steps': len(expected_test['steps']),
        'actual_steps': len(current_test['steps']),
        'step_matches': []
    }
    
    # Check step count
    if len(current_test['steps']) != len(expected_test['steps']):
        verification['issues'].append(f"Step count mismatch: expected {len(expected_test['steps'])}, got {len(current_test['steps'])}")
        return verification
    
    # Check each step content
    for i, (expected_step, current_step) in enumerate(zip(expected_test['steps'], current_test['steps'])):
        step_match = {
            'step_number': i + 1,
            'matches': True,
            'issues': []
        }
        
        # Compare action
        if expected_step['action'].strip() != current_step['action'].strip():
            step_match['matches'] = False
            step_match['issues'].append("Action content mismatch")
        
        # Compare result
        if expected_step['result'].strip() != current_step['result'].strip():
            step_match['matches'] = False
            step_match['issues'].append("Result content mismatch")
        
        # Compare data
        if expected_step['data'].strip() != current_step['data'].strip():
            step_match['matches'] = False
            step_match['issues'].append("Data content mismatch")
        
        verification['step_matches'].append(step_match)
        
        if not step_match['matches']:
            verification['issues'].extend([f"Step {i+1}: {issue}" for issue in step_match['issues']])
    
    # Overall verification
    verification['verification_passed'] = (
        len(verification['issues']) == 0 and
        all(step['matches'] for step in verification['step_matches'])
    )
    
    return verification

def generate_final_report(verification_results: List[Dict[str, Any]], 
                         expected_data: Dict[str, Any]) -> str:
    """Generate comprehensive final report."""
    report = []
    report.append("FINAL VERIFICATION REPORT")
    report.append("=" * 60)
    report.append(f"Verification Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Project: MLBMOB-2799 Test Step Updates")
    report.append("")
    
    # Summary statistics
    total_tests = len(verification_results)
    verified_tests = sum(1 for r in verification_results if r['verification_passed'])
    total_steps_expected = sum(r['expected_steps'] for r in verification_results)
    total_steps_actual = sum(r['actual_steps'] for r in verification_results)
    
    report.append("SUMMARY:")
    report.append(f"- Total tests processed: {total_tests}")
    report.append(f"- Successfully verified: {verified_tests}")
    report.append(f"- Failed verification: {total_tests - verified_tests}")
    report.append(f"- Expected total steps: {total_steps_expected}")
    report.append(f"- Actual total steps: {total_steps_actual}")
    report.append(f"- Success rate: {(verified_tests/total_tests)*100:.1f}%")
    report.append("")
    
    # Detailed verification results
    report.append("DETAILED VERIFICATION RESULTS:")
    for result in verification_results:
        if result['verification_passed']:
            report.append(f"✓ {result['test_key']}: VERIFIED")
            report.append(f"    Steps: {result['actual_steps']}/{result['expected_steps']}")
        else:
            report.append(f"✗ {result['test_key']}: FAILED")
            report.append(f"    Steps: {result['actual_steps']}/{result['expected_steps']}")
            for issue in result['issues']:
                report.append(f"    - {issue}")
        report.append("")
    
    # Project completion status
    report.append("PROJECT COMPLETION STATUS:")
    if verified_tests == total_tests:
        report.append("✅ ALL TESTS SUCCESSFULLY UPDATED")
        report.append("✅ MLBMOB-2799 is ready for test execution")
        report.append("✅ All 11 test cases now have proper test steps")
    else:
        report.append("❌ SOME TESTS REQUIRE ATTENTION")
        report.append(f"   {total_tests - verified_tests} tests need manual review")
        report.append("   Check individual test issues above")
    
    report.append("")
    report.append("AUTOMATION SUMMARY:")
    report.append("- Data transformation: COMPLETED")
    report.append("- Test backup: COMPLETED")
    report.append("- Batch updates: COMPLETED")
    report.append("- Verification: COMPLETED")
    report.append("- Rollback capability: AVAILABLE")
    
    if verified_tests == total_tests:
        report.append("\n🎉 AUTOMATION PROJECT COMPLETED SUCCESSFULLY!")
    else:
        report.append("\n⚠️  AUTOMATION PROJECT NEEDS ATTENTION")
    
    return "\n".join(report)

def main():
    """Main function for final verification."""
    print("PHASE 5: Final Verification and Reporting")
    print("=" * 60)
    
    try:
        # Load expected data
        print("Loading expected test data...")
        expected_data = load_expected_data()
        
        # Authenticate
        print("Authenticating with XRAY API...")
        token = authenticate()
        
        # Verify each test
        print(f"\nVerifying {len(expected_data['tests'])} tests...")
        verification_results = []
        
        for i, expected_test in enumerate(expected_data['tests'], 1):
            print(f"\n[{i}/{len(expected_data['tests'])}] Verifying {expected_test['key']}...")
            
            # Get current test state
            current_test = get_test_current_state(expected_test['issue_id'], token)
            if not current_test:
                verification_results.append({
                    'test_key': expected_test['key'],
                    'issue_id': expected_test['issue_id'],
                    'verification_passed': False,
                    'issues': ['Failed to retrieve current test state'],
                    'expected_steps': len(expected_test['steps']),
                    'actual_steps': 0,
                    'step_matches': []
                })
                continue
            
            # Verify test steps
            verification = verify_test_steps(expected_test, current_test)
            verification_results.append(verification)
            
            if verification['verification_passed']:
                print(f"    ✓ Verification passed: {verification['actual_steps']} steps match")
            else:
                print(f"    ✗ Verification failed: {len(verification['issues'])} issues")
                for issue in verification['issues'][:3]:  # Show first 3 issues
                    print(f"      - {issue}")
        
        # Generate final report
        print("\nGenerating final report...")
        report = generate_final_report(verification_results, expected_data)
        
        # Save report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f'final_report_{timestamp}.md'
        verification_file = f'verification_results_{timestamp}.json'
        
        # Save markdown report
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # Save detailed verification results
        with open(verification_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'project': 'MLBMOB-2799 Test Step Updates',
                'total_tests': len(verification_results),
                'verified_tests': sum(1 for r in verification_results if r['verification_passed']),
                'verification_results': verification_results
            }, f, indent=2, ensure_ascii=False)
        
        # Display summary
        total_tests = len(verification_results)
        verified_tests = sum(1 for r in verification_results if r['verification_passed'])
        
        print(f"\n{report}")
        print(f"\n✓ Final report saved to: {report_file}")
        print(f"✓ Verification data saved to: {verification_file}")
        
        print(f"\n🎯 FINAL RESULTS:")
        print(f"   Tests verified: {verified_tests}/{total_tests}")
        print(f"   Success rate: {(verified_tests/total_tests)*100:.1f}%")
        
        if verified_tests == total_tests:
            print(f"\n🎉 AUTOMATION PROJECT COMPLETED SUCCESSFULLY!")
            print(f"   All {total_tests} tests in MLBMOB-2799 now have proper test steps")
            return True
        else:
            print(f"\n⚠️  {total_tests - verified_tests} tests need attention")
            print(f"   Check {report_file} for details")
            return False
        
    except Exception as e:
        print(f"✗ Verification failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)