#!/usr/bin/env python3
"""
Fix Confluence code blocks specifically
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

def extract_and_fix_code_blocks(content: str) -> str:
    """Extract code blocks, fix their content, and rebuild the page"""
    
    # First, let's find all the code blocks and their content
    code_blocks = []
    
    # Pattern to match code blocks
    pattern = r'<ac:structured-macro[^>]+ac:name="code"[^>]*>.*?</ac:structured-macro>'
    
    # Extract all code blocks
    for match in re.finditer(pattern, content, re.DOTALL):
        code_blocks.append(match.group(0))
    
    # Process each code block
    fixed_content = content
    
    for i, block in enumerate(code_blocks):
        # Extract the CDATA content
        cdata_match = re.search(r'<!\[CDATA\[(.*?)\]\]>', block, re.DOTALL)
        if cdata_match:
            cdata_content = cdata_match.group(1)
            
            # Check if this block has leaked content
            if any(tag in cdata_content for tag in ['<h1>', '<h2>', '<h3>', '<strong>', '<code>']):
                # This is a broken block - extract only the actual code
                
                # For the prerequisites block
                if 'export XRAY_CLIENT' in cdata_content:
                    # Extract just the export commands
                    fixed_cdata = '''# 1. Create XRAY API Key in Global Settings
# 2. Set environment variables
export XRAY_CLIENT="your_client_id"
export XRAY_SECRET="your_client_secret"
export JIRA_PROJECT_KEY="YOUR_PROJECT"
export JIRA_PROJECT_ID="10000"
# 3. Install dependencies
pip install requests python-dotenv pandas tenacity'''
                    
                    # Create the fixed block
                    fixed_block = f'''<ac:structured-macro ac:name="code" ac:schema-version="1">
<ac:parameter ac:name="language">bash</ac:parameter>
<ac:plain-text-body><![CDATA[{fixed_cdata}]]></ac:plain-text-body>
</ac:structured-macro>'''
                    
                    # Replace in content
                    fixed_content = fixed_content.replace(block, fixed_block)
                    
                    # Now add the leaked content after the code block
                    insert_pos = fixed_content.find(fixed_block) + len(fixed_block)
                    leaked_content = '''
<h2>Authentication Process</h2>
<h3>Step 1: Obtain Authentication Token</h3>
<p><strong>Endpoint</strong>: <code>https://xray.cloud.getxray.app/api/v2/authenticate</code></p>
<p><strong>Method</strong>: <code>POST</code></p>
<p><strong>Content-Type</strong>: <code>application/json</code></p>
<p><strong>Request Body</strong>:</p>'''
                    
                    fixed_content = fixed_content[:insert_pos] + leaked_content + fixed_content[insert_pos:]
                
                # For other blocks with HTML tags
                elif '<strong>' in cdata_content or '<h' in cdata_content:
                    # This block has HTML that shouldn't be there
                    # Extract the part before the HTML
                    html_start = min(
                        cdata_content.find('<') if '<' in cdata_content else len(cdata_content),
                        len(cdata_content)
                    )
                    
                    if html_start > 0:
                        clean_code = cdata_content[:html_start].strip()
                    else:
                        clean_code = ''
                    
                    if clean_code:
                        # Get the language
                        lang_match = re.search(r'ac:parameter ac:name="language">([^<]+)<', block)
                        language = lang_match.group(1) if lang_match else 'text'
                        
                        # Create clean block
                        fixed_block = f'''<ac:structured-macro ac:name="code" ac:schema-version="1">
<ac:parameter ac:name="language">{language}</ac:parameter>
<ac:plain-text-body><![CDATA[{clean_code}]]></ac:plain-text-body>
</ac:structured-macro>'''
                        
                        fixed_content = fixed_content.replace(block, fixed_block)
    
    # Fix the JSON code block with escaped quotes
    fixed_content = re.sub(
        r'&quot;client_id&quot;:\s*&quot;([^&]+)&quot;',
        r'"client_id": "\1"',
        fixed_content
    )
    fixed_content = re.sub(
        r'&quot;client_secret&quot;:\s*&quot;([^&]+)&quot;',
        r'"client_secret": "\1"',
        fixed_content
    )
    
    # Fix other HTML entities
    fixed_content = fixed_content.replace('&lt;h1&gt;', '<h1>')
    fixed_content = fixed_content.replace('&lt;/h1&gt;', '</h1>')
    fixed_content = fixed_content.replace('&lt;h2&gt;', '<h2>')
    fixed_content = fixed_content.replace('&lt;/h2&gt;', '</h2>')
    fixed_content = fixed_content.replace('&lt;h3&gt;', '<h3>')
    fixed_content = fixed_content.replace('&lt;/h3&gt;', '</h3>')
    fixed_content = fixed_content.replace('&quot;', '"')
    
    # Fix the bash code blocks that should be separate
    # Find sections that look like "# Using a JSON file" followed by curl commands
    curl_sections = [
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
    
    for title, code in curl_sections:
        # Remove the h1 tags and create proper sections
        fixed_content = re.sub(
            f'<h1>{title}</h1>\n{re.escape(code)}',
            f'<h3>{title}</h3>\n<ac:structured-macro ac:name="code" ac:schema-version="1">\n<ac:parameter ac:name="language">bash</ac:parameter>\n<ac:plain-text-body><![CDATA[{code}]]></ac:plain-text-body>\n</ac:structured-macro>',
            fixed_content
        )
    
    # Fix the "Bearer ${token}" template literal
    fixed_content = re.sub(
        r"'Authorization': Bearer \$\{token\}",
        "'Authorization': `Bearer ${token}`",
        fixed_content
    )
    
    # Clean up empty paragraphs
    fixed_content = re.sub(r'<p>\s*</p>', '', fixed_content)
    
    return fixed_content

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
        
        # Apply fixes
        fixed_content = extract_and_fix_code_blocks(original_content)
        
        # Update the page
        confluence.update_page(
            page_id=page_id,
            title=title,
            body=fixed_content,
            type='page',
            representation='storage',
            minor_edit=False,
            version_comment='Fixed code blocks and formatting'
        )
        
        return True, f"Page '{title}' - Fixed code blocks"
        
    except Exception as e:
        return False, f"Error processing page {page_id}: {str(e)}"

def main():
    """Main function"""
    print("Confluence Code Block Fix")
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
    print("This will fix:")
    print("- Code blocks with leaked HTML content")
    print("- HTML entities in content")
    print("- Proper code block formatting")
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