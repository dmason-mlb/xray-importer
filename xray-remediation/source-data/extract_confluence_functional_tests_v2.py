#!/usr/bin/env python3
"""
Extract functional test cases from Confluence doc 4904976484 (table format) and convert to Xray JSON format.
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
    """Extract individual functional test cases from Confluence content (table format)."""
    test_cases = []
    
    # Find all functional test case sections - they start with TC-xxx headings followed by tables
    test_pattern = r'<h3[^>]*>.*?(TC-[^<]+).*?</h3>\s*<table[^>]*>(.*?)</table>'
    matches = re.findall(test_pattern, content, re.DOTALL)
    
    for match in matches:
        test_id = match[0].strip()
        table_content = match[1].strip()
        
        # Extract data from table rows
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_content, re.DOTALL)
        
        # Parse table data
        test_data = {}
        for row in rows:
            cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
            if len(cells) >= 2:
                key = re.sub(r'<[^>]+>', '', cells[0]).strip().replace('*', '')
                value = cells[1].strip()
                test_data[key] = value
        
        # Extract values from test_data
        summary = test_data.get('Test Case ID', f'Functional test {test_id}')
        priority = test_data.get('Priority', 'Medium')
        platforms = test_data.get('Platforms', 'iOS, Android')
        folder_structure = test_data.get('Folder Structure', 'Team Page/General')
        tags = test_data.get('Tag(s)', '@team-page, @functional')
        preconditions = test_data.get('Preconditions', '')
        test_steps = test_data.get('Test Steps', '')
        expected_result = test_data.get('Expected Result', '')
        test_data_field = test_data.get('Test Data', '')
        related_issues = test_data.get('Related Issue', test_data.get('Related Issues', ''))
        
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
        test_steps = clean_html(test_steps)
        expected_result = clean_html(expected_result)
        preconditions = clean_html(preconditions)
        
        # Parse test steps into structured format
        steps = []
        if test_steps:
            # Split by "Step X:" pattern
            step_parts = re.split(r'Step \d+:', test_steps)
            for i, step_part in enumerate(step_parts[1:], 1):  # Skip first empty part
                step_clean = step_part.strip()
                if step_clean:
                    # Split by arrow to separate action from expected result
                    parts = step_clean.split('→')
                    action = parts[0].strip()
                    result = ' → '.join(parts[1:]).strip() if len(parts) > 1 else ''
                    
                    steps.append({
                        "index": i,
                        "action": action,
                        "data": "",
                        "result": result
                    })
        
        # Parse tags to determine labels
        labels = ["functional", "team_page", "manual"]
        if tags:
            tag_parts = [tag.strip().replace('@', '') for tag in tags.split(',')]
            labels.extend(tag_parts)
        
        # Add platform labels
        if 'iOS' in platforms:
            labels.append('ios')
        if 'Android' in platforms:
            labels.append('android')
        
        # Add priority label
        if priority:
            labels.append(priority.lower())
        
        # Add test ID as label
        labels.append(test_id)
        
        # Clean up labels (remove duplicates and empty strings)
        labels = list(set([label for label in labels if label]))
        
        # Create description from folder structure and summary
        description = f"Folder: {folder_structure}\nPlatforms: {platforms}"
        if test_data_field:
            description += f"\nTest Data: {clean_html(test_data_field)}"
        if related_issues:
            description += f"\nRelated Issues: {clean_html(related_issues)}"
        
        # Create preconditions list
        preconditions_list = []
        if preconditions:
            preconditions_list.append(preconditions)
        
        test_case = {
            "testInfo": {
                "summary": summary,
                "description": description,
                "labels": labels,
                "priority": priority,
                "testType": "Manual",
                "steps": steps,
                "expectedResults": expected_result,
                "preconditions": preconditions_list
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