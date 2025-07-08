#!/usr/bin/env python3
"""
Fix Confluence pages using API v2 for new editor support
"""

import os
import re
import requests
from requests.auth import HTTPBasicAuth
import json
from typing import Dict, List, Tuple

# API Configuration
BASE_URL = os.getenv('JIRA_BASE_URL')
EMAIL = os.getenv('JIRA_EMAIL')
API_TOKEN = os.getenv('ATLASSIAN_TOKEN')

# V2 API endpoint
V2_API = f"{BASE_URL}/wiki/api/v2"

# Authentication
auth = HTTPBasicAuth(EMAIL, API_TOKEN)

def get_page_v2(page_id: str) -> Dict:
    """Get page using v2 API"""
    url = f"{V2_API}/pages/{page_id}"
    params = {
        "body-format": "storage",
        "get-draft": "false"
    }
    
    response = requests.get(url, auth=auth, params=params)
    response.raise_for_status()
    data = response.json()
    print(f"Page structure keys: {list(data.keys())}")  # Debug
    if 'body' in data:
        print(f"Body structure: {data['body'].keys()}")  # Debug
    return data

def update_page_v2(page_id: str, title: str, content: str, version: int) -> bool:
    """Update page using v2 API with new editor format"""
    url = f"{V2_API}/pages/{page_id}"
    
    data = {
        "id": page_id,
        "status": "current",
        "title": title,
        "body": {
            "representation": "storage",
            "value": content
        },
        "version": {
            "number": version + 1,
            "message": "Fixed formatting and migrated to new editor"
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    response = requests.put(url, auth=auth, json=data, headers=headers)
    
    if response.status_code == 200:
        return True
    else:
        print(f"Error updating page: {response.status_code} - {response.text}")
        return False

def fix_content_for_v2(content: str) -> str:
    """Fix content for v2 API and new editor"""
    
    # First, let's clean up the prerequisites code block that has leaked content
    if 'export XRAY_CLIENT' in content and '<h2>Authentication Process</h2>' in content:
        # Find the broken code block
        pattern = r'(<ac:structured-macro[^>]+ac:name="code"[^>]*>.*?<ac:plain-text-body><!\[CDATA\[)(.*?)(\]\]></ac:plain-text-body></ac:structured-macro>)'
        
        match = re.search(pattern, content, re.DOTALL)
        if match and '<h2>Authentication Process</h2>' in match.group(2):
            # Split the content at the authentication process
            code_content = match.group(2)
            parts = code_content.split('<h2>Authentication Process</h2>')
            
            if len(parts) == 2:
                # Clean bash code
                bash_code = parts[0].strip()
                # Remove any HTML tags from bash code
                bash_code = re.sub(r'<[^>]+>', '', bash_code)
                bash_code = bash_code.replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"')
                
                # Reconstruct the code block
                fixed_block = f'{match.group(1)}{bash_code}{match.group(3)}'
                
                # Add the authentication content after the code block
                auth_content = '<h2>Authentication Process</h2>' + parts[1]
                auth_content = auth_content.replace('</ac:plain-text-body></ac:structured-macro>', '')
                
                # Replace in content
                content = content.replace(match.group(0), fixed_block + '\n' + auth_content)
    
    # Fix HTML entities
    content = content.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
    
    # Fix JSON quotes in code blocks
    # Find JSON code blocks
    json_pattern = r'(<ac:parameter ac:name="language">json</ac:parameter>.*?<!\[CDATA\[)(.*?)(\]\]>)'
    
    def fix_json_block(match):
        prefix = match.group(1)
        json_content = match.group(2)
        suffix = match.group(3)
        
        # Fix quotes
        json_content = json_content.replace('&quot;', '"')
        
        return prefix + json_content + suffix
    
    content = re.sub(json_pattern, fix_json_block, content, flags=re.DOTALL)
    
    # Fix the cURL sections that are using h1 instead of h3
    curl_fixes = [
        ('<h1>Using a JSON file</h1>', '<h3>Using a JSON file</h3>'),
        ('<h1>Direct JSON</h1>', '<h3>Direct JSON</h3>'),
        ('<h1>Store token in variable</h1>', '<h3>Store token in variable</h3>')
    ]
    
    for old, new in curl_fixes:
        content = content.replace(old, new)
    
    # Ensure these curl commands are in code blocks
    curl_commands = [
        ('Using a JSON file', '''curl -H "Content-Type: application/json" -X POST \\
  --data @"cloud_auth.json" \\
  https://xray.cloud.getxray.app/api/v2/authenticate'''),
        ('Direct JSON', '''curl -H "Content-Type: application/json" -X POST \\
  --data '{"client_id": "YOUR_CLIENT_ID", "client_secret": "YOUR_CLIENT_SECRET"}' \\
  https://xray.cloud.getxray.app/api/v2/authenticate'''),
        ('Store token in variable', '''token=$(curl -H "Content-Type: application/json" -X POST \\
  --data @"cloud_auth.json" \\
  https://xray.cloud.getxray.app/api/v2/authenticate | tr -d '"')''')
    ]
    
    for title, cmd in curl_commands:
        # Check if the command is not in a code block
        if cmd in content and not (f'<![CDATA[{cmd}]]>' in content):
            # Find the command and wrap it
            pattern = f'<h3>{title}</h3>\n{re.escape(cmd)}'
            replacement = f'''<h3>{title}</h3>
<ac:structured-macro ac:name="code" ac:schema-version="1">
<ac:parameter ac:name="language">bash</ac:parameter>
<ac:plain-text-body><![CDATA[{cmd}]]></ac:plain-text-body>
</ac:structured-macro>'''
            content = content.replace(pattern, replacement)
    
    # Fix template literals in JavaScript
    content = re.sub(
        r"'Authorization': Bearer \$\{token\}",
        "'Authorization': `Bearer ${token}`",
        content
    )
    
    # Fix broken code blocks that have content after them
    content = re.sub(
        r'</ac:structured-macro>\s*\n*(bash|python|javascript|json|text)\s*\n',
        '</ac:structured-macro>\n',
        content
    )
    
    # Clean up empty paragraphs
    content = re.sub(r'<p>\s*</p>', '', content)
    
    # Fix any code blocks that have HTML inside CDATA
    def clean_cdata_content(match):
        cdata_content = match.group(1)
        
        # If there are HTML tags inside, it's probably broken
        if any(tag in cdata_content for tag in ['<h1>', '<h2>', '<h3>', '<strong>', '<code>', '</code>']):
            # Try to extract just the code part
            # Look for where HTML starts
            html_start = cdata_content.find('<')
            if html_start > 0:
                cdata_content = cdata_content[:html_start].strip()
            else:
                # Remove all HTML tags
                cdata_content = re.sub(r'<[^>]+>', '', cdata_content)
        
        return f'<![CDATA[{cdata_content}]]>'
    
    content = re.sub(r'<!\[CDATA\[(.*?)\]\]>', clean_cdata_content, content, flags=re.DOTALL)
    
    # Ensure TOC is simple
    content = re.sub(
        r'<ac:structured-macro[^>]+ac:name="toc"[^>]*>.*?</ac:structured-macro>',
        '''<ac:structured-macro ac:name="toc" ac:schema-version="1">
<ac:parameter ac:name="maxLevel">2</ac:parameter>
<ac:parameter ac:name="minLevel">2</ac:parameter>
<ac:parameter ac:name="style">none</ac:parameter>
</ac:structured-macro>''',
        content,
        flags=re.DOTALL
    )
    
    return content

def fix_page_v2(page_id: str) -> Tuple[bool, str]:
    """Fix page using v2 API"""
    try:
        # Get page
        page = get_page_v2(page_id)
        
        title = page['title']
        content = page['body']['storage']['value']
        version = page['version']['number']
        
        # Fix content
        fixed_content = fix_content_for_v2(content)
        
        # Update page
        if update_page_v2(page_id, title, fixed_content, version):
            return True, f"Page '{title}' - Updated with v2 API"
        else:
            return False, f"Page '{title}' - Update failed"
            
    except Exception as e:
        return False, f"Error processing page {page_id}: {str(e)}"

def main():
    """Main function"""
    print("Confluence V2 API Fix")
    print("=" * 50)
    
    # Check environment variables
    required_vars = ['JIRA_BASE_URL', 'JIRA_EMAIL', 'ATLASSIAN_TOKEN']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Error: Missing environment variables: {', '.join(missing_vars)}")
        return
    
    print(f"Using Confluence V2 API at: {V2_API}")
    print()
    
    # Page IDs to process
    page_ids = [
        "4934565948",  # Parent page
        "4934729793",  # XRAY API Authentication Guide
        "4934598688",  # XRAY GraphQL API Reference
        "4934500384",  # JIRA Field Requirements and Validation
        "4934565974",  # Implementation Guide for Test Automation
        "4936237082"   # XRAY Test Modification Guide
    ]
    
    print(f"Processing {len(page_ids)} pages...")
    print("This will:")
    print("- Use V2 API for new editor support")
    print("- Fix all formatting issues")
    print("- Clean up code blocks")
    print("- Ensure proper structure")
    print()
    
    # Process each page
    for page_id in page_ids:
        success, message = fix_page_v2(page_id)
        
        if success:
            print(f"✓ {message}")
        else:
            print(f"✗ {message}")
    
    print()
    print("Complete! Pages should now use the new editor.")

if __name__ == "__main__":
    main()