#!/usr/bin/env python3
import json
import requests
import base64
import os
import uuid
import re

# Confluence API configuration
CONFLUENCE_BASE_URL = 'https://baseball.atlassian.net/wiki'
PAGE_ID = '4932862074'
EMAIL = os.environ.get('JIRA_EMAIL', 'douglas.mason@mlb.com')
API_TOKEN = os.environ.get('ATLASSIAN_TOKEN')  # Set via environment variable

# Create auth header
auth_string = f"{EMAIL}:{API_TOKEN}"
auth_bytes = auth_string.encode('ascii')
auth_b64 = base64.b64encode(auth_bytes).decode('ascii')

headers = {
    'Authorization': f'Basic {auth_b64}',
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

# Read test data to get JIRA keys
with open('mlbmob/extra-info-response.json', 'r') as f:
    test_data = json.load(f)

# Create a mapping of test numbers to test data
test_mapping = {}
results = test_data['data']['getExpandedTests']['results']

# The order of tests in the JSON follows the document order
test_numbers = [
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
    11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
    21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
    31, 32, 33, 34, 35, 36, 37, 38, 39, 40,
    41, 42, 43, 44, 45, 46, 47, 48, 49, 50,
    51, 52, 53, 54, 55, 56, 57, 58, 59, 60,
    61, 62, 63, 64, 65, 66, 67, 68, 69, 70,
    71, 72, 73, 74, 75, 76
]

for i, test_num in enumerate(test_numbers):
    if i < len(results):
        test_mapping[test_num] = results[i]

# Get current page content
get_url = f"{CONFLUENCE_BASE_URL}/rest/api/content/{PAGE_ID}?expand=body.storage,version"
response = requests.get(get_url, headers=headers)

if response.status_code != 200:
    print(f"❌ Failed to get current page. Status code: {response.status_code}")
    exit(1)

page_data = response.json()
current_version = page_data['version']['number']
current_content = page_data['body']['storage']['value']

print(f"Current page version: {current_version}")

# Process each test (skip Test 1 since it's already updated)
for test_num in range(2, 77):
    test_info = test_mapping.get(test_num, {})
    jira_key = test_info.get('jira', {}).get('key', 'UNKNOWN')
    
    # Create the new task body with Test number and linked JIRA key
    new_task_body = f'Test {test_num}: <a href="https://baseball.atlassian.net/browse/{jira_key}">{jira_key}</a>'
    
    # Find and replace the task body content
    # Look for the pattern of the task body with "Approved" text
    # The pattern is: <ac:task-body><span class="placeholder-inline-tasks">Approved</span></ac:task-body>
    
    # First, let's find the test section
    test_section_pattern = f'Test {test_num}: <a href="[^"]+">{jira_key}</a></h3>'
    
    # Find where this test starts in the content
    test_match = re.search(test_section_pattern, current_content)
    if test_match:
        # Find the next task body after this test heading
        search_start = test_match.end()
        
        # Look for the task body pattern after this position
        task_body_pattern = r'<ac:task-body><span class="placeholder-inline-tasks">Approved</span></ac:task-body>'
        
        # Find the first occurrence of this pattern after the test heading
        remaining_content = current_content[search_start:]
        task_match = re.search(task_body_pattern, remaining_content)
        
        if task_match:
            # Calculate the actual position in the full content
            actual_pos = search_start + task_match.start()
            
            # Replace just this occurrence
            before = current_content[:actual_pos]
            after = current_content[actual_pos + len(task_match.group(0)):]
            
            new_task_body_html = f'<ac:task-body><span class="placeholder-inline-tasks">{new_task_body}</span></ac:task-body>'
            current_content = before + new_task_body_html + after
            
            print(f"✓ Updated Test {test_num} action item text to: {new_task_body}")
        else:
            print(f"⚠️  Could not find task body for Test {test_num}")
    else:
        print(f"⚠️  Could not find Test {test_num} section")

# Update the page
update_data = {
    "version": {
        "number": current_version + 1
    },
    "title": page_data['title'],
    "type": "page",
    "body": {
        "storage": {
            "value": current_content,
            "representation": "storage"
        }
    }
}

update_url = f"{CONFLUENCE_BASE_URL}/rest/api/content/{PAGE_ID}"
update_response = requests.put(update_url, headers=headers, json=update_data)

if update_response.status_code == 200:
    print("\n✅ Confluence page updated successfully!")
    print(f"Page URL: {CONFLUENCE_BASE_URL}/wiki/spaces/MLBMOB/pages/{PAGE_ID}")
    print("\nAll action items now show 'Test X: JIRA-KEY' with linked JIRA issues")
else:
    print(f"\n❌ Failed to update page. Status code: {update_response.status_code}")
    print(f"Response: {update_response.text}")