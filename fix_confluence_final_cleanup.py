#!/usr/bin/env python3
"""
Final cleanup for Confluence pages - remove empty code blocks and fix remaining issues
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
    return response.json()

def update_page_v2(page_id: str, title: str, content: str, version: int) -> bool:
    """Update page using v2 API"""
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
            "message": "Final cleanup - removed empty code blocks and fixed remaining issues"
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

def final_cleanup(content: str) -> str:
    """Final cleanup of content"""
    
    # Remove empty code blocks
    empty_code_pattern = r'<ac:structured-macro[^>]+ac:name="code"[^>]*>\s*<ac:parameter[^>]+>.*?</ac:parameter>\s*</ac:structured-macro>'
    
    # Find all code blocks
    code_blocks = re.findall(r'<ac:structured-macro[^>]+ac:name="code"[^>]*>.*?</ac:structured-macro>', content, re.DOTALL)
    
    for block in code_blocks:
        # Check if this block has no CDATA content or empty CDATA
        if '<ac:plain-text-body></ac:plain-text-body>' in block or \
           '<ac:plain-text-body><![CDATA[]]></ac:plain-text-body>' in block or \
           (not '<ac:plain-text-body>' in block):
            # Remove this empty block
            content = content.replace(block, '')
    
    # Fix the JavaScript code that's outside a code block
    # Find loose JavaScript code
    js_pattern = r'<code>\);\s*\}\s*\}\s*\n\s*async function executeGraphQLQuery.*?</code>'
    
    js_match = re.search(js_pattern, content, re.DOTALL)
    if js_match:
        # This JavaScript should be part of the previous code block
        js_code = js_match.group(0).replace('<code>', '').replace('</code>', '')
        
        # Find the JavaScript code block that ends with "Authentication failed:"
        js_block_pattern = r'(<ac:structured-macro[^>]+ac:name="code"[^>]*>.*?<ac:parameter[^>]+>javascript</ac:parameter>.*?<!\[CDATA\[)(.*?)(Authentication failed:.*?)(\]\]></ac:plain-text-body></ac:structured-macro>)'
        
        def fix_js_block(match):
            prefix = match.group(1)
            code = match.group(2)
            auth_failed = match.group(3)
            suffix = match.group(4)
            
            # Complete the JavaScript code
            full_code = code + auth_failed + js_code.strip()
            
            return prefix + full_code + suffix
        
        content = re.sub(js_block_pattern, fix_js_block, content, flags=re.DOTALL)
        
        # Remove the loose JavaScript
        content = content.replace(js_match.group(0), '')
    
    # Add missing content for some sections
    # Response section after "Store token in variable"
    response_section = '''<h3>Response</h3>
<ul>
<li><strong>200 OK</strong>: Returns a JWT token as a JSON string (with quotes)
<ac:structured-macro ac:name="code" ac:schema-version="1">
<ac:parameter ac:name="language">text</ac:parameter>
<ac:plain-text-body><![CDATA["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."]]></ac:plain-text-body>
</ac:structured-macro></li>
<li><strong>400 Bad Request</strong>: Wrong request syntax</li>
<li><strong>401 Unauthorized</strong>: Invalid license or credentials</li>
<li><strong>500 Internal Server Error</strong>: Server error during authentication</li>
</ul>

<h3>Step 2: Use Token in GraphQL Requests</h3>
<p><strong>GraphQL Endpoint</strong>: <code>https://xray.cloud.getxray.app/api/v2/graphql</code></p>
<p><strong>Headers</strong>:</p>
<ac:structured-macro ac:name="code" ac:schema-version="1">
<ac:parameter ac:name="language">text</ac:parameter>
<ac:plain-text-body><![CDATA[Authorization: Bearer <token>
Content-Type: application/json]]></ac:plain-text-body>
</ac:structured-macro>

<p><strong>Example GraphQL Request</strong>:</p>'''
    
    # Find where to insert this
    store_token_pattern = r'(Store token in variable</h3>.*?</ac:structured-macro>)\s*(<ac:structured-macro[^>]+ac:name="code"[^>]*>\s*<ac:parameter[^>]+>text</ac:parameter>\s*</ac:structured-macro>)'
    
    if re.search(store_token_pattern, content, re.DOTALL):
        content = re.sub(
            store_token_pattern,
            r'\1\n' + response_section,
            content,
            flags=re.DOTALL
        )
    
    # Add missing Python and JavaScript implementation headers
    if '<h2>Python Implementation</h2>' not in content:
        python_pattern = r'(<ac:structured-macro[^>]+ac:name="code"[^>]*>.*?<ac:parameter[^>]+>python</ac:parameter>)'
        content = re.sub(
            python_pattern,
            '<h2>Python Implementation</h2>\n\\1',
            content,
            count=1,
            flags=re.DOTALL
        )
    
    if '<h2>JavaScript/Node.js Implementation</h2>' not in content:
        js_pattern = r'(</ac:structured-macro>\s*)(<ac:structured-macro[^>]+ac:name="code"[^>]*>.*?<ac:parameter[^>]+>javascript</ac:parameter>)'
        
        # Find the right place - after the Python code block
        python_end = content.find('return response.json()]]></ac:plain-text-body></ac:structured-macro>')
        if python_end > 0:
            insert_pos = python_end + len('return response.json()]]></ac:plain-text-body></ac:structured-macro>')
            content = content[:insert_pos] + '\n\n<h2>JavaScript/Node.js Implementation</h2>\n' + content[insert_pos:]
    
    # Remove any remaining "Authorization: Bearer \nContent-Type: application/json" that's outside code blocks
    loose_headers = re.search(r'Authorization: Bearer \s*\nContent-Type: application/json', content)
    if loose_headers and not re.search(r'<!\[CDATA\[.*?' + re.escape(loose_headers.group(0)) + r'.*?\]\]>', content, re.DOTALL):
        content = content.replace(loose_headers.group(0), '')
    
    # Add security best practices content if missing
    if re.search(r'<h2>Security Best Practices</h2>\s*<p></p>\s*<p></p>', content):
        security_content = '''<h2>Security Best Practices</h2>
<ul>
<li>Never commit API credentials to version control</li>
<li>Use environment variables or secure key management systems</li>
<li>Rotate API keys regularly</li>
<li>Implement proper error handling to avoid exposing credentials</li>
<li>Use HTTPS for all API communications</li>
<li>Monitor API usage for suspicious activity</li>
</ul>'''
        
        content = re.sub(
            r'<h2>Security Best Practices</h2>\s*<p></p>\s*<p></p>',
            security_content,
            content
        )
    
    # Clean up multiple empty paragraphs
    content = re.sub(r'(<p></p>\s*){2,}', '<p></p>', content)
    content = re.sub(r'<p>\s*</p>', '', content)
    
    # Clean up extra whitespace
    content = re.sub(r'\n\n\n+', '\n\n', content)
    
    return content

def fix_page_final(page_id: str) -> Tuple[bool, str]:
    """Final cleanup for page"""
    try:
        # Get page
        page = get_page_v2(page_id)
        
        title = page['title']
        content = page['body']['storage']['value']
        version = page['version']['number']
        
        # Apply final cleanup
        fixed_content = final_cleanup(content)
        
        # Update page
        if update_page_v2(page_id, title, fixed_content, version):
            return True, f"Page '{title}' - Final cleanup completed"
        else:
            return False, f"Page '{title}' - Update failed"
            
    except Exception as e:
        return False, f"Error processing page {page_id}: {str(e)}"

def main():
    """Main function"""
    print("Confluence Final Cleanup")
    print("=" * 50)
    
    # Check environment variables
    required_vars = ['JIRA_BASE_URL', 'JIRA_EMAIL', 'ATLASSIAN_TOKEN']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Error: Missing environment variables: {', '.join(missing_vars)}")
        return
    
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
    print("- Remove empty code blocks")
    print("- Fix JavaScript code outside blocks")
    print("- Add missing section content")
    print("- Clean up formatting")
    print()
    
    # Process each page
    for page_id in page_ids:
        success, message = fix_page_final(page_id)
        
        if success:
            print(f"✓ {message}")
        else:
            print(f"✗ {message}")
    
    print()
    print("Complete! Pages should now be properly formatted.")

if __name__ == "__main__":
    main()