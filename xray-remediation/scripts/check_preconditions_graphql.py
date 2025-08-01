#!/usr/bin/env python3
"""
Check for existing preconditions using Xray GraphQL API
"""
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir / 'xray-api'))
from auth_utils import XrayAPIClient

def check_existing_preconditions():
    # Initialize client
    client = XrayAPIClient()
    
    # Load the precondition analysis
    analysis_path = Path(__file__).parent.parent / "logs" / "precondition_analysis.json"
    with open(analysis_path, 'r') as f:
        analysis_data = json.load(f)
    
    unique_preconditions = analysis_data['unique_preconditions']
    
    print(f"\n=== CHECKING EXISTING PRECONDITIONS IN XRAY ===")
    print(f"Total unique preconditions to check: {len(unique_preconditions)}")
    
    # GraphQL query to get all preconditions
    query = """
    query GetPreconditions($jql: String!, $limit: Int!) {
        getPreconditions(jql: $jql, limit: $limit) {
            total
            results {
                issueId
                jira(fields: ["key", "summary", "labels"])
                definition
            }
        }
    }
    """
    
    variables = {
        "jql": "project = FRAMED",
        "limit": 1000
    }
    
    try:
        result = client.execute_graphql_query(query, variables)
        
        if result and 'getPreconditions' in result:
            preconditions_data = result['getPreconditions']
            total = preconditions_data.get('total', 0)
            print(f"\nTotal preconditions found in Xray: {total}")
            
            existing_preconditions = {}
            if total > 0:
                for precondition in preconditions_data.get('results', []):
                    issue_id = precondition['issueId']
                    jira_data = precondition.get('jira', {})
                    key = jira_data.get('key', issue_id)
                    summary = jira_data.get('summary', '')
                    labels = jira_data.get('labels', [])
                    definition = precondition.get('definition', '')
                    
                    if summary:
                        existing_preconditions[summary] = {
                            'key': key,
                            'issueId': issue_id,
                            'labels': labels,
                            'definition': definition
                        }
                        print(f"Found: {key} - {summary}")
            
            # Check which of our preconditions already exist
            precondition_mapping = {}
            missing_preconditions = []
            
            print(f"\n=== CHECKING OUR PRECONDITIONS ===")
            for precondition in unique_preconditions:
                # Check for exact match
                if precondition in existing_preconditions:
                    precondition_mapping[precondition] = existing_preconditions[precondition]['key']
                    print(f"✓ EXISTS: \"{precondition}\" -> {existing_preconditions[precondition]['key']}")
                else:
                    # Also check for similar matches (case-insensitive)
                    found = False
                    for existing_summary, existing_data in existing_preconditions.items():
                        if precondition.lower() == existing_summary.lower():
                            precondition_mapping[precondition] = existing_data['key']
                            print(f"✓ EXISTS (case match): \"{precondition}\" -> {existing_data['key']}")
                            found = True
                            break
                    
                    if not found:
                        missing_preconditions.append(precondition)
                        print(f"✗ MISSING: \"{precondition}\"")
            
            # Save results
            results = {
                'existing_preconditions': precondition_mapping,
                'missing_preconditions': missing_preconditions,
                'all_xray_preconditions': existing_preconditions,
                'total_found': len(existing_preconditions),
                'total_missing': len(missing_preconditions)
            }
            
            output_path = Path(__file__).parent.parent / "logs" / "precondition_check_results.json"
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
            
            print(f"\n=== SUMMARY ===")
            print(f"Existing preconditions found: {len(precondition_mapping)}")
            print(f"Missing preconditions to create: {len(missing_preconditions)}")
            print(f"Results saved to: {output_path}")
            
            return results
        else:
            print("No result from GraphQL query")
            return None
            
    except Exception as e:
        print(f"Error checking preconditions: {e}")
        return None

if __name__ == "__main__":
    check_existing_preconditions()