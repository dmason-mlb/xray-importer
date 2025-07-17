#!/usr/bin/env python3
"""
Explore what projects and data exist in Xray
"""

import json
import requests
import os
from pathlib import Path

def get_auth_token():
    """Get authentication token"""
    client_id = os.environ.get('XRAY_CLIENT_ID')
    client_secret = os.environ.get('XRAY_CLIENT_SECRET')
    
    auth_url = "https://xray.cloud.getxray.app/api/v1/authenticate"
    auth_data = {
        "client_id": client_id,
        "client_secret": client_secret
    }
    
    response = requests.post(auth_url, json=auth_data)
    response.raise_for_status()
    
    return response.text.strip('"')

def execute_graphql_query(token, query, variables=None):
    """Execute GraphQL query"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "query": query,
        "variables": variables or {}
    }
    
    response = requests.post("https://xray.cloud.getxray.app/api/v2/graphql", headers=headers, json=payload)
    response.raise_for_status()
    
    result = response.json()
    if "errors" in result:
        print(f"GraphQL errors: {result['errors']}")
        return None
    
    return result.get("data")

def explore_data():
    """Explore what data is available"""
    
    print("🔍 Exploring Xray data...")
    
    token = get_auth_token()
    print("✅ Authentication successful")
    
    # Try different queries to see what works
    queries_to_try = [
        {
            "name": "Simple test count",
            "query": """
            query {
                getTests(limit: 1) {
                    total
                }
            }
            """
        },
        {
            "name": "Tests in FRAMED project",
            "query": """
            query {
                getTests(jql: "project = FRAMED", limit: 5) {
                    total
                    results {
                        issueId
                    }
                }
            }
            """
        },
        {
            "name": "Tests with issuetype",
            "query": """
            query {
                getTests(jql: "project = FRAMED AND issuetype = Test", limit: 5) {
                    total
                    results {
                        issueId
                    }
                }
            }
            """
        },
        {
            "name": "All tests (any project)",
            "query": """
            query {
                getTests(limit: 10) {
                    total
                    results {
                        issueId
                        jira(fields: ["key", "project"])
                    }
                }
            }
            """
        },
        {
            "name": "Preconditions in FRAMED",
            "query": """
            query {
                getPreconditions(jql: "project = FRAMED", limit: 5) {
                    total
                    results {
                        issueId
                    }
                }
            }
            """
        }
    ]
    
    results = {}
    
    for query_info in queries_to_try:
        print(f"\n📊 Testing: {query_info['name']}")
        
        try:
            result = execute_graphql_query(token, query_info['query'])
            if result:
                results[query_info['name']] = result
                
                # Print summary
                if 'getTests' in result:
                    total = result['getTests']['total']
                    print(f"   ✅ Found {total} tests")
                    
                    if result['getTests'].get('results'):
                        for test in result['getTests']['results'][:3]:
                            jira_info = test.get('jira', {})
                            project = jira_info.get('project', {}).get('key', 'Unknown') if jira_info else 'Unknown'
                            print(f"      - {test['issueId']} (Project: {project})")
                
                elif 'getPreconditions' in result:
                    total = result['getPreconditions']['total']
                    print(f"   ✅ Found {total} preconditions")
                    
            else:
                print(f"   ❌ Query failed or returned no data")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results[query_info['name']] = {"error": str(e)}
    
    # Save exploration results
    output_file = Path(__file__).parent.parent / 'logs' / 'data_exploration.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Exploration results saved to: {output_file}")
    
    return results

if __name__ == "__main__":
    try:
        results = explore_data()
        
        print("\n" + "="*50)
        print("EXPLORATION SUMMARY")
        print("="*50)
        
        for name, result in results.items():
            if "error" in result:
                print(f"❌ {name}: {result['error']}")
            elif 'getTests' in result:
                print(f"✅ {name}: {result['getTests']['total']} tests")
            elif 'getPreconditions' in result:
                print(f"✅ {name}: {result['getPreconditions']['total']} preconditions")
            else:
                print(f"? {name}: Unknown result format")
        
    except Exception as e:
        print(f"❌ Exploration failed: {e}")
        import traceback
        traceback.print_exc()