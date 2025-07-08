#!/usr/bin/env python3
"""
Update Confluence page to properly map expected results to test steps
"""

import os
import requests
import json
import re
from typing import Dict, List, Tuple

# Get credentials from environment
JIRA_BASE_URL = os.getenv('JIRA_BASE_URL')
JIRA_EMAIL = os.getenv('JIRA_EMAIL')
ATLASSIAN_TOKEN = os.getenv('ATLASSIAN_TOKEN')

# Page ID
PAGE_ID = "4904976484"
CONFLUENCE_API = f"{JIRA_BASE_URL}/wiki/rest/api/content/{PAGE_ID}"

def get_page_content():
    """Get current page content"""
    headers = {
        'Accept': 'application/json'
    }
    
    auth = (JIRA_EMAIL, ATLASSIAN_TOKEN)
    
    response = requests.get(
        f"{CONFLUENCE_API}?expand=body.storage,version",
        headers=headers,
        auth=auth
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get page: {response.status_code}")
        return None

def parse_test_case(test_html: str) -> Dict:
    """Parse a test case from HTML table"""
    # Extract test steps
    steps_match = re.search(r'<strong>Test Steps</strong></td><td>(.*?)</td>', test_html, re.DOTALL)
    if steps_match:
        steps_html = steps_match.group(1)
        # Split by <br/> and clean
        steps = [s.strip() for s in re.split(r'<br\s*/?>', steps_html) if s.strip()]
        # Remove step numbers
        steps = [re.sub(r'^\d+\.\s*', '', step) for step in steps]
    else:
        steps = []
    
    # Extract expected results
    results_match = re.search(r'<strong>Expected Result</strong></td><td>(.*?)</td>', test_html, re.DOTALL)
    if results_match:
        results_html = results_match.group(1)
        # Split by bullet points
        results = re.findall(r'•\s*(.*?)(?=<br/>|$)', results_html)
        results = [r.strip() for r in results if r.strip()]
    else:
        results = []
    
    return {
        'steps': steps,
        'results': results
    }

def map_results_to_steps(test_case: Dict) -> Dict[str, List[Tuple[str, List[str]]]]:
    """Map expected results to their corresponding steps"""
    # Manual mapping based on test case analysis
    test_mappings = {
        'TC-001': [
            ('Navigate to Team Page', []),
            ('Tap on the team selector dropdown', ['Team drawer opens smoothly', 'All 30 MLB teams are displayed']),
            ('Select a different team from the list', ['Selected team\'s page loads with correct content', 'Team name updates in the header'])
        ],
        'TC-002': [
            ('Select Arizona Diamondbacks from team selector', ['Team name displays correctly without cutoff', 'Dropdown arrow remains visible'])
        ],
        'TC-003': [
            ('Navigate to team with live game', []),
            ('Observe MIG section', ['Live game card displays current score', 'Game status shows "LIVE"']),
            ('Check game score updates', ['Score updates in real-time']),
            ('Verify broadcast information', ['Broadcast details are visible'])
        ],
        'TC-004': [
            ('View MIG section', []),
            ('Swipe left/right on calendar bar', ['Calendar scrolls smoothly']),
            ('Tap on different game dates', ['Selected date highlights', 'Game card updates to show selected game'])
        ],
        'TC-005': [
            ('Navigate to team page during HRD period', []),
            ('Check MIG section', ['HRD displays with "HRD" text and start time', 'HRD logo shows when active', 'Where to watch details visible'])
        ],
        'TC-006': [
            ('Scroll to Top Stories section', []),
            ('Swipe through articles', ['Carousel scrolls smoothly']),
            ('Tap on an article', ['Article opens correctly', 'Images load properly'])
        ],
        'TC-007': [
            ('Scroll to video carousel', []),
            ('Tap on a video', ['Video player opens']),
            ('Verify playback controls', ['Playback starts (if autoplay enabled)', 'Controls are accessible'])
        ],
        'TC-008': [
            ('Navigate to Team Page', []),
            ('Check Top Stories section', ['Editorial feed displays (iOS)', 'Carousel displays (Android)', 'Content is team-specific'])
        ],
        'TC-009': [
            ('Open Team Page', []),
            ('Check all text elements', ['All UI text in Spanish']),
            ('Tap on articles', ['Articles load in Spanish']),
            ('Check ticketing links', ['Links work correctly'])
        ],
        'TC-010': [
            ('Open Team Page', []),
            ('Verify MIG displays Japanese', ['Content displays in Japanese']),
            ('Check all sections', ['Proper character rendering', 'Correct API calls with lang=ja'])
        ],
        'TC-011': [
            ('Close app', []),
            ('Open team page deep link', ['App opens to correct team']),
            ('Verify correct team loads', ['All sections load properly'])
        ],
        'TC-012': [
            ('Scroll to Team Info section', []),
            ('Tap "2025 Schedule"', ['Native schedule view opens']),
            ('Tap "2024 Schedule & Results"', ['Correct year displays'])
        ],
        'TC-013': [
            ('Force close app', []),
            ('Open app and navigate to Team Page', []),
            ('Measure load time', ['Page loads within 3 seconds', 'No visible lag or stuttering', 'Images load progressively'])
        ],
        'TC-014': [
            ('Switch between 5 different teams', ['Each switch completes < 2 seconds']),
            ('Monitor performance', ['Previous team data clears', 'No memory leaks'])
        ],
        'TC-015': [
            ('Enable airplane mode', []),
            ('Open Team Page', ['Appropriate error messages']),
            ('Try various actions', ['Cached content displays if available', 'No crashes'])
        ],
        'TC-016': [
            ('Navigate to Athletics team page', ['Page loads without errors', 'All modules display correctly'])
        ],
        'TC-017': [
            ('Enable screen reader', []),
            ('Navigate through Team Page', ['All elements properly labeled']),
            ('Test all interactive elements', ['Navigation order logical', 'Actions announced correctly'])
        ],
        'TC-018': [
            ('Set device to largest text size', []),
            ('Open Team Page', ['Text scales appropriately']),
            ('Check all text elements', ['No text truncation', 'Layout remains functional'])
        ],
        'TC-019': [
            ('Open same team on both platforms', []),
            ('Compare all sections', ['Same sections present']),
            ('Test same actions', ['Similar visual appearance', 'Consistent behavior'])
        ],
        'TC-020': [
            ('Open Team Page on iPad', []),
            ('Check MIG carousel', ['Consistent card heights']),
            ('Verify card heights', ['Proper spacing', 'No layout issues'])
        ],
        'TC-021': [
            ('Open Charles Proxy', []),
            ('Perform various actions', ['Page view tracked']),
            ('Verify analytics calls', ['Interactions logged', 'Correct parameters sent'])
        ],
        'TC-022': [
            ('Navigate to Team Page on Opening Day', []),
            ('Check MIG section for special branding', ['Opening Day branding displays in MIG']),
            ('Verify content sections for Opening Day content', ['Special Opening Day content in carousels']),
            ('Check for special badges or indicators', ['Appropriate badges/styling applied', 'Links to Opening Day promotions work'])
        ],
        'TC-023': [
            ('Navigate to any team page during All-Star break', []),
            ('Check MIG section', ['All-Star Game promotion visible']),
            ('Verify AL/NL All-Star team selections', ['Team\'s All-Star selections highlighted']),
            ('Check for All-Star voting links', ['Voting links functional (if active)', 'Special All-Star content in carousels'])
        ],
        'TC-024': [
            ('Navigate to playoff team\'s page', []),
            ('Check MIG for playoff games', ['Playoff games prominently displayed']),
            ('Verify playoff series information', ['Series status clearly shown']),
            ('Check for elimination/advancement updates', ['Next game information accurate', 'Playoff-specific content in carousels'])
        ],
        'TC-025': [
            ('Navigate to World Series team page', []),
            ('Verify World Series branding', ['World Series branding prominent']),
            ('Check game information accuracy', ['Series status and game info correct']),
            ('Test ticket/viewing links', ['Special World Series content featured', 'All links functional'])
        ],
        'TC-026': [
            ('Navigate to Team Page during ST', []),
            ('Check MIG for ST games', ['ST badge displays on games']),
            ('Verify split squad handling', ['Split squad games clearly marked']),
            ('Check venue information', ['Correct ST venue information', 'Roster updates reflected'])
        ],
        'TC-027': [
            ('Navigate to participating team page', []),
            ('Check MIG for international games', ['International Series branding visible']),
            ('Verify special event branding', ['Correct venue (London/Tokyo/etc)']),
            ('Check timezone handling', ['Proper timezone conversion', 'Special event content featured'])
        ],
        'TC-028': [
            ('During All-Star week with HRD', []),
            ('Check Team Page MIG', ['Both HRD and ASG display correctly']),
            ('Verify both events shown', ['Clear differentiation between events']),
            ('Test navigation between events', ['Navigation works properly', 'No UI conflicts or overlaps'])
        ],
        'TC-029': [
            ('Navigate to Team Page during warmup', []),
            ('Check MIG display', ['"Warmup" status clearly shown']),
            ('Verify countdown timer', ['Countdown to first pitch displays']),
            ('Check product links', ['No score shown yet', 'Appropriate product links available'])
        ],
        'TC-030': [
            ('Navigate to Team Page during delay', []),
            ('Check MIG status display', ['"Delayed" status prominent']),
            ('Verify delay reason shown', ['Delay reason displayed']),
            ('Monitor for updates', ['Current score preserved', 'Updates when game resumes'])
        ],
        'TC-031': [
            ('Navigate to Team Page', []),
            ('Check suspended game display', ['"Suspended" status clear']),
            ('Verify resume information', ['Resume date/time displayed']),
            ('Check both original and resume dates', ['Score at suspension shown', 'Links to both game dates work'])
        ],
        'TC-032': [
            ('Navigate during manager challenge', []),
            ('Check MIG display', ['Challenge indicator visible']),
            ('Verify challenge indicator', ['Game paused status shown']),
            ('Monitor resolution', ['Updates after decision', 'Seamless return to play'])
        ],
        'TC-033': [
            ('Navigate to Team Page', []),
            ('Check postponed game display', ['"Postponed" clearly shown']),
            ('Verify postponement reason', ['Reason displayed (Rain, etc.)']),
            ('Check for makeup date', ['Makeup date if scheduled', 'Ticket exchange info if available'])
        ],
        'TC-034': [
            ('Navigate to Team Page', []),
            ('Check forfeit game display', ['"Forfeit" status displayed']),
            ('Verify official score (9-0)', ['Official 9-0 score shown']),
            ('Check forfeit reason', ['Forfeit reason provided', 'Historical context available'])
        ],
        'TC-035': [
            ('Monitor preview game approaching start', ['Smooth state transitions']),
            ('Observe transition to warmup', ['No stuck states']),
            ('Watch warmup to live transition', ['Timely updates (< 30s)']),
            ('Monitor final out to final state', ['No data inconsistencies'])
        ],
        'TC-036': [
            ('Navigate to Team Page', []),
            ('Check both games display', ['Both games clearly separated']),
            ('Verify different states', ['Game 1/Game 2 indicators']),
            ('Test switching between games', ['Independent state tracking', 'Proper time display for each'])
        ],
        'TC-037': [
            ('Navigate to Team Page', []),
            ('Check inning display', ['Extra inning number shown']),
            ('Verify free runner indicators', ['Free runner rule applied']),
            ('Monitor score updates', ['Proper score tracking', 'No display issues with 10+ innings'])
        ],
        'TC-038': [
            ('Force app to background during live game', []),
            ('Wait 5 minutes', []),
            ('Return to Team Page', ['Current game state loads']),
            ('Verify correct state displays', ['No stuck on old state', 'Score updates properly', 'Smooth recovery process'])
        ]
    }
    
    return test_mappings

def format_test_steps_html(test_id: str, steps_with_results: List[Tuple[str, List[str]]]) -> str:
    """Format test steps with their expected results as HTML"""
    html_parts = []
    
    for i, (step, results) in enumerate(steps_with_results, 1):
        # Add step
        html_parts.append(f"{i}. {step}")
        
        # Add results for this step
        if results:
            for result in results:
                html_parts.append(f"   → {result}")
    
    return "<br/>".join(html_parts)

def update_page_content(page_data: Dict):
    """Update the page with new content"""
    content = page_data['body']['storage']['value']
    
    # Get test mappings
    test_mappings = map_results_to_steps({})
    
    # Process each test case
    for test_id, steps_with_results in test_mappings.items():
        # Find the test case in the content
        test_pattern = rf'(<tr>.*?Test Case ID</td><td>{test_id}</td>.*?</tr>.*?<strong>Test Steps</strong></td><td>)(.*?)(</td>.*?<strong>Expected Result</strong></td><td>)(.*?)(</td>)'
        
        def replace_test(match):
            formatted_steps = format_test_steps_html(test_id, steps_with_results)
            # Keep the original structure but replace the content
            return match.group(1) + formatted_steps + match.group(3) + "See step results above" + match.group(5)
        
        content = re.sub(test_pattern, replace_test, content, flags=re.DOTALL)
    
    # Update the page
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    auth = (JIRA_EMAIL, ATLASSIAN_TOKEN)
    
    update_data = {
        "version": {
            "number": page_data['version']['number'] + 1
        },
        "type": "page",
        "title": page_data['title'],
        "body": {
            "storage": {
                "value": content,
                "representation": "storage"
            }
        }
    }
    
    response = requests.put(
        CONFLUENCE_API,
        json=update_data,
        headers=headers,
        auth=auth
    )
    
    if response.status_code == 200:
        print("Page updated successfully")
    else:
        print(f"Failed to update page: {response.status_code}")
        print(response.text)

def main():
    """Main function"""
    # Get current page content
    page_data = get_page_content()
    if not page_data:
        return
    
    # Create updated content with properly formatted test steps
    content = page_data['body']['storage']['value']
    
    # Get test mappings
    test_mappings = map_results_to_steps({})
    
    # Create new content with updated test steps format
    for test_id, steps_with_results in test_mappings.items():
        # Find the table row for this test
        test_pattern = rf'(<td>{test_id}</td>.*?<td><strong>Test Steps</strong></td><td>)(.*?)(</td>.*?<td><strong>Expected Result</strong></td><td>)(.*?)(</td>)'
        
        # Format steps with expected results
        formatted_html = []
        for i, (step, results) in enumerate(steps_with_results, 1):
            step_html = f"<strong>Step {i}:</strong> {step}"
            if results:
                result_html = "<br/>".join([f"&nbsp;&nbsp;&nbsp;&nbsp;→ {r}" for r in results])
                formatted_html.append(f"{step_html}<br/>{result_html}")
            else:
                formatted_html.append(step_html)
        
        new_steps_html = "<br/>".join(formatted_html)
        
        # Update both test steps and expected results cells
        def replace_test(match):
            # Return with updated test steps and a note in expected results
            return match.group(1) + new_steps_html + match.group(3) + "<em>Expected results are mapped to each step above</em>" + match.group(5)
        
        content = re.sub(test_pattern, replace_test, content, flags=re.DOTALL | re.MULTILINE)
    
    # Update the page
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    auth = (JIRA_EMAIL, ATLASSIAN_TOKEN)
    
    update_data = {
        "version": {
            "number": page_data['version']['number'] + 1
        },
        "type": "page",
        "title": page_data['title'],
        "body": {
            "storage": {
                "value": content,
                "representation": "storage"
            }
        }
    }
    
    response = requests.put(
        CONFLUENCE_API,
        json=update_data,
        headers=headers,
        auth=auth
    )
    
    if response.status_code == 200:
        print("Page updated successfully")
        print(f"Updated {len(test_mappings)} test cases with properly mapped expected results")
    else:
        print(f"Failed to update page: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    main()