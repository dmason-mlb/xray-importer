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
    summary = test_info['summary']
    description = test_info['description']
    precondition = test_info['precondition']
    
    # Default values
    action = "Perform the test action as described"
    result = "Verify the expected behavior occurs"
    
    # Clean up the summary for better parsing
    summary_lower = summary.lower()
    
    # MLB.tv related tests
    if 'mlb.tv' in summary_lower:
        if 'module stops playing after removal' in summary_lower:
            action = "Start playing content in the MLB.tv module, then remove the module from the screen"
            result = "Verify that video playback stops immediately when the module is removed"
        elif 'module should stop playing after removal' in summary_lower:
            action = "Play a video in the MLB.tv module and then navigate away or remove the module"
            result = "Verify that the video stops playing and resources are properly released"
        elif 'live mode fgotd support' in summary_lower:
            action = "Access MLB.tv in Live Mode and navigate to the Free Game of the Day (FGOTD)"
            result = "Verify that FGOTD is properly supported and accessible in Live Mode"
        else:
            action = "Access the MLB.tv module/feature"
            result = "Verify MLB.tv functionality works as expected"
    
    # News related tests
    elif 'news' in summary_lower:
        if 'favorite team news' in summary_lower:
            action = "Navigate to the news section with a favorite team selected"
            result = "Verify that news items related to the user's favorite team are displayed"
        elif 'open a news item' in summary_lower:
            action = "Click/tap on a news item from the news list"
            result = "Verify that the news item opens correctly with full content displayed"
        elif 'latest news as default tab' in summary_lower:
            action = "Navigate to the news section"
            result = "Verify that the 'Latest' tab is selected by default and shows recent news"
        else:
            action = "Access the news section/feature"
            result = "Verify news content is displayed correctly"
    
    # Deep-link tests
    elif 'deep-link' in summary_lower or 'deeplink' in summary_lower:
        if 'scoreboard screen' in summary_lower:
            action = "Open the app using the scoreboard deep-link URL"
            result = "Verify that the app opens directly to the scoreboard screen"
        elif 'watch screen' in summary_lower:
            action = "Open the app using the watch screen deep-link URL"
            result = "Verify that the app opens directly to the watch screen"
        else:
            action = "Open the app using the specified deep-link"
            result = "Verify that the app navigates to the correct screen"
    
    # Main page tests
    elif 'main page' in summary_lower:
        if 'impression tracking' in summary_lower:
            action = "Navigate to the main page and wait for all modules to load"
            result = "Verify that impression tracking events are fired for visible modules"
        else:
            action = "Navigate to the main page"
            result = "Verify the main page loads correctly with all expected components"
    
    # Ticket merchandising
    elif 'ticket' in summary_lower and 'merchandising' in summary_lower:
        action = "Navigate to the surface containing the Ticket Merchandising Module"
        result = "Verify the module displays ticket information and purchase options correctly"
    
    # Surface tests
    elif 'surface' in summary_lower:
        action = "Navigate to the specified surface in the application"
        result = "Verify the surface loads completely with all expected modules and content"
    
    # Login/Authentication tests
    elif 'login' in summary_lower or 'auth' in summary_lower:
        action = "Perform the login/authentication process"
        result = "Verify successful authentication and proper user session establishment"
    
    # Video/Playback tests
    elif 'video' in summary_lower or 'play' in summary_lower or 'player' in summary_lower:
        action = "Interact with video playback functionality"
        result = "Verify video plays correctly with proper controls and behavior"
    
    # Module tests
    elif 'module' in summary_lower:
        if 'remove' in summary_lower or 'removal' in summary_lower:
            action = "Interact with the module and then remove it from the view"
            result = "Verify the module is properly removed and any associated processes are stopped"
        else:
            action = "Access and interact with the specified module"
            result = "Verify the module functions as expected"
    
    # Parse patterns like "Component - Action - Expected"
    if ' - ' in summary:
        parts = summary.split(' - ', 2)
        if len(parts) >= 2:
            component = parts[0].strip()
            if len(parts) == 3:
                action_part = parts[1].strip()
                expected = parts[2].strip()
                action = f"Access {component} and {action_part}"
                result = f"Verify {expected}"
            else:
                behavior = parts[1].strip()
                action = f"Access {component}"
                result = f"Verify {behavior}"
    
    # Use precondition to enhance action if available
    if precondition and 'GIVEN' in precondition:
        given_context = precondition.replace('GIVEN', '').strip()
        if given_context and action == "Perform the test action as described":
            action = f"Set up the test with {given_context}, then perform the test action"
    
    # Use description to enhance if summary was not specific enough
    if description and action == "Perform the test action as described":
        if 'should' in description.lower():
            expected_behavior = description.split('should', 1)[1].strip()
            action = "Execute the test scenario"
            result = f"Verify that {expected_behavior}"
        elif description:
            action = f"Execute: {description[:100]}..." if len(description) > 100 else f"Execute: {description}"
    
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

Please review each test case below and check the box if the proposed test step is approved for submission to XRAY.

- Check the box next to "Approved" if the test step accurately represents the test case
- Leave unchecked if the test step needs revision
- Add comments in JIRA if specific changes are needed

---

## Test Cases

"""
    
    for i, test in enumerate(tests, 1):
        test_info = extract_test_info(test)
        action, result = generate_test_step(test_info)
        
        # Format description - show first 200 chars if too long
        desc_display = test_info['description'] if test_info['description'] else 'No description provided'
        if len(desc_display) > 200:
            desc_display = desc_display[:197] + "..."
        
        markdown_content += f"""### Test {i}: {test_info['key']}

- [ ] **Approved**

**Issue ID:** {test_info['issueId']}  
**JIRA Key:** [{test_info['key']}](https://baseball.atlassian.net/browse/{test_info['key']})  
**Summary:** {test_info['summary']}  
**Description:** {desc_display}  

**Proposed Test Step:**
- **Action:** {action}
- **Expected Result:** {result}

---

"""
    
    # Add summary section at the end
    markdown_content += """## Summary

**Total Tests:** 76  
**Approved:** ___ / 76  
**Pending Review:** ___ / 76  

---

**Next Steps:**
1. Review each test step for accuracy
2. Check boxes for approved steps
3. Submit approved steps to XRAY
4. Create follow-up tasks for steps requiring revision

"""
    
    return markdown_content

if __name__ == "__main__":
    markdown = process_tests()
    with open('xray_test_steps_review.md', 'w') as f:
        f.write(markdown)
    print("Enhanced markdown document created successfully as 'xray_test_steps_review.md'!")