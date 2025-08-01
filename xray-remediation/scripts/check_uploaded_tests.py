#!/usr/bin/env python3
"""
Check what functional tests have been uploaded to Xray
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir / 'xray-api'))
from auth_utils import XrayAPIClient

def check_uploaded_tests():
    client = XrayAPIClient()
    
    # Query to get recently created tests
    query = """
    query GetRecentTests($jql: String!, $limit: Int!) {
        getTests(jql: $jql, limit: $limit) {
            total
            results {
                issueId
                jira(fields: ["key", "summary", "labels", "created"])
                testType {
                    name
                }
            }
        }
    }
    """
    
    # Get tests created today with functional label
    variables = {
        "jql": "project = FRAMED AND created >= '2025-08-01' AND labels = functional ORDER BY created DESC",
        "limit": 50
    }
    
    try:
        result = client.execute_graphql_query(query, variables)
        
        if result and 'getTests' in result:
            tests = result['getTests']['results']
            total = result['getTests']['total']
            
            print(f"\n=== FUNCTIONAL TESTS UPLOADED TODAY ===")
            print(f"Total found: {total}")
            print(f"\nTests:")
            
            for i, test in enumerate(tests, 1):
                key = test['jira'].get('key', 'Unknown')
                summary = test['jira'].get('summary', 'No summary')
                created = test['jira'].get('created', 'Unknown')
                test_type = test['testType']['name'] if test.get('testType') else 'Unknown'
                
                print(f"\n{i}. {key}: {summary}")
                print(f"   Type: {test_type}")
                print(f"   Created: {created}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_uploaded_tests()