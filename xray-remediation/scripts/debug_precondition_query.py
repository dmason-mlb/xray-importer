#!/usr/bin/env python3
"""
Debug script to test precondition queries
"""

import json
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'xray-api'))

from auth_utils import XrayAPIClient

def debug_precondition_query():
    """Test querying a specific precondition"""
    print("Testing Precondition Query...")
    print("=" * 50)
    
    client = XrayAPIClient()
    
    # Test with a known precondition ID
    test_cases = [
        ("FRAMED-1364", "1158154"),
        ("FRAMED-1584", "1162603")
    ]
    
    for jira_key, issue_id in test_cases:
        print(f"\nQuerying {jira_key} (ID: {issue_id})")
        
        query = """
        query GetPreconditionWithTests($issueId: String!) {
            getPrecondition(issueId: $issueId) {
                issueId
                definition
                preconditionType {
                    name
                    kind
                }
                tests(limit: 100, start: 0) {
                    total
                    results {
                        issueId
                        jira(fields: ["key", "summary"])
                    }
                }
                jira(fields: ["key", "summary", "labels"])
            }
        }
        """
        
        variables = {"issueId": issue_id}
        result = client.execute_graphql_query(query, variables)
        
        print(f"Raw response: {json.dumps(result, indent=2)}")
        
        # Try to extract the data
        if result and 'data' in result and 'getPrecondition' in result['data']:
            precond = result['data']['getPrecondition']
            if precond:
                jira_data = precond.get('jira', {})
                print(f"\nExtracted data:")
                print(f"  Key: {jira_data.get('key', 'N/A')}")
                print(f"  Summary: {jira_data.get('summary', 'N/A')}")
                print(f"  Labels: {jira_data.get('labels', [])}")
                print(f"  Tests total: {precond.get('tests', {}).get('total', 0)}")
            else:
                print("  No precondition data in response")
        else:
            print("  Unexpected response format")

if __name__ == "__main__":
    debug_precondition_query()