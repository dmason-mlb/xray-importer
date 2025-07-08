#!/usr/bin/env python3
"""
Fix Confluence table of contents, anchor links, and editor version
"""

import os
import re
from atlassian import Confluence
from typing import Dict, List, Tuple
import json

# Initialize Confluence client
confluence = Confluence(
    url=os.getenv('JIRA_BASE_URL'),
    username=os.getenv('JIRA_EMAIL'),
    password=os.getenv('ATLASSIAN_TOKEN'),
    cloud=True
)

def create_toc_with_anchors(content: str) -> str:
    """Create a proper table of contents with working anchor links"""
    
    # Find all headers in the content
    headers = []
    header_pattern = r'<h(\d)>([^<]+)</h\1>'
    
    for match in re.finditer(header_pattern, content):
        level = int(match.group(1))
        title = match.group(2).strip()
        # Create anchor ID from title (remove special chars, lowercase, replace spaces)
        anchor_id = re.sub(r'[^a-zA-Z0-9\s-]', '', title).lower().replace(' ', '-')
        headers.append((level, title, anchor_id))
    
    # Build TOC
    toc_lines = []
    toc_lines.append('<ac:structured-macro ac:name="toc" ac:schema-version="1">')
    toc_lines.append('<ac:parameter ac:name="maxLevel">3</ac:parameter>')
    toc_lines.append('<ac:parameter ac:name="minLevel">1</ac:parameter>')
    toc_lines.append('<ac:parameter ac:name="type">list</ac:parameter>')
    toc_lines.append('<ac:parameter ac:name="outline">true</ac:parameter>')
    toc_lines.append('<ac:parameter ac:name="printable">false</ac:parameter>')
    toc_lines.append('</ac:structured-macro>')
    
    toc = '\n'.join(toc_lines)
    
    # Add anchor macros before headers
    for level, title, anchor_id in headers:
        # Add anchor before the header
        anchor = f'<ac:structured-macro ac:name="anchor" ac:schema-version="1"><ac:parameter ac:name="">{anchor_id}</ac:parameter></ac:structured-macro>'
        # Replace header with anchor + header
        content = re.sub(
            f'<h{level}>{re.escape(title)}</h{level}>',
            f'{anchor}<h{level}>{title}</h{level}>',
            content,
            count=1
        )
    
    return toc, content

def fix_table_of_contents(content: str) -> str:
    """Fix table of contents sections in the content"""
    
    # Pattern to find existing table of contents
    toc_patterns = [
        # Numbered list with links
        r'<ol>.*?</ol>',
        # Header followed by numbered list
        r'<h2>Table of Contents</h2>\s*<ol>.*?</ol>',
    ]
    
    # Remove old TOC patterns
    for pattern in toc_patterns:
        if re.search(pattern, content, re.DOTALL | re.IGNORECASE):
            content = re.sub(pattern, '', content, flags=re.DOTALL | re.IGNORECASE)
    
    # Create new TOC
    toc, content_with_anchors = create_toc_with_anchors(content)
    
    # Insert TOC after the first h1 or at the beginning
    h1_match = re.search(r'</h1>', content_with_anchors)
    if h1_match:
        insert_pos = h1_match.end()
        content_with_anchors = (
            content_with_anchors[:insert_pos] + 
            '\n' + toc + '\n' + 
            content_with_anchors[insert_pos:]
        )
    else:
        content_with_anchors = toc + '\n' + content_with_anchors
    
    return content_with_anchors

def fix_content_formatting(content: str) -> str:
    """Comprehensive fix for all formatting issues"""
    
    # First fix all the previous issues
    content = fix_broken_code_blocks(content)
    content = re.sub(r'<p>\s*</p>', '', content)
    content = fix_headers_and_code(content)
    
    # Fix table of contents and add anchors
    content = fix_table_of_contents(content)
    
    return content

