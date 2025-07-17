#!/usr/bin/env python3
"""
Create Confluence documentation for XRAY GraphQL API
"""

import os
import requests
import json
from typing import Dict, Any

# Get credentials from environment
JIRA_BASE_URL = os.getenv('JIRA_BASE_URL')
JIRA_EMAIL = os.getenv('JIRA_EMAIL')
ATLASSIAN_TOKEN = os.getenv('ATLASSIAN_TOKEN')

# Confluence API endpoint
CONFLUENCE_API = f"{JIRA_BASE_URL}/wiki/rest/api/content"

# Parent page ID
PARENT_PAGE_ID = "4907925574"
SPACE_KEY = "~911651470"

def create_page(title: str, content: str, parent_id: str = None) -> Dict[str, Any]:
    """Create a Confluence page"""
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    auth = (JIRA_EMAIL, ATLASSIAN_TOKEN)
    
    data = {
        "type": "page",
        "title": title,
        "space": {"key": SPACE_KEY},
        "body": {
            "storage": {
                "value": content,
                "representation": "storage"
            }
        }
    }
    
    if parent_id:
        data["ancestors"] = [{"id": parent_id}]
    
    response = requests.post(
        CONFLUENCE_API,
        json=data,
        headers=headers,
        auth=auth
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"Created page: {title} (ID: {result['id']})")
        return result
    else:
        print(f"Failed to create page {title}: {response.status_code}")
        print(response.text)
        return None

