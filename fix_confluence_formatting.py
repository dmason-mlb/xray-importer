#!/usr/bin/env python3
"""
Fix Confluence page formatting issues
Converts markdown syntax to proper Confluence storage format
"""

import os
import re
from atlassian import Confluence
from typing import Dict, List, Tuple

# Initialize Confluence client
confluence = Confluence(
    url=os.getenv('JIRA_BASE_URL'),
    username=os.getenv('JIRA_EMAIL'),
    password=os.getenv('ATLASSIAN_TOKEN'),
    cloud=True
)

def fix_content_formatting(content: str) -> str:
    """Fix various formatting issues in Confluence content"""
    
    # Remove empty paragraph tags
    content = re.sub(r'<p></p>', '', content)
    
    # Fix markdown headers (# Header -> <h1>Header</h1>)
    # Handle headers at the beginning of lines
    content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)
    content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
    content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
    content = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', content, flags=re.MULTILINE)
    
    # Fix markdown headers in the middle of content
    content = re.sub(r'<h1>(.+)</h1>\n(.+)', r'<h1>\1</h1>\n\2', content)
    
    # Fix markdown links [text](url) -> <a href="url">text</a>
    # Handle external links
    content = re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)', r'<a href="\2">\1</a>', content)
    
    # Fix markdown anchor links [text](#anchor) -> just text (anchors don't work the same in Confluence)
    content = re.sub(r'\[([^\]]+)\]\(#[^)]+\)', r'\1', content)
    
    # Fix file links [text](file.md) -> text (remove the link part)
    content = re.sub(r'\[([^\]]+)\]\([^)]+\.md\)', r'\1', content)
    
    # Fix inline code `code` -> <code>code</code>
    # But be careful not to replace inside CDATA sections
    def replace_inline_code(match):
        full_match = match.group(0)
        if '<![CDATA[' in full_match and ']]>' in full_match:
            return full_match
        return re.sub(r'`([^`]+)`', r'<code>\1</code>', full_match)
    
    # Split content to handle CDATA sections separately
    parts = re.split(r'(<!\[CDATA\[.*?\]\]>)', content, flags=re.DOTALL)
    processed_parts = []
    for i, part in enumerate(parts):
        if i % 2 == 0:  # Not inside CDATA
            part = re.sub(r'`([^`]+)`', r'<code>\1</code>', part)
        processed_parts.append(part)
    content = ''.join(processed_parts)
    
    # Clean up any remaining markdown code blocks that aren't in proper Confluence format
    # Look for triple backticks
    content = re.sub(r'```(\w+)?\n(.*?)```', 
                    lambda m: f'<ac:structured-macro ac:name="code" ac:schema-version="1">' + 
                             (f'<ac:parameter ac:name="language">{m.group(1)}</ac:parameter>' if m.group(1) else '') +
                             f'<ac:plain-text-body><![CDATA[{m.group(2)}]]></ac:plain-text-body></ac:structured-macro>',
                    content, flags=re.DOTALL)
    
    # Fix double backticks to single backticks inside text
    content = re.sub(r'``(.+?)``', r'<code>\1</code>', content)
    
    # Clean up extra newlines around headers
    content = re.sub(r'\n\n+<h(\d)>', r'\n<h\1>', content)
    content = re.sub(r'</h(\d)>\n\n+', r'</h\1>\n', content)
    
    return content

def fix_page(page_id: str, dry_run: bool = False) -> Tuple[bool, str]:
    """Fix formatting in a single page"""
    try:
        # Get page content
        page = confluence.get_page_by_id(
            page_id, 
            expand='body.storage,version'
        )
        
        if not page:
            return False, f"Page {page_id} not found"
        
        title = page['title']
        original_content = page['body']['storage']['value']
        version = page['version']['number']
        
        # Fix the content
        fixed_content = fix_content_formatting(original_content)
        
        # Check if content changed
        if fixed_content == original_content:
            return True, f"Page '{title}' - No changes needed"
        
        if dry_run:
            return True, f"Page '{title}' - Would update (dry run)"
        
        # Update the page
        confluence.update_page(
            page_id=page_id,
            title=title,
            body=fixed_content,
            type='page',
            representation='storage',
            minor_edit=True
        )
        
        return True, f"Page '{title}' - Updated successfully"
        
    except Exception as e:
        return False, f"Error processing page {page_id}: {str(e)}"

def get_all_page_ids() -> List[str]:
    """Get all page IDs to process"""
    page_ids = []
    
    # Parent page
    parent_id = "4934565948"
    page_ids.append(parent_id)
    
    # Child pages
    child_ids = [
        "4934729793",  # XRAY API Authentication Guide
        "4934598688",  # XRAY GraphQL API Reference
        "4934500384",  # JIRA Field Requirements and Validation
        "4934565974",  # Implementation Guide for Test Automation
        "4936237082"   # XRAY Test Modification Guide
    ]
    page_ids.extend(child_ids)
    
    return page_ids

def main():
    """Main function to fix all pages"""
    print("Confluence Formatting Fixer")
    print("=" * 50)
    
    # Check environment variables
    required_vars = ['JIRA_BASE_URL', 'JIRA_EMAIL', 'ATLASSIAN_TOKEN']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Error: Missing environment variables: {', '.join(missing_vars)}")
        return
    
    print(f"Confluence URL: {os.getenv('JIRA_BASE_URL')}")
    print(f"User: {os.getenv('JIRA_EMAIL')}")
    print()
    
    # Get all page IDs
    page_ids = get_all_page_ids()
    print(f"Found {len(page_ids)} pages to process")
    print()
    
    # Process each page
    success_count = 0
    error_count = 0
    
    for page_id in page_ids:
        success, message = fix_page(page_id, dry_run=False)
        
        if success:
            print(f"✓ {message}")
            success_count += 1
        else:
            print(f"✗ {message}")
            error_count += 1
    
    print()
    print("=" * 50)
    print(f"Summary: {success_count} successful, {error_count} errors")

if __name__ == "__main__":
    main()