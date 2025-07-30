#!/usr/bin/env python3
"""
Simple test to get working query format
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
from auth_utils import XrayAPIClient

def test_working_format():
    """Test with exact working format from existing scripts"""
    
    client = XrayAPIClient()
    
    # Use exact format from working script
    query = """
    query GetTests($jql: String!, $limit: Int!, $start: Int!) {
        getTests(jql: $jql, limit: $limit, start: $start) {
            total
            start
            limit
            results {
                issueId
                folder {
                    path
                }
            }
        }
    }
    """
    
    variables = {
        "jql": "project = FRAMED",
        "limit": 10,
        "start": 0
    }
    
    try:
        result = client.execute_graphql_query(query, variables)
        print(f"✅ Query successful!")
        print(f"Total tests: {result['getTests']['total']}")
        print(f"Results returned: {len(result['getTests']['results'])}")
        
        if result['getTests']['results']:
            for test in result['getTests']['results'][:5]:
                print(f"  - {test['issueId']} in folder: {test.get('folder', {}).get('path', 'No folder')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Query failed: {e}")
        
        # Try even simpler
        simple_query = """
        query {
            getTests(jql: "project = FRAMED", limit: 5) {
                total
                results {
                    issueId
                }
            }
        }
        """
        
        try:
            result2 = client.execute_graphql_query(simple_query)
            print(f"✅ Simple query worked: {result2['getTests']['total']} tests")
        except Exception as e2:
            print(f"❌ Even simple query failed: {e2}")

if __name__ == "__main__":
    test_working_format()