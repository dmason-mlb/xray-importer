#!/usr/bin/env python3
"""
Get numeric project ID for FRAMED project.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "xray-api"))

from auth_utils import XrayAPIClient

def main():
    client = XrayAPIClient()
    token = client.get_auth_token()
    
    # Try to get project info through tests
    query = """
    query GetProjectInfo {
        getTests(jql: "project = FRAMED", limit: 1) {
            results {
                projectId
                jira(fields: ["project"])
            }
        }
    }
    """
    
    try:
        response = client.execute_graphql_query(query, {})
        if response and 'getTests' in response:
            results = response['getTests']['results']
            if results:
                print(f"Project info from test:")
                print(f"  projectId field: {results[0].get('projectId', 'Not found')}")
                print(f"  JIRA project: {results[0]['jira'].get('project', {})}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()