def main():
    """Create all documentation pages"""
    
    # Create landing page content
    landing_content = """<h1>XRAY GraphQL API Documentation for Test Management</h1>

<ac:structured-macro ac:name="info" ac:schema-version="1" ac:macro-id="info-macro">
<ac:rich-text-body>
<p>This documentation provides comprehensive guidance for using XRAY's GraphQL API to create and manage test cases programmatically. It is designed for test engineers and automation teams looking to implement API-based test management workflows.</p>
</ac:rich-text-body>
</ac:structured-macro>

<h2>Overview</h2>

<p>The XRAY GraphQL API provides powerful capabilities for test management automation:</p>
<ul>
<li>Authenticate with XRAY's cloud API</li>
<li>Create hierarchical folder structures for test organization</li>
<li>Import test cases with proper labeling and categorization</li>
<li>Create test sets for execution planning</li>
<li>Handle batch operations with error recovery</li>
</ul>

<h2>Documentation Structure</h2>

<h3>1. <ac:link><ri:page ri:content-title="XRAY API Authentication Guide"/></ac:link></h3>
<ul>
<li>XRAY API authentication process</li>
<li>Token management and security</li>
<li>Best practices for credential handling</li>
<li>Code examples in multiple languages</li>
</ul>

<h3>2. <ac:link><ri:page ri:content-title="XRAY GraphQL API Reference"/></ac:link></h3>
<ul>
<li>Complete API reference for all GraphQL operations</li>
<li>Mutation and query documentation</li>
<li>Field descriptions and requirements</li>
<li>Request/response examples</li>
</ul>

<h3>3. <ac:link><ri:page ri:content-title="JIRA Field Requirements and Validation"/></ac:link></h3>
<ul>
<li>Detailed JIRA field specifications</li>
<li>Validation rules and constraints</li>
<li>Label taxonomy and conventions</li>
<li>Common issues and solutions</li>
</ul>

<h3>4. <ac:link><ri:page ri:content-title="Implementation Guide for Test Automation"/></ac:link></h3>
<ul>
<li>Production-ready implementation examples</li>
<li>Folder creation and management</li>
<li>Test import with batch processing</li>
<li>Test set creation and organization</li>
<li>Error handling and retry logic</li>
</ul>

<h2>Quick Start Guide</h2>

<h3>Prerequisites</h3>

<ac:structured-macro ac:name="code" ac:schema-version="1" ac:macro-id="code-macro">
<ac:parameter ac:name="language">bash</ac:parameter>
<ac:plain-text-body><![CDATA[# 1. Create XRAY API Key in Global Settings
# 2. Set environment variables
export XRAY_CLIENT="your_client_id"
export XRAY_SECRET="your_client_secret"
export JIRA_PROJECT_KEY="YOUR_PROJECT"
export JIRA_PROJECT_ID="10000"

# 3. Install dependencies
pip install requests python-dotenv pandas tenacity]]></ac:plain-text-body>
</ac:structured-macro>

<h3>Basic Usage Example</h3>

<ac:structured-macro ac:name="code" ac:schema-version="1" ac:macro-id="code-macro">
<ac:parameter ac:name="language">python</ac:parameter>
<ac:plain-text-body><![CDATA[import requests
import os

# Authenticate
def get_token():
    response = requests.post(
        "https://xray.cloud.getxray.app/api/v2/authenticate",
        json={
            "client_id": os.getenv("XRAY_CLIENT"),
            "client_secret": os.getenv("XRAY_SECRET")
        }
    )
    return response.text.strip('"')

# Create a test
def create_test(token, project_key, summary, steps):
    query = '''
    mutation CreateTest($jira: JSON!, $steps: [CreateStepInput!]) {
        createTest(jira: $jira, testType: {name: "Manual"}, steps: $steps) {
            test {
                issueId
                jira(fields: ["key"])
            }
        }
    }
    '''
    
    variables = {
        "jira": {
            "fields": {
                "project": {"key": project_key},
                "summary": summary,
                "issuetype": {"name": "Test"}
            }
        },
        "steps": steps
    }
    
    response = requests.post(
        "https://xray.cloud.getxray.app/api/v2/graphql",
        json={"query": query, "variables": variables},
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.json()]]></ac:plain-text-body>
</ac:structured-macro>

<h2>Test Organization Best Practices</h2>

<h3>Folder Structure</h3>
<p>Organize tests hierarchically by feature and component:</p>
<ac:structured-macro ac:name="code" ac:schema-version="1" ac:macro-id="code-macro">
<ac:parameter ac:name="language">text</ac:parameter>
<ac:plain-text-body><![CDATA[/Feature Name
  /Component A
    /Functional Tests
    /API Tests
  /Component B
    /Integration Tests
    /Performance Tests
  /Special Scenarios
    /Edge Cases
    /Error Handling]]></ac:plain-text-body>
</ac:structured-macro>

<h3>Label Taxonomy</h3>
<p>Use consistent labeling for test categorization:</p>
<ul>
<li><strong>Feature</strong>: @feature-name, @component-name</li>
<li><strong>Test Type</strong>: @functional, @api, @integration, @e2e</li>
<li><strong>Platform</strong>: @web, @mobile, @ios, @android</li>
<li><strong>Priority</strong>: @critical, @high, @medium, @low</li>
<li><strong>Execution</strong>: @smoke, @regression, @nightly, @release</li>
</ul>

<h3>Test Set Organization</h3>
<ul>
<li><strong>Smoke Tests</strong>: Quick validation suites (10-20 tests)</li>
<li><strong>Feature Tests</strong>: Complete feature coverage</li>
<li><strong>Regression Tests</strong>: Full regression suites</li>
<li><strong>Platform Tests</strong>: Platform-specific test sets</li>
</ul>

<h2>API Operations Summary</h2>

<h3>Core Mutations</h3>
<table>
<tbody>
<tr>
<th>Operation</th>
<th>Description</th>
<th>Use Case</th>
</tr>
<tr>
<td><code>createFolder</code></td>
<td>Create test repository folders</td>
<td>Organize tests hierarchically</td>
</tr>
<tr>
<td><code>createTest</code></td>
<td>Create new test cases</td>
<td>Import manual or automated tests</td>
</tr>
<tr>
<td><code>createTestSet</code></td>
<td>Create test sets</td>
<td>Group tests for execution</td>
</tr>
<tr>
<td><code>addTestsToFolder</code></td>
<td>Organize tests in folders</td>
<td>Categorize existing tests</td>
</tr>
<tr>
<td><code>addTestsToTestSet</code></td>
<td>Add tests to sets</td>
<td>Build execution suites</td>
</tr>
</tbody>
</table>

<h3>Core Queries</h3>
<table>
<tbody>
<tr>
<th>Operation</th>
<th>Description</th>
<th>Use Case</th>
</tr>
<tr>
<td><code>getFolder</code></td>
<td>Retrieve folder information</td>
<td>List tests in folder</td>
</tr>
<tr>
<td><code>getTest</code></td>
<td>Get test details</td>
<td>View test steps and metadata</td>
</tr>
<tr>
<td><code>getTestSet</code></td>
<td>Get test set information</td>
<td>View tests in execution set</td>
</tr>
</tbody>
</table>

<h2>Error Handling</h2>

<p>The API provides comprehensive error information:</p>
<ul>
<li>Authentication errors (401)</li>
<li>Validation errors (400)</li>
<li>Permission errors (403)</li>
<li>Rate limiting (429)</li>
<li>GraphQL-specific errors in response</li>
</ul>

<h2>Performance Considerations</h2>

<ul>
<li>Batch operations in groups of 10-50 items</li>
<li>Use GraphQL aliases for multiple operations</li>
<li>Implement retry logic with exponential backoff</li>
<li>Cache authentication tokens (valid ~24 hours)</li>
<li>Rate limit: 60 requests per minute</li>
</ul>

<h2>Additional Resources</h2>

<ul>
<li><a href="https://docs.getxray.app/display/XRAYCLOUD/GraphQL+API">Official XRAY GraphQL Documentation</a></li>
<li><a href="https://developer.atlassian.com/cloud/jira/platform/">JIRA Cloud REST API</a></li>
<li><a href="https://graphql.org/learn/best-practices/">GraphQL Best Practices</a></li>
<li><ac:link><ri:page ri:content-title="SDUI Testing Hub - Test Plans and Strategies"/></ac:link> - Parent documentation hub</li>
</ul>

<ac:structured-macro ac:name="info" ac:schema-version="1" ac:macro-id="info-macro">
<ac:rich-text-body>
<p><strong>Version:</strong> 1.0<br/>
<strong>Last Updated:</strong> January 2025<br/>
<strong>Maintainer:</strong> Test Engineering Team</p>
</ac:rich-text-body>
</ac:structured-macro>"""

    # Create landing page
    landing_page = create_page(
        "XRAY GraphQL API Documentation",
        landing_content,
        PARENT_PAGE_ID
    )
    
    if not landing_page:
        print("Failed to create landing page, aborting")
        return
    
    landing_page_id = landing_page['id']
    
    # Read content files
    # NOTE: Documentation moved to MLB-App/Test/sdui-test-docs repository
