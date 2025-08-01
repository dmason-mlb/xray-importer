#!/usr/bin/env python3
"""
Remove duplicate tags/labels from test JSON files
"""

import json
from pathlib import Path
from datetime import datetime

def remove_duplicates_from_list(tags):
    """Remove duplicates while preserving order"""
    seen = set()
    result = []
    for tag in tags:
        if tag not in seen:
            seen.add(tag)
            result.append(tag)
    return result

def clean_api_tests(file_path):
    """Remove duplicate tags from API tests"""
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    tests_cleaned = 0
    
    for test in data['testSuite']['testCases']:
        original_tags = test.get('tags', [])
        cleaned_tags = remove_duplicates_from_list(original_tags)
        
        if len(original_tags) != len(cleaned_tags):
            tests_cleaned += 1
            print(f"  Cleaned {test['testCaseId']}: {len(original_tags)} → {len(cleaned_tags)} tags")
            test['tags'] = cleaned_tags
    
    return data, tests_cleaned

def clean_functional_tests(file_path):
    """Remove duplicate labels from functional tests"""
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    tests_cleaned = 0
    
    for test in data['tests']:
        test_info = test.get('testInfo', {})
        original_labels = test_info.get('labels', [])
        cleaned_labels = remove_duplicates_from_list(original_labels)
        
        if len(original_labels) != len(cleaned_labels):
            tests_cleaned += 1
            summary = test_info.get('summary', 'Unknown')
            print(f"  Cleaned '{summary}': {len(original_labels)} → {len(cleaned_labels)} labels")
            test_info['labels'] = cleaned_labels
    
    return data, tests_cleaned

def main():
    """Main cleanup process"""
    print("\n" + "="*60)
    print("REMOVING DUPLICATE TAGS/LABELS")
    print("="*60)
    
    base_path = Path(__file__).parent.parent / 'test-data'
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create backup directory
    backup_dir = base_path / 'backups' / f'duplicate_cleanup_{timestamp}'
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Process API tests
    api_file = base_path / 'api_tests_xray.json'
    print(f"\nProcessing: {api_file.name}")
    
    # Backup original
    with open(api_file, 'r') as f:
        original_api = f.read()
    with open(backup_dir / api_file.name, 'w') as f:
        f.write(original_api)
    
    # Clean and save
    api_data, api_cleaned = clean_api_tests(api_file)
    with open(api_file, 'w') as f:
        json.dump(api_data, f, indent=2)
    
    print(f"✓ API tests: {api_cleaned} tests cleaned")
    
    # Process functional tests
    functional_file = base_path / 'functional_tests_xray.json'
    print(f"\nProcessing: {functional_file.name}")
    
    # Backup original
    with open(functional_file, 'r') as f:
        original_functional = f.read()
    with open(backup_dir / functional_file.name, 'w') as f:
        f.write(original_functional)
    
    # Clean and save
    functional_data, functional_cleaned = clean_functional_tests(functional_file)
    with open(functional_file, 'w') as f:
        json.dump(functional_data, f, indent=2)
    
    print(f"✓ Functional tests: {functional_cleaned} tests cleaned")
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"✓ Total tests cleaned: {api_cleaned + functional_cleaned}")
    print(f"✓ Backups created in: {backup_dir}")
    print(f"✓ Duplicate tags removed successfully!")

if __name__ == "__main__":
    main()