#!/usr/bin/env python3
"""
Debug script to examine the structure of the functional test Confluence page.
"""

import sys
import re

# Add confluence-tool scripts to path
sys.path.append('/Users/douglas.mason/Documents/GitHub/confluence-tool/scripts')

from confluence_client import ConfluenceClient
from config import get_config

def main():
    """Debug the functional test page structure."""
    config = get_config()
    if not config:
        sys.exit(1)
    
    client = ConfluenceClient(config['domain'], config['email'], config['api_token'])
    page_id = "4904976484"
    
    print(f"Fetching Confluence page {page_id}...")
    
    try:
        page = client.get_page(page_id, expand=['body.storage'])
        content = page['body']['storage']['value']
        
        print(f"Page title: {page['title']}")
        print(f"Page version: {page['version']['number']}")
        print(f"Content length: {len(content)} characters")
        
        # Save raw content to file for inspection
        with open('functional_page_content.html', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("Saved raw content to functional_page_content.html")
        
        # Look for different heading patterns
        print("\nLooking for heading patterns...")
        
        # Check for h1, h2, h3 headings
        for level in [1, 2, 3, 4]:
            headings = re.findall(rf'<h{level}[^>]*>(.*?)</h{level}>', content, re.DOTALL)
            if headings:
                print(f"H{level} headings found: {len(headings)}")
                for i, heading in enumerate(headings[:5]):  # Show first 5
                    clean_heading = re.sub(r'<[^>]+>', '', heading).strip()
                    print(f"  {i+1}. {clean_heading}")
                if len(headings) > 5:
                    print(f"  ... and {len(headings) - 5} more")
        
        # Look for table structures
        tables = re.findall(r'<table[^>]*>(.*?)</table>', content, re.DOTALL)
        if tables:
            print(f"\nTables found: {len(tables)}")
            for i, table in enumerate(tables[:3]):  # Show first 3
                rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table, re.DOTALL)
                print(f"  Table {i+1}: {len(rows)} rows")
        
        # Look for list structures
        lists = re.findall(r'<ul[^>]*>(.*?)</ul>', content, re.DOTALL)
        if lists:
            print(f"\nUnordered lists found: {len(lists)}")
        
        ol_lists = re.findall(r'<ol[^>]*>(.*?)</ol>', content, re.DOTALL)
        if ol_lists:
            print(f"Ordered lists found: {len(ol_lists)}")
        
        # Look for test case patterns
        print("\nLooking for test case patterns...")
        
        # Different possible test ID patterns
        patterns = [
            r'FTC-\d+',
            r'TC-\d+',
            r'TEST-\d+',
            r'FUNC-\d+',
            r'F-\d+',
            r'Test Case \d+',
            r'Test \d+',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                print(f"Pattern '{pattern}' found {len(matches)} times:")
                for match in matches[:10]:  # Show first 10
                    print(f"  - {match}")
        
        # Look for keywords that might indicate test structure
        keywords = ['test', 'verify', 'check', 'validate', 'ensure', 'steps', 'expected', 'result']
        print("\nKeyword analysis:")
        for keyword in keywords:
            count = len(re.findall(keyword, content, re.IGNORECASE))
            print(f"  '{keyword}': {count} occurrences")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()