#!/usr/bin/env python3
"""
Fix Confluence page formatting issues - Version 2
More comprehensive fix for markdown to Confluence storage format conversion
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
    
    # Step 1: Remove all empty <p></p> tags
    content = re.sub(r'<p>\s*</p>', '', content)
    
    # Step 2: Fix headers inside <p> tags (move them outside)
    content = re.sub(r'<p>\s*<h(\d)>(.+?)</h\1>\s*</p>', r'<h\1>\2</h\1>', content)
    
    # Step 3: Fix markdown headers (must be more aggressive)
    # Look for headers even with content before/after on same line
    patterns = [
        (r'(?:^|\n)# ([^\n]+)', r'\n<h1>\1</h1>'),
        (r'(?:^|\n)## ([^\n]+)', r'\n<h2>\1</h2>'),
        (r'(?:^|\n)### ([^\n]+)', r'\n<h3>\1</h3>'),
        (r'(?:^|\n)#### ([^\n]+)', r'\n<h4>\1</h4>'),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    # Step 4: Fix code blocks that are outside of CDATA
    # First, protect existing proper code blocks
    protected_blocks = []
    def protect_block(match):
        protected_blocks.append(match.group(0))
        return f"__PROTECTED_BLOCK_{len(protected_blocks)-1}__"
    
    content = re.sub(
        r'<ac:structured-macro[^>]+ac:name="code"[^>]*>.*?</ac:structured-macro>',
        protect_block,
        content,
        flags=re.DOTALL
    )
    
    # Fix standalone language indicators (e.g., "python", "bash", "json")
    # These often appear after code blocks
    content = re.sub(r'\n(python|bash|javascript|json|graphql|text)\n', r'\n', content)
    
    # Step 5: Fix inline code backticks
    # Single backticks
    content = re.sub(r'(?<!`)`([^`\n]+)`(?!`)', r'<code>\1</code>', content)
    
    # Double backticks (often used for empty code)
    content = re.sub(r'``([^`]+)``', r'<code>\1</code>', content)
    
    # Step 6: Fix broken code tags
    content = re.sub(r'</code>([^<\n]+)<code>', r'\1', content)
    
    # Step 7: Clean up code block endings that leaked out
    content = re.sub(r'``\s*<code>', '<code>', content)
    content = re.sub(r'</code>\s*``', '</code>', content)
    content = re.sub(r'``\s*\n', '\n', content)
    
    # Step 8: Fix markdown links
    # External links
    content = re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)', r'<a href="\2">\1</a>', content)
    
    # Anchor links (just remove the link part)
    content = re.sub(r'\[([^\]]+)\]\(#[^)]+\)', r'\1', content)
    
    # File links (remove .md links)
    content = re.sub(r'\[([^\]]+)\]\([^)]+\.md\)', r'\1', content)
    
    # Step 9: Fix table of contents style lists
    # Convert numbered lists with links to proper lists without links
    content = re.sub(r'(\d+)\.\s*\[([^\]]+)\]\([^)]+\)', r'\1. \2', content)
    
    # Step 10: Restore protected blocks
    for i, block in enumerate(protected_blocks):
        content = content.replace(f"__PROTECTED_BLOCK_{i}__", block)
    
    # Step 11: Clean up extra whitespace
    content = re.sub(r'\n\n\n+', '\n\n', content)
    
    # Step 12: Fix any remaining stray code formatting
    # Remove backticks that might be at the start of lines
    content = re.sub(r'^\s*```\s*$', '', content, flags=re.MULTILINE)
    
    # Step 13: Fix template literal syntax in JavaScript
    content = re.sub(r'(?<!`)(`)\$\{([^}]+)\}(?<!`)', r'${\2}', content)
    
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
            # In dry run, show a preview of changes
            print(f"\nDry run for '{title}':")
            print("Sample of changes:")
            # Show first few differences
            for i, (orig, fixed) in enumerate(zip(original_content.split('\n')[:10], 
                                                 fixed_content.split('\n')[:10])):
                if orig != fixed:
                    print(f"  Original: {orig[:80]}...")
                    print(f"  Fixed:    {fixed[:80]}...")
                    if i >= 3:
                        break
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
    print("Confluence Formatting Fixer - Version 2")
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
    
    # Ask for dry run
    response = input("Do a dry run first? (y/n): ").lower()
    dry_run = response == 'y'
    
    if dry_run:
        print("\nDRY RUN MODE - No changes will be made")
    print()
    
    # Process each page
    success_count = 0
    error_count = 0
    
    for page_id in page_ids:
        success, message = fix_page(page_id, dry_run=dry_run)
        
        if success:
            print(f"✓ {message}")
            success_count += 1
        else:
            print(f"✗ {message}")
            error_count += 1
    
    print()
    print("=" * 50)
    print(f"Summary: {success_count} successful, {error_count} errors")
    
    if dry_run and success_count > 0:
        print("\nDry run complete. Run again without dry run to apply changes.")

if __name__ == "__main__":
    main()