#!/usr/bin/env python3
"""
Analyze duplicate tags/labels in test JSON files
"""

import json
from pathlib import Path
from collections import Counter

def analyze_duplicates(file_path, tag_field_path):
    """Analyze duplicate tags in a test file"""
    
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    print(f"\n{'='*60}")
    print(f"Analyzing: {file_path.name}")
    print(f"{'='*60}")
    
    duplicate_summary = {
        'total_tests': 0,
        'tests_with_duplicates': 0,
        'duplicate_tags': Counter(),
        'worst_offenders': []
    }
    
    # Navigate to test array based on file type
    if 'testSuite' in data:
        # API tests
        tests = data['testSuite']['testCases']
        tag_field = 'tags'
    else:
        # Functional tests
        tests = data['tests']
        tag_field = 'labels'
    
    duplicate_summary['total_tests'] = len(tests)
    
    for i, test in enumerate(tests):
        # Get tags/labels
        if 'testSuite' in data:
            tags = test.get('tags', [])
            test_id = test.get('testCaseId', f'Test {i+1}')
        else:
            tags = test.get('testInfo', {}).get('labels', [])
            test_id = test.get('testInfo', {}).get('summary', f'Test {i+1}')
        
        # Check for duplicates
        tag_counts = Counter(tags)
        duplicates = {tag: count for tag, count in tag_counts.items() if count > 1}
        
        if duplicates:
            duplicate_summary['tests_with_duplicates'] += 1
            duplicate_summary['duplicate_tags'].update(duplicates.keys())
            
            duplicate_summary['worst_offenders'].append({
                'test_id': test_id,
                'duplicates': duplicates,
                'original_tags': tags
            })
            
            print(f"\n{test_id}:")
            print(f"  Original tags: {tags}")
            print(f"  Duplicates found: {duplicates}")
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Total tests: {duplicate_summary['total_tests']}")
    print(f"Tests with duplicate tags: {duplicate_summary['tests_with_duplicates']}")
    print(f"Percentage with duplicates: {duplicate_summary['tests_with_duplicates'] / duplicate_summary['total_tests'] * 100:.1f}%")
    
    print(f"\nMost common duplicate tags:")
    for tag, count in duplicate_summary['duplicate_tags'].most_common(10):
        print(f"  - '{tag}': found duplicated in {count} tests")
    
    return duplicate_summary

def main():
    """Main analysis"""
    base_path = Path(__file__).parent.parent / 'test-data'
    
    # Analyze both files
    api_results = analyze_duplicates(
        base_path / 'api_tests_xray.json',
        'testSuite.testCases.tags'
    )
    
    functional_results = analyze_duplicates(
        base_path / 'functional_tests_xray.json',
        'tests.testInfo.labels'
    )
    
    # Save detailed report
    report = {
        'api_tests': api_results,
        'functional_tests': functional_results
    }
    
    report_path = Path(__file__).parent.parent / 'logs' / 'duplicate_tags_analysis.json'
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n✓ Detailed report saved to: {report_path}")

if __name__ == "__main__":
    main()