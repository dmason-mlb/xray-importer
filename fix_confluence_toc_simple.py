#!/usr/bin/env python3
"""
Fix Confluence TOC to be simple (top-level only) and remove duplicates
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

def remove_duplicate_tocs(content: str) -> str:
    """Remove all existing TOCs (both manual and macro-based)"""
    
    # Remove existing TOC macros
    content = re.sub(
        r'<ac:structured-macro[^>]+ac:name="toc"[^>]*>.*?</ac:structured-macro>',
        '',
        content,
        flags=re.DOTALL
    )
    
    # Remove manual table of contents patterns
    toc_patterns = [
        # Numbered list with links
        r'<ol>.*?</ol>',
        # Header followed by numbered list
        r'<h2>Table of Contents</h2>\s*<ol>.*?</ol>',
        # Any section that looks like a manual TOC
        r'<h[23]>(?:Table of Contents|Contents|TOC)</h[23]>\s*(?:<p>.*?</p>)?\s*<ol>.*?</ol>',
    ]
    
    for pattern in toc_patterns:
        content = re.sub(pattern, '', content, flags=re.DOTALL | re.IGNORECASE)
    
    return content

def add_simple_toc(content: str) -> str:
    """Add a simple TOC showing only top-level sections"""
    
    # First remove all existing TOCs
    content = remove_duplicate_tocs(content)
    
    # Create simple TOC macro - maxLevel=2 means only h1 and h2
    toc = '''<ac:structured-macro ac:name="toc" ac:schema-version="1">
<ac:parameter ac:name="maxLevel">2</ac:parameter>
<ac:parameter ac:name="minLevel">2</ac:parameter>
<ac:parameter ac:name="type">list</ac:parameter>
<ac:parameter ac:name="outline">false</ac:parameter>
<ac:parameter ac:name="printable">false</ac:parameter>
</ac:structured-macro>'''
    
    # Find the first h1 to insert TOC after
    h1_match = re.search(r'</h1>', content)
    if h1_match:
        insert_pos = h1_match.end()
        content = (
            content[:insert_pos] + 
            '\n' + toc + '\n' + 
            content[insert_pos:]
        )
    else:
        # No h1 found, insert at beginning
        content = toc + '\n' + content
    
    return content

def fix_page_toc(page_id: str) -> Tuple[bool, str]:
    """Fix TOC in a single page"""
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
        
        # Fix the TOC
        fixed_content = add_simple_toc(original_content)
        
        # Check if content changed
        if fixed_content == original_content:
            return True, f"Page '{title}' - No TOC changes needed"
        
        # Update the page
        confluence.update_page(
            page_id=page_id,
            title=title,
            body=fixed_content,
            type='page',
            representation='storage',
            minor_edit=False,
            version_comment='Simplified TOC to show only top-level sections'
        )
        
        return True, f"Page '{title}' - Simplified TOC successfully"
        
    except Exception as e:
        return False, f"Error processing page {page_id}: {str(e)}"

def main():
    """Main function"""
    print("Confluence Simple TOC Fix")
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
    print("- Remove all duplicate TOCs (manual and macro-based)")
    print("- Add a simple TOC showing only top-level sections (h2)")
    print()
    
    # Process each page
    for page_id in page_ids:
        success, message = fix_page_toc(page_id)
        
        if success:
            print(f"✓ {message}")
        else:
            print(f"✗ {message}")
    
    print()
    print("Complete!")
    print("\nNote: Pages should now have:")
    print("- A single, simple TOC at the top")
    print("- Only top-level sections (h2) listed")
    print("- No duplicate TOCs")

if __name__ == "__main__":
    main()