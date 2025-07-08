#!/usr/bin/env python3
"""
Comprehensive fix for Confluence formatting issues including editor mode
"""

import os
import re
from atlassian import Confluence
from typing import Dict, List, Tuple
import html

# Initialize Confluence client
confluence = Confluence(
    url=os.getenv('JIRA_BASE_URL'),
    username=os.getenv('JIRA_EMAIL'),
    password=os.getenv('ATLASSIAN_TOKEN'),
    cloud=True
)

def fix_html_entities(content: str) -> str:
    """Fix HTML entities that should be rendered as actual characters"""
    
    # First, protect content inside CDATA sections
    cdata_blocks = []
    def protect_cdata(match):
        cdata_blocks.append(match.group(0))
        return f"__CDATA_BLOCK_{len(cdata_blocks)-1}__"
    
    content = re.sub(r'<!\[CDATA\[.*?\]\]>', protect_cdata, content, flags=re.DOTALL)
    
    # Fix common HTML entities outside of CDATA
    content = re.sub(r'&lt;', '<', content)
    content = re.sub(r'&gt;', '>', content)
    content = re.sub(r'&amp;', '&', content)
    content = re.sub(r'&quot;', '"', content)
    
    # Restore CDATA blocks
    for i, block in enumerate(cdata_blocks):
        content = content.replace(f"__CDATA_BLOCK_{i}__", block)
    
    return content

def fix_code_blocks_comprehensively(content: str) -> str:
    """Fix all code block issues"""
    
    # Pattern 1: Fix broken authentication process sections
    content = re.sub(
        r'&lt;h2&gt;Authentication Process&lt;/h2&gt;\s*&lt;h3&gt;Step 1: Obtain Authentication Token&lt;/h3&gt;',
        '<h2>Authentication Process</h2>\n<h3>Step 1: Obtain Authentication Token</h3>',
        content
    )
    
    # Pattern 2: Fix endpoint/method/content-type sections
    content = re.sub(
        r'<strong>Endpoint</strong>:\s*</code>([^<]+)<code>',
        '<strong>Endpoint</strong>: <code>\\1</code>',
        content
    )
    
    content = re.sub(
        r'<strong>Method</strong>:\s*</code>([^<]+)<code>',
        '<strong>Method</strong>: <code>\\1</code>',
        content
    )
    
    content = re.sub(
        r'<strong>Content-Type</strong>:\s*</code>([^<]+)<code>',
        '<strong>Content-Type</strong>: <code>\\1</code>',
        content
    )
    
    # Pattern 3: Fix malformed headers in code blocks
    # Look for patterns like <h1>text</h1> inside what should be comments
    content = re.sub(
        r'<h1>(\d+\. [^<]+)</h1>',
        '# \\1',
        content
    )
    
    # Pattern 4: Fix code blocks that have leaked content
    # Find bash/python/etc. that appear after a code block ends
    pattern = r'</ac:plain-text-body></ac:structured-macro>\s*\n*(bash|python|javascript|json|graphql|text)\s*\n'
    content = re.sub(pattern, '</ac:plain-text-body></ac:structured-macro>\n', content)
    
    return content

def fix_prerequisites_section(content: str) -> str:
    """Fix the prerequisites section specifically"""
    
    # Fix the prerequisites code block
    prerequisites_pattern = r'(Prerequisites</h[23]>)(.*?)(<ac:structured-macro[^>]+ac:name="code"[^>]*>)'
    
    def fix_prereq(match):
        header = match.group(1)
        between = match.group(2)
        code_start = match.group(3)
        
        # Clean up the between content
        between = re.sub(r'<p>\s*</p>', '', between)
        between = between.strip()
        
        return header + '\n' + code_start
    
    content = re.sub(prerequisites_pattern, fix_prereq, content, flags=re.DOTALL)
    
    return content

