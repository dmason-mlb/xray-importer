#!/usr/bin/env python3
"""
Fetch FRAMED project data directly
Based on working script logic
"""

import json
import requests
import os
import time
from datetime import datetime
from pathlib import Path

# Configuration
XRAY_BASE_URL = "https://xray.cloud.getxray.app/api"
PROJECT_KEY = "FRAMED"
BATCH_SIZE = 50

def get_auth_token():
    """Get authentication token"""
    client_id = os.environ.get('XRAY_CLIENT_ID')
    client_secret = os.environ.get('XRAY_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        raise ValueError("XRAY_CLIENT_ID and XRAY_CLIENT_SECRET must be set")
    
    auth_url = f"{XRAY_BASE_URL}/v1/authenticate"
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
    
    response = requests.post(f"{XRAY_BASE_URL}/v2/graphql", headers=headers, json=payload)
    response.raise_for_status()
    
    result = response.json()
    if "errors" in result:
        raise Exception(f"GraphQL errors: {result['errors']}")
    
    return result.get("data")

def fetch_tests_batch(token, start=0, limit=50):
    """Fetch a batch of tests using the working query format"""
    
    query = """
    query GetTests($jql: String!, $limit: Int!, $start: Int!) {
        getTests(jql: $jql, limit: $limit, start: $start) {
            total
            start
            limit
            results {
                issueId
                testType {
                    name
                }
                folder {
                    path
                }
                steps {
                    id
                }
                jira(fields: ["key", "summary", "labels"])
            }
        }
    }
    """
    
    variables = {
        "jql": f"project = {PROJECT_KEY} AND issuetype = Test",
        "limit": limit,
        "start": start
    }
    
    return execute_graphql_query(token, query, variables)

def fetch_preconditions(token):
    """Fetch all preconditions"""
    
    query = """
    query GetPreconditions($jql: String!, $limit: Int!) {
        getPreconditions(jql: $jql, limit: $limit) {
            total
            results {
                issueId
                jira(fields: ["key", "summary"])
            }
        }
    }
    """
    
    variables = {
        "jql": f"project = {PROJECT_KEY} AND issuetype = 'Pre-Condition'",
        "limit": 200
    }
    
    return execute_graphql_query(token, query, variables)

def fetch_all_framed_data():
    """Fetch all FRAMED data"""
    
    print("🔍 Fetching FRAMED project data...")
    
    # Get authentication
    print("🔐 Authenticating...")
    token = get_auth_token()
    print("✅ Authentication successful")
    
    # Fetch tests in batches
    print("📊 Fetching tests...")
    all_tests = []
    start = 0
    
    while True:
        print(f"   Batch starting at {start}...")
        result = fetch_tests_batch(token, start, BATCH_SIZE)
        
        tests_data = result['getTests']
        batch_tests = tests_data['results']
        all_tests.extend(batch_tests)
        
        total = tests_data['total']
        print(f"   Retrieved {len(batch_tests)} tests (total: {len(all_tests)}/{total})")
        
        if start + BATCH_SIZE >= total:
            break
            
        start += BATCH_SIZE
        time.sleep(0.5)  # Rate limiting
    
    print(f"✅ Retrieved {len(all_tests)} tests")
    
    # Fetch preconditions
    print("📋 Fetching preconditions...")
    precond_result = fetch_preconditions(token)
    preconditions = precond_result['getPreconditions']['results']
    print(f"✅ Retrieved {len(preconditions)} preconditions")
    
    # Save data
    data = {
        "timestamp": datetime.now().isoformat(),
        "project": PROJECT_KEY,
        "tests": all_tests,
        "preconditions": preconditions,
        "summary": {
            "total_tests": len(all_tests),
            "total_preconditions": len(preconditions)
        }
    }
    
    output_file = Path(__file__).parent.parent / 'backups' / 'framed_raw_data.json'
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"💾 Data saved to: {output_file}")
    
    return data

if __name__ == "__main__":
    try:
        data = fetch_all_framed_data()
        print(f"\n✅ FRAMED data fetch complete:")
        print(f"   - {data['summary']['total_tests']} tests")
        print(f"   - {data['summary']['total_preconditions']} preconditions")
        
    except Exception as e:
        print(f"❌ Fetch failed: {e}")
        import traceback
        traceback.print_exc()