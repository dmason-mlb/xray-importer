#!/usr/bin/env python3
"""
Generic debug script to examine the structure of Confluence pages.
Usage: python debug_confluence_page.py <page_id>
"""

import sys
import re
from pathlib import Path

# Add confluence-tool scripts to path
sys.path.append('/Users/douglas.mason/Documents/GitHub/confluence-tool/scripts')

from confluence_client import ConfluenceClient
from config import get_config


def analyze_headings(content):
    """Analyze heading structure in the content."""
    print("\nAnalyzing heading patterns...")
    
    # Check for h1, h2, h3, h4 headings
    for level in [1, 2, 3, 4]:
        headings = re.findall(rf'<h{level}[^>]*>(.*?)</h{level}>', content, re.DOTALL)
        if headings:
            print(f"H{level} headings found: {len(headings)}")
            for i, heading in enumerate(headings[:5]):  # Show first 5
                clean_heading = re.sub(r'<[^>]+>', '', heading).strip()
                print(f"  {i+1}. {clean_heading}")
            if len(headings) > 5:
                print(f"  ... and {len(headings) - 5} more")


def analyze_test_patterns(content):
    """Analyze test case patterns in the content."""
    print("\nAnalyzing test case patterns...")
    
    # API test patterns
    api_patterns = [
        r'API-\d+',
        r'API-[A-Z]+-\d+',
        r'API-[A-Z]{2,4}-\d+',
        r'API-[A-Z]{2,4}\d+',
        r'Test.*?API-\d+',
        r'Test.*?API-[A-Z]+-\d+',
    ]
    
    # Functional test patterns
    functional_patterns = [
        r'FTC-\d+',
        r'TC-\d+',
        r'TEST-\d+',
        r'FUNC-\d+',
        r'F-\d+',
        r'Test Case \d+',
        r'Test \d+',
    ]
    
    all_patterns = api_patterns + functional_patterns
    all_matches = set()
    
    for pattern in all_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            print(f"Pattern '{pattern}' found {len(matches)} times:")
            for match in matches[:10]:  # Show first 10
                all_matches.add(match.upper())
                print(f"  - {match}")
    
    if all_matches:
        print(f"\nTotal unique test IDs found: {len(all_matches)}")
        print("Sorted list:")
        for test_id in sorted(all_matches):
            print(f"  - {test_id}")


def analyze_structure(content):
    """Analyze structural elements in the content."""
    print("\nAnalyzing document structure...")
    
    # Tables
    tables = re.findall(r'<table[^>]*>(.*?)</table>', content, re.DOTALL)
    if tables:
        print(f"Tables found: {len(tables)}")
        for i, table in enumerate(tables[:3]):  # Show first 3
            rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table, re.DOTALL)
            print(f"  Table {i+1}: {len(rows)} rows")
    
    # Lists
    ul_lists = re.findall(r'<ul[^>]*>(.*?)</ul>', content, re.DOTALL)
    if ul_lists:
        print(f"Unordered lists found: {len(ul_lists)}")
    
    ol_lists = re.findall(r'<ol[^>]*>(.*?)</ol>', content, re.DOTALL)
    if ol_lists:
        print(f"Ordered lists found: {len(ol_lists)}")


def analyze_keywords(content):
    """Analyze test-related keywords in the content."""
    print("\nKeyword analysis:")
    
    keywords = ['test', 'verify', 'check', 'validate', 'ensure', 'steps', 'expected', 'result']
    for keyword in keywords:
        count = len(re.findall(keyword, content, re.IGNORECASE))
        print(f"  '{keyword}': {count} occurrences")


def main():
    """Debug a Confluence page structure."""
    if len(sys.argv) != 2:
        print("Usage: python debug_confluence_page.py <page_id>")
        sys.exit(1)
    
    page_id = sys.argv[1]
    
    config = get_config()
    if not config:
        sys.exit(1)
    
    client = ConfluenceClient(config['domain'], config['email'], config['api_token'])
    
    print(f"Fetching Confluence page {page_id}...")
    
    try:
        page = client.get_page(page_id, expand=['body.storage'])
        content = page['body']['storage']['value']
        
        print(f"Page title: {page['title']}")
        print(f"Page version: {page['version']['number']}")
        print(f"Content length: {len(content)} characters")
        
        # Save raw content to file for inspection
        output_file = Path(f'page_{page_id}_content.html')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Saved raw content to {output_file}")
        
        # Perform various analyses
        analyze_headings(content)
        analyze_test_patterns(content)
        analyze_structure(content)
        analyze_keywords(content)
        
        # Look for test sections
        print("\nLooking for test sections...")
        
        # API test sections
        api_sections = re.findall(r'<h[34][^>]*>.*?(API-[^<\s]+).*?</h[34]>(.*?)(?=<h[34][^>]*>.*?API-|$)', content, re.DOTALL)
        if api_sections:
            print(f"Found {len(api_sections)} API test sections")
            for i, (test_id, section_content) in enumerate(api_sections[:5]):
                print(f"  {i+1}. {test_id}")
                clean_content = re.sub(r'<[^>]+>', ' ', section_content).strip()
                preview = clean_content[:100].replace('\n', ' ')
                print(f"     Content: {preview}...")
        
        # Functional test sections  
        func_sections = re.findall(r'<h3[^>]*>.*?(TC-[^<\s]+).*?</h3>(.*?)(?=<h3[^>]*>.*?TC-|$)', content, re.DOTALL)
        if func_sections:
            print(f"Found {len(func_sections)} functional test sections")
            for i, (test_id, section_content) in enumerate(func_sections[:5]):
                print(f"  {i+1}. {test_id}")
                clean_content = re.sub(r'<[^>]+>', ' ', section_content).strip()
                preview = clean_content[:100].replace('\n', ' ')
                print(f"     Content: {preview}...")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()