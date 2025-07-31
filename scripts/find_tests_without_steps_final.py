#!/usr/bin/env python3
"""
Optimized script to find tests without steps in Applause Regression folder.
Uses smaller batches and early filtering to avoid timeouts.
"""

import os
import sys
import json
import requests
import time
from typing import List, Dict, Optional
from datetime import datetime

# GraphQL endpoint
GRAPHQL_ENDPOINT = "https://xray.cloud.getxray.app/api/v2/graphql"
AUTH_ENDPOINT = "https://xray.cloud.getxray.app/api/v2/authenticate"

# Target folder
TARGET_FOLDER = "/Applause Regression"
PROJECT_KEY = "MLBMOB"
PROJECT_ID = "26420"

class XrayGraphQLClient:
    """Client for interacting with Xray GraphQL API."""
    
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = None
        self.headers = {
            "Content-Type": "application/json"
        }
    
    def authenticate(self) -> bool:
        """Authenticate with Xray API and get JWT token."""
        auth_data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        try:
            response = requests.post(AUTH_ENDPOINT, json=auth_data)
            response.raise_for_status()
            self.token = response.text.strip('"')
            self.headers["Authorization"] = f"Bearer {self.token}"
            print("✓ Successfully authenticated with Xray API")
            return True
        except requests.exceptions.RequestException as e:
            print(f"✗ Failed to authenticate: {e}")
            return False
    
    def execute_query(self, query: str, variables: Dict = None) -> Optional[Dict]:
        """Execute a GraphQL query."""
        payload = {
            "query": query,
            "variables": variables or {}
        }
        
        try:
            response = requests.post(GRAPHQL_ENDPOINT, json=payload, headers=self.headers)
            response.raise_for_status()
            
            result = response.json()
            if "errors" in result:
                print(f"GraphQL errors: {json.dumps(result['errors'], indent=2)}")
                return None
            
            return result.get("data")
        except requests.exceptions.RequestException as e:
            print(f"✗ Request failed: {e}")
            return None
    
    def get_tests_batch(self, start: int, limit: int = 100) -> Optional[Dict]:
        """Get a batch of tests."""
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
                    steps {
                        id
                    }
                    testType {
                        name
                    }
                    jira(fields: ["key", "summary"])
                }
            }
        }
        """
        
        variables = {
            "jql": f"project = {PROJECT_KEY} AND issuetype = Test",
            "limit": limit,
            "start": start
        }
        
        return self.execute_query(query, variables)

def main():
    """Main function."""
    # Get credentials
    client_id = os.getenv("XRAY_CLIENT")
    client_secret = os.getenv("XRAY_SECRET")
    
    if not client_id or not client_secret:
        print("✗ Error: XRAY_CLIENT and XRAY_SECRET environment variables must be set")
        sys.exit(1)
    
    # Initialize client
    client = XrayGraphQLClient(client_id, client_secret)
    
    if not client.authenticate():
        sys.exit(1)
    
    print(f"\nSearching for tests without steps in '{TARGET_FOLDER}'...")
    
    # First, get total count
    data = client.get_tests_batch(0, 1)
    if not data or not data.get("getTests"):
        print("✗ Failed to get test count")
        sys.exit(1)
    
    total = data["getTests"]["total"]
    print(f"Total tests in project: {total}")
    
    # Process in batches
    batch_size = 100  # Increased batch size
    start = 0
    tests_without_steps = []
    tests_in_applause = 0
    
    print("\nProcessing tests...")
    start_time = time.time()
    
    while start < total:
        # Check if we've been running too long
        if time.time() - start_time > 110:  # 110 seconds max
            print("\n⚠️  Processing time limit reached. Stopping early.")
            print(f"Processed {start} of {total} tests")
            break
        
        data = client.get_tests_batch(start, batch_size)
        if not data or not data.get("getTests"):
            break
        
        results = data["getTests"]["results"]
        
        # Process each test
        for test in results:
            folder = test.get("folder", {})
            folder_path = folder.get("path", "") if folder else ""
            
            # Check if in Applause Regression folder
            if folder_path.startswith(TARGET_FOLDER):
                tests_in_applause += 1
                
                # Check if has no steps
                steps = test.get("steps", [])
                if not steps:
                    jira = test.get("jira", {})
                    key = jira.get("key", "Unknown") if jira else "Unknown"
                    summary = jira.get("summary", "No summary") if jira else "No summary"
                    test_type = test.get("testType", {}).get("name", "Unknown")
                    
                    tests_without_steps.append({
                        "key": key,
                        "summary": summary,
                        "folder": folder_path,
                        "testType": test_type
                    })
        
        start += batch_size
        
        # Progress update
        if start % 400 == 0 or start >= total:
            elapsed = time.time() - start_time
            print(f"  Processed: {min(start, total)}/{total} tests ({elapsed:.1f}s)")
            print(f"    - In Applause Regression: {tests_in_applause}")
            print(f"    - Without steps: {len(tests_without_steps)}")
    
    # Generate report
    print(f"\n{'='*50}")
    print(f"RESULTS:")
    print(f"  • Tests in Applause Regression: {tests_in_applause}")
    print(f"  • Tests without steps: {len(tests_without_steps)}")
    
    if tests_without_steps:
        # Save report
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open("applause_tests_without_steps.txt", "w") as f:
            f.write(f"Tests Without Steps in Applause Regression\n")
            f.write(f"==========================================\n\n")
            f.write(f"Generated: {timestamp}\n")
            f.write(f"Total: {len(tests_without_steps)} tests\n")
            f.write(f"\n{'-'*80}\n\n")
            
            # Group by folder
            by_folder = {}
            for test in tests_without_steps:
                folder = test['folder']
                if folder not in by_folder:
                    by_folder[folder] = []
                by_folder[folder].append(test)
            
            for folder in sorted(by_folder.keys()):
                f.write(f"Folder: {folder}\n")
                f.write(f"{'-'*40}\n")
                for test in sorted(by_folder[folder], key=lambda x: x['key']):
                    f.write(f"  • {test['key']} - {test['summary']}\n")
                    f.write(f"    Type: {test['testType']}\n")
                    f.write(f"    Link: https://mlbam.atlassian.net/browse/{test['key']}\n\n")
                f.write("\n")
        
        # Save CSV
        with open("applause_tests_without_steps.csv", "w") as f:
            f.write("Issue Key,Summary,Test Type,Folder Path,JIRA Link\n")
            for test in sorted(tests_without_steps, key=lambda x: x['key']):
                summary = test['summary'].replace('"', '""')
                f.write(f'"{test["key"]}","{summary}","{test["testType"]}","{test["folder"]}","https://mlbam.atlassian.net/browse/{test["key"]}"\n')
        
        print(f"\n✓ Report saved to: applause_tests_without_steps.txt")
        print(f"✓ CSV saved to: applause_tests_without_steps.csv")
        
        # Show first few examples
        print(f"\nFirst {min(5, len(tests_without_steps))} tests without steps:")
        for i, test in enumerate(tests_without_steps[:5]):
            print(f"  {i+1}. {test['key']} - {test['summary']}")

if __name__ == "__main__":
    main()