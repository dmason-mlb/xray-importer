#!/usr/bin/env python3
"""
Final comprehensive fix for Confluence page formatting issues
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

def fix_broken_code_blocks(content: str) -> str:
    """Fix code blocks where content leaked outside CDATA"""
    
    # Pattern to find broken code blocks
    # Look for code macro that ends with ]]></ac:plain-text-body></ac:structured-macro>
    # followed by a language name and then code
    pattern = r'(</ac:plain-text-body></ac:structured-macro>)\s*(python|bash|javascript|json|graphql|text)\s*\n([^<]+?)(?=<)'
    
    def replace_broken_block(match):
        # Extract the language and code
        closing_tag = match.group(1)
        language = match.group(2)
        code = match.group(3).rstrip()
        
        # Create a new proper code block
        new_block = f'</ac:structured-macro>\n<ac:structured-macro ac:name="code" ac:schema-version="1">'
        new_block += f'<ac:parameter ac:name="language">{language}</ac:parameter>'
        new_block += f'<ac:plain-text-body><![CDATA[{code}]]></ac:plain-text-body></ac:structured-macro>'
        
        return new_block
    
    content = re.sub(pattern, replace_broken_block, content, flags=re.MULTILINE | re.DOTALL)
    
    return content

def fix_content_formatting(content: str) -> str:
    """Comprehensive fix for all formatting issues"""
    
    # Step 1: Fix broken code blocks first
    content = fix_broken_code_blocks(content)
    
    # Step 2: Remove all empty paragraph tags
    content = re.sub(r'<p>\s*</p>', '', content)
    
    # Step 3: Fix headers that shouldn't be in the middle of code blocks
    # Look for headers inside CDATA sections and escape them
    def protect_cdata_content(match):
        cdata_content = match.group(1)
        # Escape any HTML tags inside CDATA
        cdata_content = cdata_content.replace('<h1>', '&lt;h1&gt;').replace('</h1>', '&lt;/h1&gt;')
        cdata_content = cdata_content.replace('<h2>', '&lt;h2&gt;').replace('</h2>', '&lt;/h2&gt;')
        cdata_content = cdata_content.replace('<h3>', '&lt;h3&gt;').replace('</h3>', '&lt;/h3&gt;')
        return f'<![CDATA[{cdata_content}]]>'
    
    content = re.sub(r'<!\[CDATA\[(.*?)\]\]>', protect_cdata_content, content, flags=re.DOTALL)
    
    # Step 4: Fix code blocks that have incorrect endings
    # Fix ``<code> patterns
    content = re.sub(r'``\s*<code>', '', content)
    content = re.sub(r'</code>\s*``', '', content)
    
    # Step 5: Fix inline code with backticks
    # But only outside of CDATA sections
    parts = re.split(r'(<!\[CDATA\[.*?\]\]>|<ac:structured-macro.*?</ac:structured-macro>)', content, flags=re.DOTALL)
    
    for i in range(len(parts)):
        if i % 2 == 0:  # Not inside CDATA or macro
            # Fix single backticks
            parts[i] = re.sub(r'(?<!`)`([^`\n]+)`(?!`)', r'<code>\1</code>', parts[i])
            # Remove any remaining backticks
            parts[i] = re.sub(r'``', '', parts[i])
            # Fix template literals that got broken
            parts[i] = re.sub(r'<code>\)\s*</code>', ')', parts[i])
    
    content = ''.join(parts)
    
    # Step 6: Fix JavaScript template literals
    # Look for patterns like Bearer ${token} or ${error.message}
    content = re.sub(r'Bearer \$\{token\}', 'Bearer ${token}', content)
    content = re.sub(r'Authentication failed: \$\{error\.message\}', '`Authentication failed: ${error.message}`', content)
    
    # Step 7: Clean up headers
    # Fix headers that appear after paragraphs
    content = re.sub(r'<p>\s*<h(\d)>(.+?)</h\1>\s*</p>', r'<h\1>\2</h\1>', content)
    
    # Step 8: Fix markdown headers
    content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)
    content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
    content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
    content = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', content, flags=re.MULTILINE)
    
    # Step 9: Fix links
    content = re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)', r'<a href="\2">\1</a>', content)
    content = re.sub(r'\[([^\]]+)\]\(#[^)]+\)', r'\1', content)
    content = re.sub(r'\[([^\]]+)\]\([^)]+\.md\)', r'\1', content)
    
    # Step 10: Clean up
    content = re.sub(r'\n\n\n+', '\n\n', content)
    
    return content

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

def main():
    """Main function"""
    print("Confluence Final Formatting Fix")
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

if __name__ == "__main__":
    main()