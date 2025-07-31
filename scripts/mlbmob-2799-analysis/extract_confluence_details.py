#!/usr/bin/env python3
"""
Extract detailed test information from Confluence document 4932862074
for the 12 test cases missing steps in MLBMOB-2799
"""

import json
import re
import os
from datetime import datetime

# List of test cases we need to find
TARGET_TESTS = [
    "MLBMOB-1567", "MLBMOB-1566", "MLBMOB-1565", "MLBMOB-1564",
    "MLBMOB-1563", "MLBMOB-1562", "MLBMOB-1560", "MLBMOB-1609",
    "MLBMOB-1622", "MLBMOB-1790", "MLBMOB-1789", "MLBMOB-1761"
]

def search_confluence_for_tests():
    """Search Confluence document for detailed test information"""
    try:
        # Import confluence search capability
        from mcp_client import confluence_search
        
        detailed_tests = {}
        
        for test_key in TARGET_TESTS:
            print(f"Searching for {test_key}...")
            
            # Search for the specific test
            results = confluence_search(f'"{test_key}"', limit=5)
            
            if results:
                for result in results:
                    if result['id'] == '4932862074':  # Our target document
                        content = result['content']['value']
                        
                        # Extract test information
                        test_info = extract_test_details(content, test_key)
                        if test_info:
                            detailed_tests[test_key] = test_info
                            print(f"✓ Found details for {test_key}")
                        break
            else:
                print(f"✗ No results found for {test_key}")
        
        return detailed_tests
        
    except Exception as e:
        print(f"Error searching Confluence: {e}")
        return {}

def extract_test_details(content, test_key):
    """Extract detailed test information from Confluence content"""
    try:
        # Look for test sections in the content
        test_pattern = rf"Test \d+: {re.escape(test_key)}.*?(?=Test \d+:|$)"
        match = re.search(test_pattern, content, re.DOTALL | re.IGNORECASE)
        
        if match:
            test_section = match.group(0)
            
            # Extract different components
            issue_id = extract_field(test_section, "Issue ID")
            summary = extract_field(test_section, "Summary")
            description = extract_field(test_section, "Description")
            
            # Extract enhanced test steps
            actions = extract_actions(test_section)
            expected_results = extract_expected_results(test_section)
            
            return {
                'key': test_key,
                'issue_id': issue_id,
                'summary': summary,
                'description': description,
                'actions': actions,
                'expected_results': expected_results,
                'full_section': test_section
            }
    
    except Exception as e:
        print(f"Error extracting details for {test_key}: {e}")
    
    return None

def extract_field(content, field_name):
    """Extract a specific field from content"""
    pattern = rf"{field_name}:\s*(.+?)(?=\n|$)"
    match = re.search(pattern, content, re.IGNORECASE)
    return match.group(1).strip() if match else None

def extract_actions(content):
    """Extract action steps from content"""
    actions = []
    
    # Look for numbered actions
    action_pattern = r"(\d+\.\s*.+?)(?=\n\d+\.|Expected Result|$)"
    matches = re.findall(action_pattern, content, re.DOTALL | re.IGNORECASE)
    
    for match in matches:
        action = match.strip()
        if action and not action.lower().startswith('expected'):
            actions.append(action)
    
    return actions

def extract_expected_results(content):
    """Extract expected results from content"""
    results = []
    
    # Look for expected results section
    results_pattern = r"Expected Result[s]?:?\s*(.+?)(?=Test \d+:|Action|$)"
    match = re.search(results_pattern, content, re.DOTALL | re.IGNORECASE)
    
    if match:
        results_text = match.group(1).strip()
        
        # Split by bullet points or numbers
        bullet_pattern = r"[•\-\*]\s*(.+?)(?=[•\-\*]|$)"
        bullets = re.findall(bullet_pattern, results_text, re.DOTALL)
        
        if bullets:
            results = [bullet.strip() for bullet in bullets]
        else:
            # If no bullets, try numbered list
            numbered_pattern = r"\d+\.\s*(.+?)(?=\n\d+\.|$)"
            numbered = re.findall(numbered_pattern, results_text, re.DOTALL)
            if numbered:
                results = [num.strip() for num in numbered]
            else:
                results = [results_text]
    
    return results

