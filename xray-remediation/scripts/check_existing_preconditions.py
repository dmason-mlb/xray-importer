#!/usr/bin/env python3
"""
Check for existing preconditions in Xray
This script will be called by the MCP tool orchestrator
"""
import json
from pathlib import Path

def prepare_precondition_check():
    # Load the precondition analysis
    analysis_path = Path(__file__).parent.parent / "logs" / "precondition_analysis.json"
    with open(analysis_path, 'r') as f:
        analysis_data = json.load(f)
    
    unique_preconditions = analysis_data['unique_preconditions']
    
    print(f"\n=== PREPARING TO CHECK EXISTING PRECONDITIONS ===")
    print(f"Total unique preconditions to check: {len(unique_preconditions)}")
    
    # Prepare data for MCP query
    check_data = {
        'unique_preconditions': unique_preconditions,
        'jql': 'project = FRAMED AND issuetype = Precondition',
        'fields_needed': ['summary', 'key', 'labels']
    }
    
    output_path = Path(__file__).parent.parent / "logs" / "precondition_check_prep.json"
    with open(output_path, 'w') as f:
        json.dump(check_data, f, indent=2)
    
    print(f"\nPrepared data for MCP query saved to: {output_path}")
    print("\nUnique preconditions to check:")
    for idx, precondition in enumerate(unique_preconditions, 1):
        print(f"{idx}. {precondition}")
    
    return check_data

if __name__ == "__main__":
    prepare_precondition_check()