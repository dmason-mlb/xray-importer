#!/usr/bin/env python3
"""
Analyze Confluence document 4904878140 structure to identify formatting inconsistencies
and verify test case content for Xray remediation validation.
"""

import os
import sys
import json
import re
from pathlib import Path
from collections import defaultdict

# Add confluence-tool scripts to path
sys.path.append('/Users/douglas.mason/Documents/GitHub/confluence-tool/scripts')

from confluence_client import ConfluenceClient
from config import get_config

def analyze_heading_structure(content):
    """Analyze heading structure and identify inconsistencies."""
    heading_analysis = {
        'h1': [], 'h2': [], 'h3': [], 'h4': [], 'h5': [], 'h6': []
    }
    
    # Find all headings
    for level in range(1, 7):
        pattern = rf'<h{level}[^>]*>(.*?)</h{level}>'
        matches = re.findall(pattern, content, re.DOTALL)
        for match in matches:
            clean_text = re.sub(r'<[^>]+>', '', match).strip()
            heading_analysis[f'h{level}'].append(clean_text)
    
    return heading_analysis

def find_api_test_cases(content):
    """Find all API test cases and their heading levels."""
    api_tests = []
    
    # Look for API test cases in different heading levels
    patterns = [
        (3, r'<h3[^>]*>.*?(API-[^<\s]+).*?</h3>'),
        (4, r'<h4[^>]*>.*?(API-[^<\s]+).*?</h4>'),
        (5, r'<h5[^>]*>.*?(API-[^<\s]+).*?</h5>'),
        (6, r'<h6[^>]*>.*?(API-[^<\s]+).*?</h6>'),
    ]
    
    for level, pattern in patterns:
        matches = re.findall(pattern, content, re.DOTALL)
        for match in matches:
            test_id = match.strip().rstrip(':')
            api_tests.append({
                'id': test_id,
                'heading_level': level,
                'raw_match': match
            })
    
    return api_tests

def analyze_parameterized_instances(content, api_tests):
    """Analyze test case content to identify parameterized instances."""
    parameterized_instances = []
    
    for test in api_tests:
        test_id = test['id']
        
        # Extract content section for this test
        level = test['heading_level']
        next_level_pattern = rf'<h{level}[^>]*>.*?{re.escape(test_id)}.*?</h{level}>(.*?)(?=<h[{level}][^>]*>.*?API-|$)'
        
        section_match = re.search(next_level_pattern, content, re.DOTALL)
        if section_match:
            section_content = section_match.group(1)
            
            # Look for indicators of parameterized instances
            # 1. Multiple table rows with different test data
            # 2. Lists of test scenarios
            # 3. Explicit mentions of "invalid" test cases (like API-003)
            
            # Check for table-based parameterization
            table_match = re.search(r'<table[^>]*>(.*?)</table>', section_content, re.DOTALL)
            if table_match:
                table_content = table_match.group(1)
                rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_content, re.DOTALL)
                
                # Look for multiple test scenarios in rows
                scenario_count = 0
                for row in rows:
                    if re.search(r'invalid|error|fail|test case|scenario', row.lower()):
                        scenario_count += 1
                
                if scenario_count > 1:
                    parameterized_instances.append({
                        'base_test_id': test_id,
                        'instance_count': scenario_count,
                        'type': 'table_based',
                        'content_preview': table_content[:200] + '...' if len(table_content) > 200 else table_content
                    })
            
            # Check for list-based parameterization
            list_items = re.findall(r'<li[^>]*>(.*?)</li>', section_content, re.DOTALL)
            if len(list_items) > 2:  # More than 2 list items might indicate parameterization
                parameterized_instances.append({
                    'base_test_id': test_id,
                    'instance_count': len(list_items),
                    'type': 'list_based',
                    'content_preview': str(list_items[:3]) + '...' if len(list_items) > 3 else str(list_items)
                })
    
    return parameterized_instances