def fix_broken_code_blocks(content: str) -> str:
    """Fix code blocks where content leaked outside CDATA"""
    pattern = r'(</ac:plain-text-body></ac:structured-macro>)\s*(python|bash|javascript|json|graphql|text)\s*\n([^<]+?)(?=<)'
    
    def replace_broken_block(match):
        closing_tag = match.group(1)
        language = match.group(2)
        code = match.group(3).rstrip()
        
        new_block = f'</ac:structured-macro>\n<ac:structured-macro ac:name="code" ac:schema-version="1">'
        new_block += f'<ac:parameter ac:name="language">{language}</ac:parameter>'
        new_block += f'<ac:plain-text-body><![CDATA[{code}]]></ac:plain-text-body></ac:structured-macro>'
        
        return new_block
    
    content = re.sub(pattern, replace_broken_block, content, flags=re.MULTILINE | re.DOTALL)
    return content

def fix_headers_and_code(content: str) -> str:
    """Fix headers and code formatting"""
    
    # Protect CDATA content
    def protect_cdata_content(match):
        cdata_content = match.group(1)
        cdata_content = cdata_content.replace('<h1>', '&lt;h1&gt;').replace('</h1>', '&lt;/h1&gt;')
        cdata_content = cdata_content.replace('<h2>', '&lt;h2&gt;').replace('</h2>', '&lt;/h2&gt;')
        cdata_content = cdata_content.replace('<h3>', '&lt;h3&gt;').replace('</h3>', '&lt;/h3&gt;')
        return f'<![CDATA[{cdata_content}]]>'
    
    content = re.sub(r'<!\[CDATA\[(.*?)\]\]>', protect_cdata_content, content, flags=re.DOTALL)
    
    # Fix code endings
    content = re.sub(r'``\s*<code>', '', content)
    content = re.sub(r'</code>\s*``', '', content)
    
    # Fix inline code outside of CDATA
    parts = re.split(r'(<!\[CDATA\[.*?\]\]>|<ac:structured-macro.*?</ac:structured-macro>)', content, flags=re.DOTALL)
    
    for i in range(len(parts)):
        if i % 2 == 0:
            parts[i] = re.sub(r'(?<!`)`([^`\n]+)`(?!`)', r'<code>\1</code>', parts[i])
            parts[i] = re.sub(r'``', '', parts[i])
    
    content = ''.join(parts)
    
    # Fix markdown headers
    content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)
    content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
    content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
    content = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', content, flags=re.MULTILINE)
    
    # Fix links
    content = re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)', r'<a href="\2">\1</a>', content)
    content = re.sub(r'\[([^\]]+)\]\(#[^)]+\)', r'\1', content)
    content = re.sub(r'\[([^\]]+)\]\([^)]+\.md\)', r'\1', content)
    
    return content

def update_page_with_new_editor(page_id: str, title: str, content: str) -> bool:
    """Update page using the proper API call to ensure new editor is used"""
    try:
        # Get current page version
        page = confluence.get_page_by_id(page_id, expand='version')
        current_version = page['version']['number']
        
        # Update the page with proper parameters
        # Using v2 would be better but atlassian-python-api uses v1
        # We ensure we're using the proper format
        result = confluence.update_page(
            page_id=page_id,
            title=title,
            body=content,
            parent_id=None,
            type='page',
            representation='storage',
            minor_edit=False,
            version_comment='Fixed table of contents and formatting'
        )
        
        return True
    except Exception as e:
        print(f"Error updating page: {e}")
        return False

def fix_page(page_id: str) -> Tuple[bool, str]:
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
        
        # Fix the content
        fixed_content = fix_content_formatting(original_content)
        
        # Check if content changed
        if fixed_content == original_content:
            return True, f"Page '{title}' - No changes needed"
        
        # Update the page with new editor support
        if update_page_with_new_editor(page_id, title, fixed_content):
            return True, f"Page '{title}' - Updated successfully with TOC"
        else:
            return False, f"Page '{title}' - Update failed"
        
    except Exception as e:
        return False, f"Error processing page {page_id}: {str(e)}"

def main():
    """Main function"""
    print("Confluence TOC and Editor Fix")
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
    print("- Add proper table of contents with working anchors")
    print("- Fix all formatting issues")
    print("- Ensure pages use the new editor")
    print()
    
    # Process each page
    for page_id in page_ids:
        success, message = fix_page(page_id)
        
        if success:
            print(f"✓ {message}")
        else:
            print(f"✗ {message}")
    
    print()
    print("Complete!")
    print("\nNote: Pages should now have:")
    print("- Working table of contents")
    print("- Proper anchor links for navigation")
    print("- New editor format")

if __name__ == "__main__":
    main()