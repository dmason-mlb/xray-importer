#!/usr/bin/env python3
import os
import requests
import json
import base64
from pathlib import Path

# Confluence API configuration
CONFLUENCE_BASE_URL = 'https://baseball.atlassian.net/wiki'
PARENT_PAGE_ID = '4934565948'
EMAIL = os.environ.get('JIRA_EMAIL')
API_TOKEN = os.environ.get('ATLASSIAN_TOKEN')

if not EMAIL or not API_TOKEN:
    print("❌ Error: JIRA_EMAIL and ATLASSIAN_TOKEN environment variables must be set")
    exit(1)

# Create auth header
auth_string = f"{EMAIL}:{API_TOKEN}"
auth_bytes = auth_string.encode('ascii')
auth_b64 = base64.b64encode(auth_bytes).decode('ascii')

headers = {
    'Authorization': f'Basic {auth_b64}',
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

# Read the markdown file
markdown_file = Path('sdui-test-creation/05-test-modification-guide.md')
if not markdown_file.exists():
    print(f"❌ Error: File {markdown_file} not found")
    exit(1)

with open(markdown_file, 'r') as f:
    markdown_content = f.read()

# Convert markdown headers to Confluence format
# Confluence uses h1-h6 tags, but we'll adjust the heading levels
content_html = markdown_content

# Basic markdown to Confluence wiki markup conversions
content_html = content_html.replace('```graphql', '<pre><code class="language-graphql">')
content_html = content_html.replace('```javascript', '<pre><code class="language-javascript">')
content_html = content_html.replace('```', '</code></pre>')
content_html = content_html.replace('**', '<strong>')
content_html = content_html.replace('`', '<code>')

# Convert headers
import re
content_html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', content_html, flags=re.MULTILINE)
content_html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', content_html, flags=re.MULTILINE)
content_html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', content_html, flags=re.MULTILINE)

# Convert lists
content_html = re.sub(r'^\- (.+)$', r'<li>\1</li>', content_html, flags=re.MULTILINE)
content_html = re.sub(r'^\d+\. (.+)$', r'<li>\1</li>', content_html, flags=re.MULTILINE)

# Add list wrappers (simplified approach)
content_html = re.sub(r'(<li>.*?</li>\n)+', r'<ul>\g<0></ul>\n', content_html, flags=re.MULTILINE | re.DOTALL)

# Convert line breaks
content_html = content_html.replace('\n\n', '</p><p>')
content_html = f'<p>{content_html}</p>'

# Clean up empty paragraphs
content_html = re.sub(r'<p>\s*</p>', '', content_html)
content_html = re.sub(r'<p>(<h[1-6]>)', r'\1', content_html)
content_html = re.sub(r'(</h[1-6]>)</p>', r'\1', content_html)

# Create the page
page_data = {
    "type": "page",
    "title": "XRAY Test Modification Guide",
    "ancestors": [{"id": PARENT_PAGE_ID}],
    "space": {"key": "~911651470"},
    "body": {
        "storage": {
            "value": content_html,
            "representation": "storage"
        }
    }
}

# Check if page already exists
search_url = f"{CONFLUENCE_BASE_URL}/rest/api/content"
search_params = {
    "title": "XRAY Test Modification Guide",
    "spaceKey": "~911651470",
    "expand": "version"
}

search_response = requests.get(search_url, headers=headers, params=search_params)
existing_pages = search_response.json().get('results', [])

if existing_pages:
    # Update existing page
    page_id = existing_pages[0]['id']
    current_version = existing_pages[0]['version']['number']
    
    update_data = {
        "version": {
            "number": current_version + 1
        },
        "title": "XRAY Test Modification Guide",
        "type": "page",
        "body": {
            "storage": {
                "value": content_html,
                "representation": "storage"
            }
        }
    }
    
    update_url = f"{CONFLUENCE_BASE_URL}/rest/api/content/{page_id}"
    response = requests.put(update_url, headers=headers, json=update_data)
    
    if response.status_code == 200:
        print(f"✅ Page updated successfully!")
        print(f"📄 Page URL: {CONFLUENCE_BASE_URL}/wiki/spaces/~911651470/pages/{page_id}")
    else:
        print(f"❌ Failed to update page. Status: {response.status_code}")
        print(f"Response: {response.text}")
else:
    # Create new page
    create_url = f"{CONFLUENCE_BASE_URL}/rest/api/content"
    response = requests.post(create_url, headers=headers, json=page_data)
    
    if response.status_code == 200:
        result = response.json()
        page_id = result['id']
        print(f"✅ Page created successfully!")
        print(f"📄 Page URL: {CONFLUENCE_BASE_URL}/wiki/spaces/~911651470/pages/{page_id}")
        print(f"📌 Parent Page: {CONFLUENCE_BASE_URL}/wiki/spaces/~911651470/pages/{PARENT_PAGE_ID}")
    else:
        print(f"❌ Failed to create page. Status: {response.status_code}")
        print(f"Response: {response.text}")