def create_enhanced_markdown():
    """Create enhanced markdown with all available details"""
    
    print("Creating enhanced markdown with Confluence details...")
    
    # For now, create a template that can be manually populated
    # since we can't directly access the MCP client here
    
    template = """# Enhanced Test Details from Confluence

**Source:** [MLBMOB XRAY - Test Steps Review and Approval](https://baseball.atlassian.net/wiki/spaces/MLBMOB/pages/4932862074)

## Instructions for Manual Enhancement

To complete this document with full test details:

1. Open the Confluence document: https://baseball.atlassian.net/wiki/spaces/MLBMOB/pages/4932862074
2. Search for each test case using Ctrl+F
3. Copy the "Enhanced Test Step" sections for each test
4. Update the placeholders below with the full details

---

## Test Cases with Placeholder Details

"""
    
    for i, test_key in enumerate(TARGET_TESTS, 1):
        # Get basic info we already have
        basic_info = get_basic_test_info(test_key)
        
        template += f"""
### {i}. [{test_key}](https://mlbam.atlassian.net/browse/{test_key}) - {basic_info['summary']}

**Issue ID:** {basic_info['issue_id']}  
**Summary:** {basic_info['summary']}  
**Status:** To Do  
**Type:** Manual  

**Actions:**
```
[TO BE POPULATED FROM CONFLUENCE]
Search for "Test {basic_info['test_number']}: {test_key}" in Confluence document
Copy the "Enhanced Test Step" -> "Action" section
```

**Expected Results:**
```
[TO BE POPULATED FROM CONFLUENCE]
Copy the "Enhanced Test Step" -> "Expected Result" section
```

**Confluence Reference:** Test {basic_info['test_number']}: {test_key}

---
"""
    
    # Save the template
    with open('enhanced_test_details_template.md', 'w') as f:
        f.write(template)
    
    print("✓ Enhanced template created: enhanced_test_details_template.md")
    print("✓ Manual population required from Confluence document")

def get_basic_test_info(test_key):
    """Get basic test information we already have"""
    test_info = {
        'MLBMOB-1567': {'summary': 'Exec Users', 'issue_id': '1132046', 'test_number': '19'},
        'MLBMOB-1566': {'summary': 'Anon Users', 'issue_id': '1132045', 'test_number': '20'},
        'MLBMOB-1565': {'summary': 'TV Yearly', 'issue_id': '1132044', 'test_number': '21'},
        'MLBMOB-1564': {'summary': 'TV Monthly', 'issue_id': '1132043', 'test_number': '22'},
        'MLBMOB-1563': {'summary': 'Single-Team Users', 'issue_id': '1132042', 'test_number': '23'},
        'MLBMOB-1562': {'summary': 'Free Users', 'issue_id': '1132041', 'test_number': '24'},
        'MLBMOB-1560': {'summary': 'Entitled', 'issue_id': 'TBD', 'test_number': '25'},
        'MLBMOB-1609': {'summary': 'All-Star Game', 'issue_id': '1132104', 'test_number': '18'},
        'MLBMOB-1622': {'summary': 'Picture-In-Picture', 'issue_id': '1132127', 'test_number': '17'},
        'MLBMOB-1790': {'summary': 'Live Game Launch', 'issue_id': '1132305', 'test_number': '14'},
        'MLBMOB-1789': {'summary': 'Archive Launch', 'issue_id': '1132304', 'test_number': '15'},
        'MLBMOB-1761': {'summary': 'Day without Games', 'issue_id': '1132275', 'test_number': '16'}
    }
    
    return test_info.get(test_key, {'summary': 'Unknown', 'issue_id': 'TBD', 'test_number': 'TBD'})

def main():
    """Main function to extract and process test details"""
    print("MLBMOB-2799 Test Details Extraction")
    print("=" * 50)
    
    print(f"Target tests: {len(TARGET_TESTS)}")
    for test in TARGET_TESTS:
        print(f"- {test}")
    
    print("\n" + "=" * 50)
    
    # Create enhanced markdown template
    create_enhanced_markdown()
    
    print("\n" + "=" * 50)
    print("EXTRACTION COMPLETE")
    print("=" * 50)
    print("Files created:")
    print("- enhanced_test_details_template.md")
    print("\nNext steps:")
    print("1. Open the Confluence document")
    print("2. Search for each test case")
    print("3. Copy the Enhanced Test Step details")
    print("4. Update the template with full details")

if __name__ == "__main__":
    main()