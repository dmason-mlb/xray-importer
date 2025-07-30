#!/usr/bin/env python3
"""
Build complete Test Case ID to JIRA issue key mapping from live JIRA API queries.
Replaces hardcoded approach with dynamic JIRA GraphQL queries using pagination.
"""

import re
import json
import os
import requests
import time
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
                jira(fields: ["key", "summary", "description"])
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

def fetch_all_framed_tests():
    """Fetch all FRAMED tests using pagination"""
    
    print("🔍 Fetching all FRAMED project tests...")
    
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
    
    return all_tests

def extract_test_case_id_from_description(description):
    """Extract Test Case ID from JIRA issue description."""
    if not description:
        return None
    
    match = re.search(r'Test Case ID:\s*([A-Z][A-Z0-9-]+)', description)
    if match:
        return match.group(1)
    return None

def build_mapping_from_live_jira_data():
    """Build mapping from live JIRA API queries."""
    
    # Fetch all tests from JIRA
    all_tests = fetch_all_framed_tests()
    
    mapping = {}
    jira_tests_without_test_case_ids = []
    
    print(f"\n🔄 Processing {len(all_tests)} JIRA tests...")
    
    for test in all_tests:
        jira_data = test.get("jira", {})
        jira_key = jira_data.get("key")
        description = jira_data.get("description", "")
        
        if not jira_key:
            continue
            
        test_case_id = extract_test_case_id_from_description(description)
        if test_case_id:
            mapping[test_case_id] = jira_key
            print(f"   ✓ {test_case_id} → {jira_key}")
        else:
            jira_tests_without_test_case_ids.append({
                "key": jira_key,
                "summary": jira_data.get("summary", "")
            })
    
    return mapping, jira_tests_without_test_case_ids

def get_pytest_test_case_ids():
    """Get all Test Case IDs from pytest files."""
    pytest_dir = Path("/Users/douglas.mason/Documents/GitHub/MLB-App/Service/Bullpen/test/pytest-allure/tests/team_page")
    
    test_case_ids = set()
    pattern = re.compile(r'@allure\.tag\(\"([^\"]+)\"\)')
    
    if not pytest_dir.exists():
        print(f"⚠️  Pytest directory not found: {pytest_dir}")
        return test_case_ids
    
    for py_file in pytest_dir.glob("*.py"):
        try:
            content = py_file.read_text()
            matches = pattern.findall(content)
            for match in matches:
                if match.startswith(("API-", "FUNC-")):
                    test_case_ids.add(match)
        except Exception as e:
            print(f"⚠️  Error reading {py_file}: {e}")
    
    return test_case_ids

def main():
    """Build and save the complete mapping."""
    
    try:
        # Build mapping from live JIRA data
        mapping, jira_tests_without_test_case_ids = build_mapping_from_live_jira_data()
        
        # Get pytest Test Case IDs
        pytest_test_case_ids = get_pytest_test_case_ids()
        
        # Save the mapping
        output_file = Path(__file__).parent.parent / "complete_test_id_mapping.json"
        with open(output_file, 'w') as f:
            json.dump(mapping, f, indent=2, sort_keys=True)
        
        print(f"\n✅ Built mapping for {len(mapping)} test case IDs")
        print(f"✅ Saved to: {output_file}")
        
        # Analyze coverage
        mapped_test_case_ids = set(mapping.keys())
        missing_in_jira = pytest_test_case_ids - mapped_test_case_ids
        extra_in_jira = mapped_test_case_ids - pytest_test_case_ids
        
        print(f"\n📊 ANALYSIS:")
        print(f"   Pytest Test Case IDs: {len(pytest_test_case_ids)}")
        print(f"   JIRA Test Case IDs: {len(mapped_test_case_ids)}")
        print(f"   Complete mappings: {len(mapped_test_case_ids & pytest_test_case_ids)}")
        
        if missing_in_jira:
            print(f"\n⚠️  Missing in JIRA ({len(missing_in_jira)} Test Case IDs):")
            for test_id in sorted(missing_in_jira):
                print(f"   - {test_id}")
        
        if extra_in_jira:
            print(f"\n📝 Extra JIRA mappings ({len(extra_in_jira)} Test Case IDs):")
            for test_id in sorted(extra_in_jira):
                print(f"   - {test_id} → {mapping[test_id]}")
        
        if jira_tests_without_test_case_ids:
            print(f"\n📋 JIRA tests without Test Case IDs ({len(jira_tests_without_test_case_ids)}):")
            for test in jira_tests_without_test_case_ids:
                print(f"   - {test['key']}: {test['summary']}")
        
        # Save analysis report
        analysis_file = Path(__file__).parent.parent / "test_case_id_analysis.json"
        analysis = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "pytest_test_case_ids": sorted(list(pytest_test_case_ids)),
            "jira_test_case_ids": sorted(list(mapped_test_case_ids)),
            "missing_in_jira": sorted(list(missing_in_jira)),
            "extra_in_jira": sorted(list(extra_in_jira)),
            "jira_tests_without_test_case_ids": jira_tests_without_test_case_ids,
            "total_mappings": len(mapping),
            "coverage_percentage": round((len(mapped_test_case_ids & pytest_test_case_ids) / len(pytest_test_case_ids)) * 100, 1) if pytest_test_case_ids else 0
        }
        
        with open(analysis_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        print(f"📄 Analysis saved to: {analysis_file}")
        
    except Exception as e:
        print(f"❌ Failed to build mapping: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()