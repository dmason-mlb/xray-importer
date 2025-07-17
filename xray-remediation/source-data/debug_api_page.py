#!/usr/bin/env python3
"""
Debug script to examine the structure of the API test Confluence page.
"""

import sys
import re

# Add confluence-tool scripts to path
sys.path.append('/Users/douglas.mason/Documents/GitHub/confluence-tool/scripts')

from confluence_client import ConfluenceClient
from config import get_config

def main():
    """Debug the API test page structure."""
    config = get_config()
    if not config:
        sys.exit(1)
    
    client = ConfluenceClient(config['domain'], config['email'], config['api_token'])
    page_id = "4904878140"
    
    print(f"Fetching Confluence page {page_id}...")
    
    try:
        page = client.get_page(page_id, expand=['body.storage'])
        content = page['body']['storage']['value']
        
        print(f"Page title: {page['title']}")
        print(f"Page version: {page['version']['number']}")
        print(f"Content length: {len(content)} characters")
        
        # Save raw content to file for inspection
        with open('api_page_content.html', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("Saved raw content to api_page_content.html")
        
        # Look for different heading patterns
        print("\nLooking for heading patterns...")
        
        # Check for h1, h2, h3 headings
        for level in [1, 2, 3, 4]:
            headings = re.findall(rf'<h{level}[^>]*>(.*?)</h{level}>', content, re.DOTALL)
            if headings:
                print(f"H{level} headings found: {len(headings)}")
                for i, heading in enumerate(headings):
                    clean_heading = re.sub(r'<[^>]+>', '', heading).strip()
                    print(f"  {i+1}. {clean_heading}")
        
        # Look for API test case patterns
        print("\nLooking for API test case patterns...")
        
        # Different possible API test ID patterns
        patterns = [
            r'API-\d+',
            r'API-[A-Z]+-\d+',
            r'API-[A-Z]{2,4}-\d+',
            r'API-[A-Z]{2,4}\d+',
            r'Test.*?API-\d+',
            r'Test.*?API-[A-Z]+-\d+',
        ]
        
        all_matches = set()
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                print(f"Pattern '{pattern}' found {len(matches)} times:")
                for match in matches:
                    all_matches.add(match.upper())
                    print(f"  - {match}")
        
        print(f"\nTotal unique API test IDs found: {len(all_matches)}")
        print("Sorted list:")
        for api_id in sorted(all_matches):
            print(f"  - {api_id}")
        
        # Look for sections with test content
        print("\nLooking for test sections...")
        
        # Find sections that contain API test IDs
        test_sections = re.findall(r'<h3[^>]*>.*?(API-[^<\s]+).*?</h3>(.*?)(?=<h3[^>]*>.*?API-|$)', content, re.DOTALL)
        print(f"Found {len(test_sections)} test sections with h3 headings")
        
        for i, (test_id, section_content) in enumerate(test_sections[:10]):
            print(f"  {i+1}. {test_id}")
            # Show first 100 chars of content
            clean_content = re.sub(r'<[^>]+>', ' ', section_content).strip()
            preview = clean_content[:100].replace('\n', ' ')
            print(f"     Content: {preview}...")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()