def ensure_proper_code_blocks(content: str) -> str:
    """Ensure all code blocks are properly formatted"""
    
    # Find all code blocks and ensure they're properly formatted
    code_block_pattern = r'<ac:structured-macro[^>]+ac:name="code"[^>]*>.*?</ac:structured-macro>'
    
    def validate_code_block(match):
        block = match.group(0)
        
        # Ensure the block has proper structure
        if '<ac:parameter ac:name="language">' not in block:
            # Try to detect language
            if 'export' in block or 'curl' in block:
                lang = 'bash'
            elif 'import' in block or 'def' in block:
                lang = 'python'
            elif '{' in block and '"' in block:
                lang = 'json'
            else:
                lang = 'text'
            
            # Reconstruct the block
            content_match = re.search(r'<ac:plain-text-body><!\[CDATA\[(.*?)\]\]></ac:plain-text-body>', block, re.DOTALL)
            if content_match:
                code_content = content_match.group(1)
                new_block = f'<ac:structured-macro ac:name="code" ac:schema-version="1">'
                new_block += f'<ac:parameter ac:name="language">{lang}</ac:parameter>'
                new_block += f'<ac:plain-text-body><![CDATA[{code_content}]]></ac:plain-text-body>'
                new_block += '</ac:structured-macro>'
                return new_block
        
        return block
    
    content = re.sub(code_block_pattern, validate_code_block, content, flags=re.DOTALL)
    
    return content

def fix_simple_toc(content: str) -> str:
    """Ensure TOC is simple and properly formatted"""
    
    # Remove any existing TOCs
    content = re.sub(
        r'<ac:structured-macro[^>]+ac:name="toc"[^>]*>.*?</ac:structured-macro>',
        '',
        content,
        flags=re.DOTALL
    )
    
    # Add a simple TOC after the first h1
    toc = '''<ac:structured-macro ac:name="toc" ac:schema-version="1" ac:macro-id="toc">
<ac:parameter ac:name="maxLevel">2</ac:parameter>
<ac:parameter ac:name="minLevel">2</ac:parameter>
<ac:parameter ac:name="style">square</ac:parameter>
<ac:parameter ac:name="indent">20px</ac:parameter>
<ac:parameter ac:name="printable">false</ac:parameter>
</ac:structured-macro>'''
    
    h1_match = re.search(r'</h1>', content)
    if h1_match:
        insert_pos = h1_match.end()
        content = (
            content[:insert_pos] + 
            '\n' + toc + '\n' + 
            content[insert_pos:]
        )
    
    return content

def fix_content_completely(content: str) -> str:
    """Apply all fixes in the correct order"""
    
    # Step 1: Fix HTML entities first
    content = fix_html_entities(content)
    
    # Step 2: Fix code blocks
    content = fix_code_blocks_comprehensively(content)
    
    # Step 3: Fix prerequisites section
    content = fix_prerequisites_section(content)
    
    # Step 4: Ensure proper code block formatting
    content = ensure_proper_code_blocks(content)
    
    # Step 5: Fix the TOC
    content = fix_simple_toc(content)
    
    # Step 6: Clean up empty paragraphs
    content = re.sub(r'<p>\s*</p>', '', content)
    
    # Step 7: Fix any remaining formatting issues
    # Remove stray closing tags
    content = re.sub(r'</code>\s*</code>', '</code>', content)
    content = re.sub(r'<code>\s*<code>', '<code>', content)
    
    # Fix inline code that's broken
    content = re.sub(r'</code>([^<]+)<code>', '\\1', content)
    
    # Clean up extra whitespace
    content = re.sub(r'\n\n\n+', '\n\n', content)
    
    return content

def update_page_new_editor(page_id: str, title: str, content: str) -> bool:
    """Update page with parameters to ensure new editor"""
    try:
        # Get current page version
        page = confluence.get_page_by_id(page_id, expand='version')
        current_version = page['version']['number']
        
        # Update with specific parameters for new editor
        result = confluence.update_page(
            page_id=page_id,
            title=title,
            body=content,
            type='page',
            representation='storage',
            minor_edit=False,
            version_comment='Comprehensive formatting fix - removed HTML entities, fixed code blocks, simplified TOC'
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
        
        # Apply comprehensive fixes
        fixed_content = fix_content_completely(original_content)
        
        # Update the page
        if update_page_new_editor(page_id, title, fixed_content):
            return True, f"Page '{title}' - Fixed comprehensively"
        else:
            return False, f"Page '{title}' - Update failed"
        
    except Exception as e:
        return False, f"Error processing page {page_id}: {str(e)}"

def main():
    """Main function"""
    print("Confluence Comprehensive Fix")
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
    print("- Fix HTML entities (&lt; &gt; etc)")
    print("- Fix code block formatting")
    print("- Fix prerequisites section")
    print("- Ensure simple TOC (top-level only)")
    print("- Clean up formatting issues")
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