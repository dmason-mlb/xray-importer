#!/usr/bin/env python3
"""
Create missing preconditions in Xray using GraphQL API
"""
import json
import sys
import time
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir / 'xray-api'))
from auth_utils import XrayAPIClient, log_operation

def create_preconditions():
    # Initialize client
    client = XrayAPIClient()
    
    # Load the precondition check results
    results_path = Path(__file__).parent.parent / "logs" / "precondition_check_results.json"
    with open(results_path, 'r') as f:
        check_results = json.load(f)
    
    missing_preconditions = check_results['missing_preconditions']
    
    print(f"\n=== CREATING MISSING PRECONDITIONS IN XRAY ===")
    print(f"Total preconditions to create: {len(missing_preconditions)}")
    
    # GraphQL mutation to create a precondition
    mutation = """
    mutation CreatePrecondition($jira: JSON!, $definition: String) {
        createPrecondition(
            jira: $jira,
            definition: $definition
        ) {
            precondition {
                issueId
                jira(fields: ["key", "summary"])
            }
            warnings
        }
    }
    """
    
    # Project configuration
    project_key = "FRAMED"
    
    created_preconditions = {}
    errors = []
    
    # Create each missing precondition
    for i, precondition_text in enumerate(missing_preconditions, 1):
        print(f"\n[{i}/{len(missing_preconditions)}] Creating: {precondition_text}")
        
        # Prepare JIRA fields
        jira_fields = {
            "fields": {
                "project": {
                    "key": project_key
                },
                "summary": precondition_text,
                "labels": ["functional", "team-page", "automated"]
            }
        }
        
        # Prepare variables
        variables = {
            "jira": jira_fields,
            "definition": precondition_text
        }
        
        try:
            result = client.execute_graphql_query(mutation, variables)
            
            if result and 'createPrecondition' in result:
                precondition_data = result['createPrecondition']['precondition']
                jira_data = precondition_data.get('jira', {})
                key = jira_data.get('key', 'Unknown')
                
                created_preconditions[precondition_text] = {
                    'key': key,
                    'issueId': precondition_data['issueId']
                }
                
                print(f"  ✓ Created: {key}")
                
                # Log the operation
                log_operation("create_precondition", {
                    "precondition": precondition_text,
                    "key": key,
                    "issueId": precondition_data['issueId']
                })
            else:
                print(f"  ✗ Failed to create precondition")
                errors.append({
                    'precondition': precondition_text,
                    'error': 'No result from mutation'
                })
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
            errors.append({
                'precondition': precondition_text,
                'error': str(e)
            })
        
        # Rate limiting - wait between requests
        time.sleep(0.5)
    
    # Save creation results
    creation_results = {
        'timestamp': datetime.now().isoformat(),
        'created_preconditions': created_preconditions,
        'errors': errors,
        'summary': {
            'total_attempted': len(missing_preconditions),
            'successfully_created': len(created_preconditions),
            'failed': len(errors)
        }
    }
    
    output_path = Path(__file__).parent.parent / "logs" / "precondition_creation_results.json"
    with open(output_path, 'w') as f:
        json.dump(creation_results, f, indent=2)
    
    print(f"\n=== SUMMARY ===")
    print(f"Successfully created: {len(created_preconditions)}")
    print(f"Failed: {len(errors)}")
    print(f"Results saved to: {output_path}")
    
    # Update the precondition mapping file for the tests
    if created_preconditions:
        update_precondition_mapping(created_preconditions)
    
    return creation_results

def update_precondition_mapping(created_preconditions):
    """Update the precondition mapping with newly created preconditions"""
    # Load existing check results
    results_path = Path(__file__).parent.parent / "logs" / "precondition_check_results.json"
    with open(results_path, 'r') as f:
        check_results = json.load(f)
    
    # Update with newly created preconditions
    check_results['existing_preconditions'].update(
        {text: data['key'] for text, data in created_preconditions.items()}
    )
    
    # Update missing list
    check_results['missing_preconditions'] = [
        p for p in check_results['missing_preconditions'] 
        if p not in created_preconditions
    ]
    
    # Save updated results
    with open(results_path, 'w') as f:
        json.dump(check_results, f, indent=2)
    
    print(f"\nUpdated precondition mapping file")

if __name__ == "__main__":
    create_preconditions()