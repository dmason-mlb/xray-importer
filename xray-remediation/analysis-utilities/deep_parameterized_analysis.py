#!/usr/bin/env python3
"""
Deep analysis of parameterized instances in API test cases to understand
the true structure and identify the 11 parameterized instances mentioned by the user.
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

def analyze_test_case_structure(content, test_id):
    """Analyze the structure of a specific test case to understand parameterization."""
    
    # Find the test case section
    patterns = [
        rf'<h3[^>]*>.*?{re.escape(test_id)}[^<]*</h3>(.*?)(?=<h[23][^>]*>|$)',
        rf'<h4[^>]*>.*?{re.escape(test_id)}[^<]*</h4>(.*?)(?=<h[234][^>]*>|$)'
    ]
    
    section_content = ""
    for pattern in patterns:
        match = re.search(pattern, content, re.DOTALL)
        if match:
            section_content = match.group(1)
            break
    
    if not section_content:
        return None
    
    # Extract structured data
    analysis = {
        'test_id': test_id,
        'has_table': False,
        'table_rows': 0,
        'has_multiple_scenarios': False,
        'scenario_count': 0,
        'validation_steps': [],
        'test_variations': [],
        'content_preview': section_content[:500]
    }
    
    # Look for tables
    table_match = re.search(r'<table[^>]*>(.*?)</table>', section_content, re.DOTALL)
    if table_match:
        analysis['has_table'] = True
        table_content = table_match.group(1)
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_content, re.DOTALL)
        analysis['table_rows'] = len(rows)
        
        # Extract test data from table
        for row in rows:
            cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
            if len(cells) >= 2:
                key = re.sub(r'<[^>]+>', '', cells[0]).strip()
                value = re.sub(r'<[^>]+>', '', cells[1]).strip()
                if key and value:
                    analysis['test_variations'].append({
                        'parameter': key,
                        'value': value
                    })
    
    # Look for multiple test scenarios (often indicated by numbered lists or bullet points)
    list_items = re.findall(r'<li[^>]*>(.*?)</li>', section_content, re.DOTALL)
    if list_items:
        analysis['scenario_count'] = len(list_items)
        analysis['has_multiple_scenarios'] = len(list_items) > 2
        
        # Extract scenario descriptions
        for item in list_items:
            clean_item = re.sub(r'<[^>]+>', '', item).strip()
            if clean_item:
                analysis['validation_steps'].append(clean_item)
    
    # Look for specific parameterization patterns
    # Pattern 1: API-003 with multiple invalid test cases
    if test_id == 'API-003':
        invalid_patterns = re.findall(r'teamId=(\d+|[^&\s]+)', section_content)
        if invalid_patterns:
            analysis['test_variations'].extend([
                {'parameter': 'teamId', 'value': val} for val in invalid_patterns
            ])
    
    # Pattern 2: Language tests with different locales
    if test_id in ['API-004', 'API-005', 'API-006']:
        lang_match = re.search(r'lang=([a-z]{2})', section_content)
        if lang_match:
            analysis['test_variations'].append({
                'parameter': 'lang',
                'value': lang_match.group(1)
            })
    
    # Pattern 3: Game state tests with different states
    if test_id.startswith('API-GS-'):
        state_patterns = re.findall(r'"([A-Z]+)"', section_content)
        state_patterns.extend(re.findall(r'status[^:]*:\s*"([^"]+)"', section_content))
        if state_patterns:
            for state in set(state_patterns):
                analysis['test_variations'].append({
                    'parameter': 'gameState',
                    'value': state
                })
    
    return analysis

def identify_true_parameterized_instances(content):
    """Identify test cases that should be considered as having parameterized instances."""
    
    # Get all unique test IDs
    all_patterns = [
        r'<h3[^>]*>.*?(API-[^<\s]+).*?</h3>',
        r'<h4[^>]*>.*?(API-[^<\s]+).*?</h4>'
    ]
    
    test_ids = set()
    for pattern in all_patterns:
        matches = re.findall(pattern, content, re.DOTALL)
        for match in matches:
            test_ids.add(match.strip().rstrip(':'))
    
    # Analyze each test case
    parameterized_tests = []
    
    for test_id in sorted(test_ids):
        analysis = analyze_test_case_structure(content, test_id)
        if analysis:
            # Criteria for parameterized instances:
            # 1. Multiple explicit test variations in table
            # 2. Test cases with known parameterization (API-003 with invalid IDs)
            # 3. Tests with multiple specific validation scenarios
            
            is_parameterized = False
            instance_count = 1  # Base count
            
            # Check for explicit test variations
            if analysis['test_variations']:
                unique_variations = set()
                for var in analysis['test_variations']:
                    if var['parameter'] in ['teamId', 'lang', 'gameState']:
                        unique_variations.add(var['value'])
                
                if len(unique_variations) > 1:
                    is_parameterized = True
                    instance_count = len(unique_variations)
            
            # Special case: API-003 with invalid team IDs
            if test_id == 'API-003':
                # Look for specific invalid test cases mentioned in content
                invalid_cases = re.findall(r'teamId=(\d+|[^&\s]+)', analysis['content_preview'])
                if len(invalid_cases) > 1:
                    is_parameterized = True
                    instance_count = len(set(invalid_cases))
            
            # Special case: Language tests (API-004, API-005, API-006)
            if test_id in ['API-004', 'API-005', 'API-006']:
                # These are inherently parameterized by language
                is_parameterized = True
                instance_count = 1  # Each language is a separate instance
            
            # Special case: Game state tests with multiple states
            if test_id.startswith('API-GS-'):
                # Look for multiple game states mentioned
                states = set(re.findall(r'"([A-Z]+)"', analysis['content_preview']))
                if len(states) > 1:
                    is_parameterized = True
                    instance_count = len(states)
            
            if is_parameterized:
                parameterized_tests.append({
                    'test_id': test_id,
                    'instance_count': instance_count,
                    'total_instances': instance_count,  # Base + variations
                    'variations': analysis['test_variations'],
                    'validation_steps': len(analysis['validation_steps']),
                    'rationale': f"Found {instance_count} distinct parameter variations"
                })
    
    return parameterized_tests

def main():
    """Main analysis function."""
    config = get_config()
    if not config:
        sys.exit(1)
    
    client = ConfluenceClient(config['domain'], config['email'], config['api_token'])
    page_id = "4904878140"
    
    print("=== DEEP PARAMETERIZED INSTANCE ANALYSIS ===")
    print(f"Analyzing Confluence page {page_id} for true parameterized instances...")
    print()
    
    try:
        page = client.get_page(page_id, expand=['body.storage'])
        content = page['body']['storage']['value']
        
        # Identify true parameterized instances
        parameterized_tests = identify_true_parameterized_instances(content)
        
        print(f"Found {len(parameterized_tests)} test cases with parameterized instances:")
        print()
        
        total_instances = 0
        for test in parameterized_tests:
            print(f"• {test['test_id']}: {test['instance_count']} instances")
            print(f"  Rationale: {test['rationale']}")
            if test['variations']:
                variations_str = [f"{v['parameter']}={v['value']}" for v in test['variations'][:3]]
                print(f"  Variations: {variations_str}")
            print()
            total_instances += test['instance_count']
        
        print(f"Total parameterized instances: {total_instances}")
        print(f"Total base test cases: {len(set(t['test_id'] for t in parameterized_tests))}")
        
        # Expected analysis
        expected_total = 66
        expected_base = 55
        expected_parameterized = expected_total - expected_base
        
        print(f"\nExpected: {expected_base} base + {expected_parameterized} parameterized = {expected_total} total")
        print(f"Found: {expected_base} base + {total_instances} parameterized = {expected_base + total_instances} total")
        
        if total_instances >= expected_parameterized:
            print("✓ Sufficient parameterized instances found")
        else:
            print(f"⚠️  Need {expected_parameterized - total_instances} more parameterized instances")
        
        # Specific analysis for API-003
        print("\n=== SPECIFIC ANALYSIS: API-003 ===")
        api_003_analysis = analyze_test_case_structure(content, 'API-003')
        if api_003_analysis:
            print(f"API-003 has {len(api_003_analysis['test_variations'])} variations:")
            for var in api_003_analysis['test_variations']:
                print(f"  - {var['parameter']}: {var['value']}")
            print(f"Validation steps: {len(api_003_analysis['validation_steps'])}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()