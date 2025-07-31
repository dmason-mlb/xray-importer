#!/usr/bin/env python3
"""
Script to combine all four response JSON files into a single file.
"""

import json
import os

def combine_json_files():
    """Combine response1.json through response4.json into a single file."""
    
    # Initialize the combined structure
    combined_data = {
        "data": {
            "getExpandedTests": {
                "total": 0,
                "results": []
            }
        }
    }
    
    # Track unique tests by issueId
    seen_issue_ids = set()
    
    # Process each response file
    for i in range(1, 5):
        filename = f"response{i}.json"
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                
            # Extract results from this file
            if "data" in data and "getExpandedTests" in data["data"]:
                results = data["data"]["getExpandedTests"].get("results", [])
                
                # Add only unique tests
                unique_count = 0
                for test in results:
                    issue_id = test.get("issueId")
                    if issue_id and issue_id not in seen_issue_ids:
                        seen_issue_ids.add(issue_id)
                        combined_data["data"]["getExpandedTests"]["results"].append(test)
                        unique_count += 1
                
                print(f"✓ Processed {filename}: {len(results)} tests ({unique_count} unique)")
        
        except Exception as e:
            print(f"✗ Error processing {filename}: {e}")
    
    # Update the total count
    total_tests = len(combined_data["data"]["getExpandedTests"]["results"])
    combined_data["data"]["getExpandedTests"]["total"] = total_tests
    
    # Save the combined file
    output_path = os.path.join(os.path.dirname(__file__), "combined_responses.json")
    with open(output_path, 'w') as f:
        json.dump(combined_data, f, indent=2)
    
    print(f"\n✓ Combined file saved: combined_responses.json")
    print(f"  Total tests: {total_tests}")

if __name__ == "__main__":
    combine_json_files()