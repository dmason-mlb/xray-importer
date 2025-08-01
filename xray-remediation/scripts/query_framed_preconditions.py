#!/usr/bin/env python3
"""
Query FRAMED project preconditions using Xray GraphQL API
"""

import json
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'xray-api'))

from auth_utils import XrayAPIClient

def query_framed_preconditions():
    """Query all FRAMED preconditions using GraphQL"""
    print("Querying FRAMED Preconditions via Xray GraphQL...")
    print("=" * 50)
    
    client = XrayAPIClient()
    
    # Query to get FRAMED preconditions using JQL
    query = """
    query GetFramedPreconditions($jql: String!, $limit: Int!, $start: Int) {
        getPreconditions(jql: $jql, limit: $limit, start: $start) {
            total
            results {
                issueId
                definition
                preconditionType {
                    name
                    kind
                }
                tests(limit: 10, start: 0) {
                    total
                    results {
                        issueId
                        jira(fields: ["key", "summary"])
                    }
                }
                jira(fields: ["key", "summary", "labels", "status"])
            }
        }
    }
    """
    
    variables = {
        "jql": "project = FRAMED AND issuetype = Precondition ORDER BY key ASC",
        "limit": 50,
        "start": 0
    }
    
    all_preconditions = []
    
    while True:
        result = client.execute_graphql_query(query, variables)
        
        if not result or not result.get('data', {}).get('getPreconditions'):
            print("Error: No data returned")
            print(f"Response: {json.dumps(result, indent=2)}")
            break
        
        data = result['data']['getPreconditions']
        total = data.get('total', 0)
        results = data.get('results', [])
        
        print(f"\nBatch: Retrieved {len(results)} preconditions (total: {total})")
        
        for precond in results:
            jira_data = precond.get('jira', {})
            key = jira_data.get('key', 'Unknown')
            summary = jira_data.get('summary', 'No summary')
            labels = jira_data.get('labels', [])
            status = jira_data.get('status', {})
            issue_id = precond.get('issueId')
            
            tests_data = precond.get('tests', {})
            test_count = tests_data.get('total', 0)
            test_keys = []
            
            if tests_data.get('results'):
                for test in tests_data['results']:
                    test_jira = test.get('jira', {})
                    test_key = test_jira.get('key')
                    if test_key:
                        test_keys.append(test_key)
            
            precondition_info = {
                'key': key,
                'issueId': issue_id,
                'summary': summary,
                'labels': labels,
                'status': status.get('name', 'Unknown'),
                'test_count': test_count,
                'test_keys': test_keys[:5],  # First 5 tests
                'definition': precond.get('definition', '')
            }
            
            all_preconditions.append(precondition_info)
            
            print(f"  {key} (ID: {issue_id})")
            print(f"    Summary: {summary}")
            print(f"    Labels: {labels}")
            print(f"    Tests: {test_count} - {', '.join(test_keys[:3])}{'...' if len(test_keys) > 3 else ''}")
        
        # Check if we need to fetch more
        variables['start'] += len(results)
        if variables['start'] >= total:
            break
    
    # Save results
    output_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                              'logs', 'framed_preconditions_graphql.json')
    
    with open(output_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total': len(all_preconditions),
            'preconditions': all_preconditions
        }, f, indent=2)
    
    print(f"\n\nSummary:")
    print(f"Total FRAMED preconditions found: {len(all_preconditions)}")
    print(f"Results saved to: {output_file}")
    
    # Analyze for duplicates based on summary
    print("\n\nAnalyzing for duplicates...")
    summary_map = {}
    for precond in all_preconditions:
        summary = precond['summary']
        if summary in summary_map:
            summary_map[summary].append(precond['key'])
        else:
            summary_map[summary] = [precond['key']]
    
    duplicates = {k: v for k, v in summary_map.items() if len(v) > 1}
    if duplicates:
        print(f"Found {len(duplicates)} duplicate summaries:")
        for summary, keys in duplicates.items():
            print(f"  '{summary}': {', '.join(keys)}")
    else:
        print("No duplicate summaries found")
    
    return all_preconditions

if __name__ == "__main__":
    from datetime import datetime
    query_framed_preconditions()