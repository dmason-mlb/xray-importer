import json
import re

def extract_test_info(test):
    """Extract relevant information from a test item"""
    issue_id = test.get('issueId', '')
    jira_info = test.get('jira', {})
    key = jira_info.get('key', '')
    summary = jira_info.get('summary', '')
    description = jira_info.get('description', '') or ''
    
    # Get preconditions if available
    preconditions = test.get('preconditions', {}).get('results', [])
    precondition_text = ''
    if preconditions:
        precondition_text = preconditions[0].get('definition', '')
    
    return {
        'issueId': issue_id,
        'key': key,
        'summary': summary,
        'description': description,
        'precondition': precondition_text
    }

def generate_test_step(test_info):
    """Generate Action and Result based on test information"""
    summary = test_info['summary'].lower()
    description = test_info['description'].lower()
    precondition = test_info['precondition'].lower()
    
    # Combine all available text for analysis
    combined_text = f"{summary} {description} {precondition}"
    
    # Default values
    action = "Perform the test action as described"
    result = "Verify the expected behavior occurs"
    
    # Pattern matching for common test scenarios
    if 'impression tracking' in combined_text:
        action = "Navigate to the specified surface/module and ensure it loads completely"
        result = "Verify that impression tracking events are fired and logged correctly"
    elif 'stops playing' in combined_text:
        action = "Start playing content in the module, then remove or navigate away from the module"
        result = "Verify that playback stops immediately when the module is removed"
    elif 'click' in combined_text or 'tap' in combined_text:
        action = "Click/tap on the specified element or button"
        result = "Verify the expected navigation or action occurs"
    elif 'display' in combined_text or 'show' in combined_text:
        action = "Navigate to the specified screen or component"
        result = "Verify that all expected elements are displayed correctly"
    elif 'load' in combined_text:
        action = "Access the specified page or component"
        result = "Verify that the content loads successfully without errors"
    elif 'error' in combined_text:
        action = "Trigger the error condition as described"
        result = "Verify that the appropriate error message or handling occurs"
    elif 'login' in combined_text or 'authentication' in combined_text:
        action = "Perform the login/authentication flow"
        result = "Verify successful authentication and proper user state"
    elif 'navigation' in combined_text:
        action = "Navigate through the specified flow or screens"
        result = "Verify correct navigation behavior and screen transitions"
    elif 'video' in combined_text or 'play' in combined_text:
        action = "Interact with the video player or playback controls"
        result = "Verify video playback functions correctly"
    elif 'ticket' in combined_text and 'merchandising' in combined_text:
        action = "Access the ticket merchandising module on the specified surface"
        result = "Verify the module displays ticket information and purchase options correctly"
    elif 'mlb.tv' in combined_text:
        action = "Access or interact with the MLB.tv feature/module"
        result = "Verify MLB.tv functionality works as expected"
    elif 'surface' in combined_text:
        action = "Navigate to the specified surface within the application"
        result = "Verify the surface loads with all expected components"
    elif 'module' in combined_text:
        action = "Interact with the specified module"
        result = "Verify the module behavior matches expectations"
    
    # More specific parsing based on summary patterns
    if test_info['summary']:
        # Extract specific actions from summary
        if ' - ' in test_info['summary']:
            parts = test_info['summary'].split(' - ')
            if len(parts) >= 2:
                context = parts[0].strip()
                behavior = parts[1].strip()
                action = f"Access {context}"
                result = f"Verify {behavior}"
    
    return action, result

def process_tests():
    """Process all tests and generate markdown content"""
    with open('mlbmob/extra-info-response.json', 'r') as f:
        data = json.load(f)
    
    tests = data['data']['getExpandedTests']['results']
    
    markdown_content = """# XRAY Test Steps Review Document

**Date:** 2025-07-07  
**Total Tests:** 76  
**Purpose:** Review and approve proposed test steps for XRAY test cases

---

## Instructions

Please review each test case below and check the box if the proposed test step is approved for submission.

---

## Test Cases

"""
    
    for i, test in enumerate(tests, 1):
        test_info = extract_test_info(test)
        action, result = generate_test_step(test_info)
        
        markdown_content += f"""### Test {i}: {test_info['key']}

- [ ] **Approved**

**Issue ID:** {test_info['issueId']}  
**JIRA Key:** {test_info['key']}  
**Summary:** {test_info['summary']}  
**Description:** {test_info['description'] if test_info['description'] else 'No description provided'}  

**Proposed Test Step:**
- **Action:** {action}
- **Result:** {result}

---

"""
    
    return markdown_content

if __name__ == "__main__":
    markdown = process_tests()
    with open('test_steps_review.md', 'w') as f:
        f.write(markdown)
    print("Markdown document created successfully!")