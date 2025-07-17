#!/usr/bin/env python3
"""
Extract functional test cases from Confluence doc 4904976484 and convert to Xray JSON format.
"""

import os
import sys
import json
import re
from pathlib import Path

# Add confluence-tool scripts to path
sys.path.append('/Users/douglas.mason/Documents/GitHub/confluence-tool/scripts')

from confluence_client import ConfluenceClient
from config import get_config

def extract_test_cases_from_content(content):
    """Extract individual functional test cases from Confluence content."""
    test_cases = []
    
    # Find all functional test case sections - they start with TC-xxx headings
    test_pattern = r'<h3[^>]*>.*?(TC-[^<]+).*?</h3>(.*?)(?=<h3[^>]*>.*?TC-|$)'
    matches = re.findall(test_pattern, content, re.DOTALL)
    
    for match in matches:
        test_id = match[0].strip()
        test_content = match[1].strip()
        
        # Extract test summary from the content
        summary_match = re.search(r'<p><strong>Test Name:</strong>\s*(.*?)</p>', test_content, re.DOTALL)
        if not summary_match:
            summary_match = re.search(r'<p><strong>Summary:</strong>\s*(.*?)</p>', test_content, re.DOTALL)
        summary = summary_match.group(1).strip() if summary_match else f"Functional test {test_id}"
        # Clean up HTML tags from summary
        summary = re.sub(r'<[^>]+>', '', summary).strip()
        
        # Extract description
        desc_match = re.search(r'<p><strong>Description:</strong>\s*(.*?)</p>', test_content, re.DOTALL)
        if not desc_match:
            desc_match = re.search(r'<p><strong>Objective:</strong>\s*(.*?)</p>', test_content, re.DOTALL)
        description = desc_match.group(1).strip() if desc_match else ""
        
        # Extract test steps
        steps = []
        steps_match = re.search(r'<p><strong>Test Steps:</strong></p>(.*?)(?=<p><strong>|$)', test_content, re.DOTALL)
        if not steps_match:
            steps_match = re.search(r'<p><strong>Steps:</strong></p>(.*?)(?=<p><strong>|$)', test_content, re.DOTALL)
        if steps_match:
            steps_content = steps_match.group(1)
            # Extract ordered list items
            step_items = re.findall(r'<li>(.*?)</li>', steps_content, re.DOTALL)
            for i, step_content in enumerate(step_items, 1):
                step_clean = re.sub(r'<[^>]+>', '', step_content).strip()
                steps.append({
                    "index": i,
                    "action": step_clean,
                    "data": "",
                    "result": ""
                })
        
        # Extract expected results
        expected_match = re.search(r'<p><strong>Expected Results:</strong></p>(.*?)(?=<p><strong>|$)', test_content, re.DOTALL)
        if not expected_match:
            expected_match = re.search(r'<p><strong>Expected Result:</strong></p>(.*?)(?=<p><strong>|$)', test_content, re.DOTALL)
        expected_results = ""
        if expected_match:
            expected_content = expected_match.group(1)
            # Extract list items
            result_items = re.findall(r'<li>(.*?)</li>', expected_content, re.DOTALL)
            if result_items:
                expected_results = "\n".join([re.sub(r'<[^>]+>', '', item).strip() for item in result_items])
            else:
                expected_results = re.sub(r'<[^>]+>', '', expected_content).strip()
        
        # Extract preconditions
        preconditions = []
        precond_match = re.search(r'<p><strong>Preconditions:</strong></p>(.*?)(?=<p><strong>|$)', test_content, re.DOTALL)
        if not precond_match:
            precond_match = re.search(r'<p><strong>Prerequisites:</strong></p>(.*?)(?=<p><strong>|$)', test_content, re.DOTALL)
        if precond_match:
            precond_content = precond_match.group(1)
            precond_items = re.findall(r'<li>(.*?)</li>', precond_content, re.DOTALL)
            for item in precond_items:
                precond_clean = re.sub(r'<[^>]+>', '', item).strip()
                preconditions.append(precond_clean)
        
        # Determine priority and labels from test_id and content
        priority = "Medium"
        labels = ["functional", "team_page", "manual"]
        
        # Add specific labels based on test ID patterns or content
        if "navigation" in test_id.lower() or "navigation" in summary.lower():
            labels.extend(["navigation", "high"])
            priority = "High"
        elif "ui" in test_id.lower() or "display" in summary.lower():
            labels.extend(["ui", "medium"])
        elif "data" in test_id.lower() or "content" in summary.lower():
            labels.extend(["data_validation", "medium"])
        elif "error" in test_id.lower() or "error" in summary.lower():
            labels.extend(["error_handling", "medium"])
        elif "performance" in test_id.lower() or "performance" in summary.lower():
            labels.extend(["performance", "high"])
            priority = "High"
        elif "accessibility" in test_id.lower() or "accessibility" in summary.lower():
            labels.extend(["accessibility", "medium"])
        elif "responsive" in test_id.lower() or "responsive" in summary.lower():
            labels.extend(["responsive", "medium"])
        
        # Add test ID as label
        labels.append(test_id)
        
        test_case = {
            "testInfo": {
                "summary": summary,
                "description": description,
                "labels": labels,
                "priority": priority,
                "testType": "Manual",
                "steps": steps,
                "expectedResults": expected_results,
                "preconditions": preconditions
            },
            "testId": test_id
        }
        
        test_cases.append(test_case)
    
    return test_cases

def main():
    """Extract functional test cases from Confluence and create Xray JSON."""
    config = get_config()
    if not config:
        sys.exit(1)
    
    client = ConfluenceClient(config['domain'], config['email'], config['api_token'])
    page_id = "4904976484"
    
    print(f"Fetching Confluence page {page_id}...")
    
    try:
        page = client.get_page(page_id, expand=['body.storage'])
        content = page['body']['storage']['value']
        
        print(f"Page title: {page['title']}")
        print(f"Page version: {page['version']['number']}")
        
        # Extract test cases
        print("Extracting test cases...")
        test_cases = extract_test_cases_from_content(content)
        
        print(f"Found {len(test_cases)} test cases")
        
        # Create Xray JSON structure
        xray_data = {
            "info": {
                "project": "FRAMED",
                "summary": "Functional Test Cases - Team Page",
                "description": "Manual functional test cases for Team Page UI and user interactions extracted from Confluence",
                "user": config['email'],
                "revision": str(page['version']['number']),
                "startDate": "2025-07-17T00:00:00Z",
                "finishDate": "2025-07-17T23:59:59Z",
                "testPlanKey": ""
            },
            "tests": test_cases
        }
        
        # Save to file
        output_file = Path(__file__).parent / "functional_tests_xray.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(xray_data, f, indent=2, ensure_ascii=False)
        
        print(f"Created Xray JSON file: {output_file}")
        print(f"Contains {len(test_cases)} functional test cases")
        
        # Print summary
        print("\nTest Case Summary:")
        for i, test in enumerate(test_cases, 1):
            print(f"{i:2d}. {test['testId']}: {test['testInfo']['summary']}")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()