def compare_with_json(api_tests, json_file_path):
    """Compare document inventory with extracted JSON."""
    with open(json_file_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    json_test_ids = set(test['testId'] for test in json_data['tests'])
    doc_test_ids = set(test['id'] for test in api_tests)
    
    comparison = {
        'json_count': len(json_test_ids),
        'document_count': len(doc_test_ids),
        'missing_from_json': doc_test_ids - json_test_ids,
        'missing_from_document': json_test_ids - doc_test_ids,
        'common_tests': json_test_ids & doc_test_ids
    }
    
    return comparison

def main():
    """Main analysis function."""
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
        print()
        
        # Save raw content for inspection
        content_file = Path(__file__).parent / "confluence_raw_content.html"
        with open(content_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Raw content saved to: {content_file}")
        print()
        
        # Analyze heading structure
        print("=== HEADING STRUCTURE ANALYSIS ===")
        heading_analysis = analyze_heading_structure(content)
        
        for level, headings in heading_analysis.items():
            if headings:
                print(f"{level.upper()} headings ({len(headings)}):")
                for i, heading in enumerate(headings, 1):
                    print(f"  {i}. {heading[:100]}{'...' if len(heading) > 100 else ''}")
                print()
        
        # Find API test cases
        print("=== API TEST CASES INVENTORY ===")
        api_tests = find_api_test_cases(content)
        
        # Group by heading level
        by_level = defaultdict(list)
        for test in api_tests:
            by_level[test['heading_level']].append(test)
        
        print(f"Total API test cases found: {len(api_tests)}")
        for level, tests in sorted(by_level.items()):
            print(f"  H{level} level: {len(tests)} tests")
            for test in sorted(tests, key=lambda x: x['id']):
                print(f"    - {test['id']}")
        print()
        
        # Check for duplicate test IDs
        test_ids = [test['id'] for test in api_tests]
        duplicates = [test_id for test_id in set(test_ids) if test_ids.count(test_id) > 1]
        if duplicates:
            print(f"⚠️  DUPLICATE TEST IDs FOUND: {duplicates}")
        else:
            print("✓ No duplicate test IDs found")
        print()
        
        # Analyze parameterized instances
        print("=== PARAMETERIZED INSTANCES ANALYSIS ===")
        parameterized_instances = analyze_parameterized_instances(content, api_tests)
        
        if parameterized_instances:
            print(f"Found {len(parameterized_instances)} potential parameterized instances:")
            for instance in parameterized_instances:
                print(f"  - {instance['base_test_id']}: {instance['instance_count']} instances ({instance['type']})")
                print(f"    Preview: {instance['content_preview'][:100]}...")
        else:
            print("No clear parameterized instances found in content structure")
        print()
        
        # Compare with JSON
        print("=== JSON COMPARISON ===")
        json_file = Path(__file__).parent / "api_tests_xray.json"
        if json_file.exists():
            comparison = compare_with_json(api_tests, json_file)
            
            print(f"Document test count: {comparison['document_count']}")
            print(f"JSON test count: {comparison['json_count']}")
            print(f"Common tests: {len(comparison['common_tests'])}")
            
            if comparison['missing_from_json']:
                print(f"Missing from JSON ({len(comparison['missing_from_json'])}): {sorted(comparison['missing_from_json'])}")
            
            if comparison['missing_from_document']:
                print(f"Missing from document ({len(comparison['missing_from_document'])}): {sorted(comparison['missing_from_document'])}")
            
            if comparison['document_count'] == comparison['json_count'] and not comparison['missing_from_json']:
                print("✓ Perfect parity between document and JSON")
            else:
                print("⚠️  Parity issues detected")
        else:
            print(f"JSON file not found: {json_file}")
        print()
        
        # Summary and recommendations
        print("=== ANALYSIS SUMMARY ===")
        unique_test_ids = set(test['id'] for test in api_tests)
        print(f"Total unique API test IDs: {len(unique_test_ids)}")
        
        # Check heading consistency
        heading_levels_used = set(test['heading_level'] for test in api_tests)
        if len(heading_levels_used) > 1:
            print(f"⚠️  INCONSISTENT HEADING LEVELS: {sorted(heading_levels_used)}")
            print("   Recommendation: Normalize all API test cases to H3 level")
        else:
            print(f"✓ Consistent heading level: H{list(heading_levels_used)[0]}")
        
        # Expected vs actual counts
        expected_base_tests = 55
        expected_total_instances = 66
        
        if len(unique_test_ids) == expected_base_tests:
            print(f"✓ Expected {expected_base_tests} base test IDs found")
        else:
            print(f"⚠️  Expected {expected_base_tests} base test IDs, found {len(unique_test_ids)}")
        
        total_parameterized = sum(instance['instance_count'] for instance in parameterized_instances)
        if total_parameterized >= (expected_total_instances - expected_base_tests):
            print(f"✓ Sufficient parameterized instances found: {total_parameterized}")
        else:
            print(f"⚠️  Expected {expected_total_instances - expected_base_tests} parameterized instances, found {total_parameterized}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()