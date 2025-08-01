#!/usr/bin/env python3
"""
Verify which preconditions still exist
"""

import json
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'xray-api'))

from auth_utils import XrayAPIClient

def verify_preconditions():
    """Check which preconditions exist"""
    print("Verifying FRAMED Preconditions...")
    print("=" * 50)
    
    client = XrayAPIClient()
    
    # Check both original and duplicate ranges
    preconditions = {
        "Original (FRAMED-135x)": [
            ("FRAMED-1355", "1158139"),
            ("FRAMED-1364", "1158154"),
            ("FRAMED-1369", "1158163"),
            ("FRAMED-1372", "1158169"),
            ("FRAMED-1375", "1158174"),
        ],
        "Duplicates (FRAMED-157x/158x/159x)": [
            ("FRAMED-1575", "1162594"),
            ("FRAMED-1584", "1162603"),
            ("FRAMED-1589", "1162608"),
            ("FRAMED-1592", "1162611"),
            ("FRAMED-1595", "1162614"),
        ]
    }
    
    for group_name, items in preconditions.items():
        print(f"\n{group_name}:")
        for jira_key, issue_id in items:
            query = """
            query GetPrecondition($issueId: String!) {
                getPrecondition(issueId: $issueId) {
                    issueId
                    jira(fields: ["key", "summary", "labels"])
                }
            }
            """
            
            variables = {"issueId": issue_id}
            result = client.execute_graphql_query(query, variables)
            
            if result and 'getPrecondition' in result:
                if result['getPrecondition'] is not None:
                    jira = result['getPrecondition'].get('jira', {})
                    print(f"  ✓ {jira_key} exists - {jira.get('summary', 'N/A')} - Labels: {jira.get('labels', [])}")
                else:
                    print(f"  ✗ {jira_key} deleted")
            else:
                print(f"  ? {jira_key} error checking")

if __name__ == "__main__":
    verify_preconditions()