# Updated consolidated documentation is available at:
# https://github.com/your-org/MLB-App/tree/main/Test/sdui-test-docs
docs_path = "/Users/douglas.mason/Documents/GitHub/MLB-App/Test/sdui-test-docs"
    
    # Create child pages
    pages = [
        {
            "file": "01-Xray-GraphQL-Complete-Reference.md",
            "title": "XRAY API Authentication Guide",
            "convert": True
        },
        {
            "file": "02-Xray-Test-Automation-Strategy.md", 
            "title": "XRAY GraphQL API Reference",
            "convert": True
        },
        {
            "file": "03-jira-field-requirements.md",
            "title": "JIRA Field Requirements and Validation",
            "convert": True
        },
        {
            "file": "04-implementation-guide.md",
            "title": "Implementation Guide for Test Automation",
            "convert": True
        }
    ]
    
    for page_info in pages:
        file_path = os.path.join(docs_path, page_info['file'])
        
        # Read markdown content
        with open(file_path, 'r') as f:
            md_content = f.read()
        
        # Convert to Confluence storage format
        if page_info['convert']:
            # This is a simplified conversion - in production you'd use a proper markdown to confluence converter
            html_content = convert_markdown_to_confluence(md_content)
        else:
            html_content = md_content
        
        # Create child page
        create_page(page_info['title'], html_content, landing_page_id)

def convert_markdown_to_confluence(md_content: str) -> str:
    """Convert markdown to Confluence storage format - simplified version"""
    import re
    
    # Start with the content
    html = md_content
    
    # Convert headers
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    
    # Convert code blocks with language
    def replace_code_block(match):
        lang = match.group(1) or 'text'
        code = match.group(2)
        return f'''<ac:structured-macro ac:name="code" ac:schema-version="1">
<ac:parameter ac:name="language">{lang}</ac:parameter>
<ac:plain-text-body><![CDATA[{code}]]></ac:plain-text-body>
</ac:structured-macro>'''
    
    html = re.sub(r'```(\w+)?\n(.*?)\n```', replace_code_block, html, flags=re.DOTALL)
    
    # Convert inline code
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
    
    # Convert bold
    html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', html)
    
    # Convert lists
    lines = html.split('\n')
    new_lines = []
    in_list = False
    list_type = None
    
    for line in lines:
        if line.strip().startswith('- ') or line.strip().startswith('* '):
            if not in_list:
                new_lines.append('<ul>')
                in_list = True
                list_type = 'ul'
            new_lines.append(f'<li>{line.strip()[2:]}</li>')
        elif re.match(r'^\d+\. ', line.strip()):
            if not in_list or list_type != 'ol':
                if in_list:
                    new_lines.append(f'</{list_type}>')
                new_lines.append('<ol>')
                in_list = True
                list_type = 'ol'
            new_lines.append(f'<li>{re.sub(r"^\d+\. ", "", line.strip())}</li>')
        else:
            if in_list:
                new_lines.append(f'</{list_type}>')
                in_list = False
                list_type = None
            new_lines.append(line)
    
    if in_list:
        new_lines.append(f'</{list_type}>')
    
    html = '\n'.join(new_lines)
    
    # Convert tables
    def convert_table(match):
        table_text = match.group(0)
        lines = table_text.strip().split('\n')
        
        # Build table
        table_html = '<table><tbody>'
        
        for i, line in enumerate(lines):
            if '---' in line:
                continue
            
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            
            if i == 0:
                table_html += '<tr>'
                for cell in cells:
                    table_html += f'<th>{cell}</th>'
                table_html += '</tr>'
            else:
                table_html += '<tr>'
                for cell in cells:
                    table_html += f'<td>{cell}</td>'
                table_html += '</tr>'
        
        table_html += '</tbody></table>'
        return table_html
    
    # Find and convert tables
    table_pattern = r'\|.+\|(?:\n\|[-\s|]+\|)?\n(?:\|.+\|\n?)+'
    html = re.sub(table_pattern, convert_table, html, flags=re.MULTILINE)
    
    # Convert paragraphs
    html = re.sub(r'\n\n(.+)\n\n', r'\n\n<p>\1</p>\n\n', html)
    
    # Clean up extra newlines
    html = re.sub(r'\n{3,}', '\n\n', html)
    
    return html

if __name__ == "__main__":
    main()