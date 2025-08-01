#!/usr/bin/env python3
"""
Test script to verify Xray GraphQL API connectivity and precondition queries
"""

import json
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'xray-api'))

from auth_utils import XrayAPIClient

def test_xray_connection():
    """Test basic Xray API connectivity"""
    print("Testing Xray API Connection...")
    print("=" * 50)
    
    try:
        client = XrayAPIClient()
        print("✓ Successfully initialized Xray API client")
        print(f"  Token obtained: {'Yes' if client.token else 'No'}")
        
        # Test a simple GraphQL query
        test_query = """
        query TestConnection {
            getTests(limit: 1, start: 0) {
                total
            }
        }
        """
        
        result = client.execute_graphql_query(test_query, {})
        print(f"\n✓ GraphQL endpoint accessible")
        print(f"  Response: {json.dumps(result, indent=2)}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        return False

def test_precondition_query():
    """Test querying a specific precondition"""
    print("\n\nTesting Precondition Query...")
    print("=" * 50)
    
    client = XrayAPIClient()
    
    # Try a known precondition
    test_issue = "FRAMED-1595"
    
    # First, try a simpler query
    simple_query = """
    query GetPrecondition($issueId: String!) {
        getPrecondition(issueId: $issueId) {
            issueId
            definition
        }
    }
    """
    
    print(f"\nQuerying precondition: {test_issue}")
    print("Using simple query first...")
    
    variables = {"issueId": test_issue}
    result = client.execute_graphql_query(simple_query, variables)
    
    print(f"Response: {json.dumps(result, indent=2)}")
    
    if result.get('data', {}).get('getPrecondition'):
        print("✓ Simple query successful, trying full query...")
        
        # Now try the full query
        full_query = """
        query GetPreconditionWithTests($issueId: String!) {
            getPrecondition(issueId: $issueId) {
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
                jira(fields: ["key", "summary", "labels"])
            }
        }
        """
        
        result = client.execute_graphql_query(full_query, variables)
        print(f"\nFull query response: {json.dumps(result, indent=2)}")
    else:
        print("✗ Simple query failed - precondition might not exist or access denied")

def test_all_preconditions():
    """Test querying all preconditions"""
    print("\n\nTesting All Preconditions Query...")
    print("=" * 50)
    
    client = XrayAPIClient()
    
    # Try to get all preconditions
    query = """
    query GetPreconditions {
        getPreconditions(limit: 5, start: 0) {
            total
            results {
                issueId
                definition
                jira(fields: ["key", "summary"])
            }
        }
    }
    """
    
    print("Querying for preconditions (limit 5)...")
    result = client.execute_graphql_query(query, {})
    
    print(f"Response: {json.dumps(result, indent=2)}")
    
    if result.get('data', {}).get('getPreconditions'):
        total = result['data']['getPreconditions'].get('total', 0)
        results = result['data']['getPreconditions'].get('results', [])
        print(f"\n✓ Found {total} total preconditions")
        print(f"  Retrieved {len(results)} in this batch")
        
        for precond in results:
            jira_data = precond.get('jira', {})
            key = jira_data.get('key', 'Unknown')
            summary = jira_data.get('summary', 'No summary')
            print(f"  - {key}: {summary}")
    else:
        print("✗ Failed to retrieve preconditions")

if __name__ == "__main__":
    # Run tests
    if test_xray_connection():
        test_precondition_query()
        test_all_preconditions()
    else:
        print("\nCannot proceed with further tests - API connection failed")