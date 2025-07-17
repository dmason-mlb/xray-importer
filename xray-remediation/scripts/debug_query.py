#!/usr/bin/env python3
"""
Debug GraphQL queries to identify issues
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
from auth_utils import XrayAPIClient

def test_simple_queries():
    """Test increasingly complex queries to find what works"""
    
    client = XrayAPIClient()
    
    # Test 1: Very simple query
    print("Testing simple query...")
    simple_query = """
    query {
        getTests(jql: "project = FRAMED", limit: 5) {
            total
        }
    }
    """
    
    try:
        result = client.execute_graphql_query(simple_query)
        print(f"✅ Simple query works: {result}")
    except Exception as e:
        print(f"❌ Simple query failed: {e}")
        return
    
    # Test 2: Add basic fields
    print("\nTesting with basic fields...")
    basic_query = """
    query {
        getTests(jql: "project = FRAMED", limit: 5) {
            total
            results {
                issueId
                summary
            }
        }
    }
    """
    
    try:
        result = client.execute_graphql_query(basic_query)
        print(f"✅ Basic fields query works: Found {result['getTests']['total']} tests")
        if result['getTests']['results']:
            print(f"Sample test: {result['getTests']['results'][0]}")
    except Exception as e:
        print(f"❌ Basic fields query failed: {e}")
        return
    
    # Test 3: Add more fields incrementally
    print("\nTesting with additional fields...")
    extended_query = """
    query {
        getTests(jql: "project = FRAMED", limit: 5) {
            total
            results {
                issueId
                summary
                testType
                labels
            }
        }
    }
    """
    
    try:
        result = client.execute_graphql_query(extended_query)
        print(f"✅ Extended query works")
        if result['getTests']['results']:
            test = result['getTests']['results'][0]
            print(f"Sample test: {test['issueId']} - {test['summary']}")
            print(f"Labels: {test.get('labels', [])}")
    except Exception as e:
        print(f"❌ Extended query failed: {e}")
        return
    
    # Test 4: Test preconditions query separately
    print("\nTesting preconditions query...")
    precond_query = """
    query {
        getPreconditions(jql: "project = FRAMED", limit: 5) {
            total
        }
    }
    """
    
    try:
        result = client.execute_graphql_query(precond_query)
        print(f"✅ Preconditions query works: Found {result['getPreconditions']['total']} preconditions")
    except Exception as e:
        print(f"❌ Preconditions query failed: {e}")

if __name__ == "__main__":
    test_simple_queries()