#!/usr/bin/env python3
"""
Extract API test cases from Confluence doc 4904878140 and convert to Xray JSON format.
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
    """Extract individual test cases from Confluence content."""
    test_cases = []
    
    # Find all API test case sections - they can be in H3 or H4 headings
    # Look for both H3 and H4 patterns since the debug showed tests in both levels
    h3_pattern = r'<h3[^>]*>.*?(API-[^<\s]+).*?</h3>(.*?)(?=<h[34][^>]*>.*?API-|$)'
    h4_pattern = r'<h4[^>]*>.*?(API-[^<\s]+).*?</h4>(.*?)(?=<h[34][^>]*>.*?API-|$)'
    
    h3_matches = re.findall(h3_pattern, content, re.DOTALL)
    h4_matches = re.findall(h4_pattern, content, re.DOTALL)
    
    # Combine both sets of matches
    matches = h3_matches + h4_matches
    
    for match in matches:
        test_id = match[0].strip().rstrip(':')  # Remove trailing colons
        test_content = match[1].strip()
        
        # Extract test data from table if present (similar to functional tests)
        test_data = {}
        table_match = re.search(r'<table[^>]*>(.*?)</table>', test_content, re.DOTALL)
        if table_match:
            table_content = table_match.group(1)
            rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_content, re.DOTALL)
            for row in rows:
                cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
                if len(cells) >= 2:
                    key = re.sub(r'<[^>]+>', '', cells[0]).strip().replace('*', '')
                    value = cells[1].strip()
                    test_data[key] = value
        
        # Extract test information from table data or fallback to basic extraction
        summary = test_data.get('Test Case ID', f"Test case {test_id}")
        if summary == test_id or not summary.strip():
            # Try to extract a better summary from the heading in the content or previous context
            heading_pattern = rf'{re.escape(test_id)}:\s*(.*?)(?:</h[34]>|$)'
            heading_match = re.search(heading_pattern, test_content, re.DOTALL)
            if heading_match:
                heading_text = re.sub(r'<[^>]+>', '', heading_match.group(1)).strip()
                summary = f"Test case {test_id}: {heading_text}"
            else:
                summary = f"Test case {test_id}"
        
        endpoint = test_data.get('Endpoint', '')
        priority = test_data.get('Priority', 'Medium')
        platforms = test_data.get('Platform/Platforms', 'iOS, Android')
        tags = test_data.get('Tag(s)', '@api @team-page')
        preconditions_text = test_data.get('Preconditions', test_data.get('Precondition', ''))
        request_info = test_data.get('Request', '')
        headers = test_data.get('Headers', '')
        expected_response = test_data.get('Expected Response', '')
        validations = test_data.get('Validations', '')
        
        # Clean HTML tags from all fields
        def clean_html(text):
            if not text:
                return ""
            # Convert <br> to newlines
            text = re.sub(r'<br\s*/?>', '\n', text)
            # Remove all other HTML tags
            text = re.sub(r'<[^>]+>', '', text)
            # Clean up whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            return text
        
        summary = clean_html(summary)
        endpoint = clean_html(endpoint)
        request_info = clean_html(request_info)
        headers = clean_html(headers)
        expected_response = clean_html(expected_response)
        validations = clean_html(validations)
        preconditions_text = clean_html(preconditions_text)
        
        # Create description from available data
        description = ""
        if endpoint:
            description += f"Endpoint: {endpoint}\n"
        if request_info:
            description += f"Request: {request_info}\n"
        if headers:
            description += f"Headers: {headers}\n"
        if platforms:
            description += f"Platforms: {platforms}\n"
        
        # Parse steps from validations or expected response
        steps = []
        if validations:
            validation_items = re.split(r'\n|•|-', validations)
            for i, item in enumerate(validation_items, 1):
                item = item.strip()
                if item:
                    steps.append({
                        "index": i,
                        "action": f"Validate: {item}",
                        "data": "",
                        "result": ""
                    })
        
        # Use expected response as expected results
        expected_results = expected_response if expected_response else validations
        
        # Parse preconditions
        preconditions = []
        if preconditions_text:
            precond_items = re.split(r'\n|•|-', preconditions_text)
            for item in precond_items:
                item = item.strip()
                if item:
                    preconditions.append(item)
        
        # Determine priority and labels from test_id
        priority = "Medium"
        labels = ["api", "team_page", "cross_platform"]
        
        # Add specific labels based on test ID patterns
        if "REG" in test_id:
            labels.extend(["regression", "high"])
            priority = "High"
        elif "PERF" in test_id:
            labels.extend(["performance", "high"])
            priority = "High"
        elif "SEC" in test_id:
            labels.extend(["security", "high"])
            priority = "High"
        elif "ERR" in test_id:
            labels.extend(["error_handling", "medium"])
        elif "DATA" in test_id:
            labels.extend(["data_validation", "medium"])
        elif "INT" in test_id:
            labels.extend(["integration", "high"])
            priority = "High"
        elif "GS" in test_id:
            labels.extend(["game_state", "high"])
            priority = "High"
        elif "JE" in test_id:
            labels.extend(["jewel_event", "high"])
            priority = "High"
        
        # Add test ID as label (clean version)
        labels.append(test_id)
        
        test_case = {
            "testInfo": {
                "summary": summary,
                "description": description,
                "labels": labels,
                "priority": priority,
                "testType": "Generic",
                "steps": steps,
                "expectedResults": expected_results,
                "preconditions": preconditions
            },
            "testId": test_id
        }
        
        test_cases.append(test_case)
    
    # Remove duplicates based on test ID
    unique_test_cases = []
    seen_ids = set()
    for test_case in test_cases:
        test_id = test_case['testId']
        if test_id not in seen_ids:
            seen_ids.add(test_id)
            unique_test_cases.append(test_case)
    
    return unique_test_cases

def main():
    """Extract API test cases from Confluence and create Xray JSON."""
    config = get_config()
    if not config:
        sys.exit(1)
    
    client = ConfluenceClient(config['domain'], config['email'], config['api_token'])
    page_id = "4904878140"
    
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
                "summary": "API Test Cases - Team Page",
                "description": "Automated API test cases for Team Page service endpoints extracted from Confluence",
                "user": config['email'],
                "revision": str(page['version']['number']),
                "startDate": "2025-07-17T00:00:00Z",
                "finishDate": "2025-07-17T23:59:59Z",
                "testPlanKey": ""
            },
            "tests": test_cases
        }
        
        # Save to file
        output_file = Path(__file__).parent / "api_tests_xray.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(xray_data, f, indent=2, ensure_ascii=False)
        
        print(f"Created Xray JSON file: {output_file}")
        print(f"Contains {len(test_cases)} API test cases")
        
        # Print summary
        print("\nTest Case Summary:")
        for i, test in enumerate(test_cases, 1):
            print(f"{i:2d}. {test['testId']}: {test['testInfo']['summary']}")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()