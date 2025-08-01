#!/usr/bin/env python3
"""
Find missing functional tests by comparing JSON with Xray
"""
import json
import sys
from pathlib import Path
from collections import defaultdict

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir / 'xray-api'))
from auth_utils import XrayAPIClient

def find_missing_tests():
    client = XrayAPIClient()
    
    # Load the functional tests data
    tests_path = Path(__file__).parent.parent / "test-data" / "functional_tests_xray.json"
    with open(tests_path, 'r') as f:
        test_data = json.load(f)
    
    json_tests = test_data['tests']
    print(f"=== FUNCTIONAL TESTS ANALYSIS ===")
    print(f"Tests in JSON file: {len(json_tests)}")
    
    # Get all functional tests from Xray
    query = """
    query GetFunctionalTests($jql: String!, $limit: Int!) {
        getTests(jql: $jql, limit: $limit) {
            total
            results {
                issueId
                jira(fields: ["key", "summary", "labels", "priority"])
                testType {
                    name
                }
                steps {
                    action
                    result
                    data
                }
            }
        }
    }
    """
    
    # Query for functional tests in Team Page folder
    variables = {
        "jql": "project = FRAMED AND labels = functional ORDER BY key ASC",
        "limit": 100
    }
    
    try:
        result = client.execute_graphql_query(query, variables)
        
        if result and 'getTests' in result:
            xray_tests = result['getTests']['results']
            total = result['getTests']['total']
            
            print(f"\nTests in Xray with 'functional' label: {total}")
            
            # Create mapping of summaries to tests
            xray_by_summary = {}
            for test in xray_tests:
                summary = test['jira'].get('summary', '')
                xray_by_summary[summary] = test
            
            # Find missing tests
            missing_tests = []
            matched_tests = []
            
            for json_test in json_tests:
                test_info = json_test.get('testInfo', {})
                summary = test_info.get('summary', '')
                
                if summary in xray_by_summary:
                    matched_tests.append({
                        'json_test': json_test,
                        'xray_test': xray_by_summary[summary]
                    })
                else:
                    missing_tests.append(json_test)
            
            print(f"\n=== RESULTS ===")
            print(f"Matched tests: {len(matched_tests)}")
            print(f"Missing tests: {len(missing_tests)}")
            
            if missing_tests:
                print(f"\n=== MISSING TESTS ===")
                for i, test in enumerate(missing_tests, 1):
                    test_info = test.get('testInfo', {})
                    print(f"\n{i}. {test_info.get('summary', 'Unknown')}")
                    print(f"   Labels: {', '.join(test_info.get('labels', []))}")
                    if 'steps' in test_info:
                        print(f"   Steps: {len(test_info['steps'])}")
            
            # Save results for next steps
            results = {
                'matched_tests': matched_tests,
                'missing_tests': missing_tests,
                'xray_summaries': list(xray_by_summary.keys())
            }
            
            output_path = Path(__file__).parent.parent / "logs" / "missing_tests_analysis.json"
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
            
            print(f"\n✓ Analysis saved to: {output_path}")
            
            # Also check for any Xray tests not in JSON
            json_summaries = {test.get('testInfo', {}).get('summary', '') for test in json_tests}
            orphan_tests = []
            
            for summary, test in xray_by_summary.items():
                if summary not in json_summaries:
                    orphan_tests.append({
                        'key': test['jira']['key'],
                        'summary': summary
                    })
            
            if orphan_tests:
                print(f"\n=== ORPHAN TESTS IN XRAY (not in JSON) ===")
                for test in orphan_tests:
                    print(f"- {test['key']}: {test['summary']}")
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_missing_tests()