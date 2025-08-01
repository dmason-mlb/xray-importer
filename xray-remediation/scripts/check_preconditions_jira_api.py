#!/usr/bin/env python3
"""
Check for existing preconditions in JIRA/Xray using REST API
"""
import os
import json
import requests
from pathlib import Path
from requests.auth import HTTPBasicAuth

def check_existing_preconditions():
    # JIRA configuration
    jira_domain = os.environ.get('JIRA_DOMAIN', 'https://framed.atlassian.net')
    jira_email = os.environ.get('JIRA_EMAIL')
    jira_api_token = os.environ.get('JIRA_API_TOKEN')
    
    if not jira_email or not jira_api_token:
        print("Error: JIRA_EMAIL and JIRA_API_TOKEN environment variables must be set")
        return None
    
    # Load the precondition analysis
    analysis_path = Path(__file__).parent.parent / "logs" / "precondition_analysis.json"
    with open(analysis_path, 'r') as f:
        analysis_data = json.load(f)
    
    unique_preconditions = analysis_data['unique_preconditions']
    
    print(f"\n=== CHECKING EXISTING PRECONDITIONS IN JIRA ===")
    print(f"Total unique preconditions to check: {len(unique_preconditions)}")
    
    # Search for existing preconditions
    jql = 'project = FRAMED AND issuetype = Precondition'
    
    # JIRA REST API endpoint
    search_url = f"{jira_domain}/rest/api/3/search"
    
    # Request parameters
    params = {
        'jql': jql,
        'fields': 'summary,key,labels',
        'maxResults': 1000
    }
    
    # Make the request
    auth = HTTPBasicAuth(jira_email, jira_api_token)
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(search_url, params=params, auth=auth, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        print(f"\nTotal preconditions found in JIRA: {data.get('total', 0)}")
        
        existing_preconditions = {}
        if data.get('total', 0) > 0:
            for issue in data.get('issues', []):
                summary = issue['fields']['summary']
                key = issue['key']
                labels = issue['fields'].get('labels', [])
                existing_preconditions[summary] = {
                    'key': key,
                    'labels': labels
                }
                print(f"Found: {key} - {summary}")
        
        # Check which of our preconditions already exist
        precondition_mapping = {}
        missing_preconditions = []
        
        print(f"\n=== CHECKING OUR PRECONDITIONS ===")
        for precondition in unique_preconditions:
            if precondition in existing_preconditions:
                precondition_mapping[precondition] = existing_preconditions[precondition]['key']
                print(f"✓ EXISTS: \"{precondition}\" -> {existing_preconditions[precondition]['key']}")
            else:
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
        
    except requests.exceptions.RequestException as e:
        print(f"Error making request to JIRA: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response text: {e.response.text}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

if __name__ == "__main__":
    check_existing_preconditions()