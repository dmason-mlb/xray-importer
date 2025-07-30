#!/usr/bin/env python3
"""
Complete inventory of FRAMED project tests and preconditions.
Based on Phase 1 assessment results.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import re

def analyze_existing_data():
    """Analyze the existing FRAMED assessment data"""
    
    # Path to assessment data
    assessment_file = Path(__file__).parent.parent / "backups" / "FRAMED_BASIC_ASSESSMENT_20250716_213912.json"
    
    if not assessment_file.exists():
        print(f"Assessment file not found: {assessment_file}")
        return
    
    with open(assessment_file) as f:
        data = json.load(f)
    
    print("=" * 80)
    print("FRAMED PROJECT INVENTORY SUMMARY")
    print("=" * 80)
    print(f"Assessment Date: {data.get('timestamp', 'Unknown')}")
    print(f"Project: {data.get('project', 'FRAMED')}")
    print()
    
    # Test Summary
    test_summary = data.get('test_summary', {})
    print("TEST SUMMARY:")
    print(f"  Total Tests: {test_summary.get('total_tests', 0)}")
    print(f"  Manual Tests: {test_summary.get('manual_tests', 0)}")
    print(f"  Automated Tests: {test_summary.get('automated_tests', 0)}")
    print(f"  Generic Tests: {test_summary.get('generic_tests', 0)}")
    print()
    
    # Precondition Summary
    precondition_summary = data.get('precondition_summary', {})
    print("PRECONDITION SUMMARY:")
    print(f"  Total Preconditions: {precondition_summary.get('total_preconditions', 0)}")
    print(f"  Associated Preconditions: {precondition_summary.get('associated_preconditions', 0)}")
    print(f"  Standalone Preconditions: {precondition_summary.get('standalone_preconditions', 0)}")
    print()
    
    # Label Analysis
    print("LABEL ANALYSIS:")
    test_case_labels = test_summary.get('test_case_labels', {})
    print(f"  Tests with Test Case ID Labels: {test_case_labels.get('count', 0)}")
    if test_case_labels.get('examples'):
        print("  Examples of Test Case ID Labels:")
        for example in test_case_labels.get('examples', [])[:5]:
            print(f"    - {example}")
    
    print()
    
    # Analyze individual tests for labels
    tests = data.get('tests', [])
    label_issues = []
    folder_issues = []
    
    for test in tests:
        test_key = test.get('key', '')
        labels = test.get('labels', [])
        
        # Check for test case ID labels (API-XXX patterns)
        test_id_labels = [label for label in labels if re.match(r'^API-[A-Z]+-\d+$|^API-\d+$', label, re.IGNORECASE)]
        if test_id_labels:
            label_issues.append({
                'key': test_key,
                'test_id_labels': test_id_labels,
                'all_labels': labels
            })
        
        # Check folder (all tests should be in folders)
        folder = test.get('folder', '')
        if not folder or folder == '/':
            folder_issues.append({
                'key': test_key,
                'summary': test.get('summary', ''),
                'current_folder': folder
            })
    
    print("DETAILED ISSUES:")
    print(f"  Tests with Test Case ID Labels: {len(label_issues)}")
    if label_issues:
        print("  First 5 examples:")
        for issue in label_issues[:5]:
            print(f"    - {issue['key']}: {issue['test_id_labels']}")
    
    print()
    print(f"  Tests NOT in folders: {len(folder_issues)}")
    if folder_issues:
        print("  First 5 examples:")
        for issue in folder_issues[:5]:
            print(f"    - {issue['key']}: {issue['summary']}")
    
    print()
    
    # JSON Truth File Analysis
    print("JSON TRUTH FILE ANALYSIS:")
    api_json = Path(__file__).parent.parent / "test-data" / "api_tests_xray.json"
    func_json = Path(__file__).parent.parent / "test-data" / "functional_tests_xray.json"
    
    if api_json.exists():
        with open(api_json) as f:
            api_data = json.load(f)
        print(f"  API Tests in JSON: {len(api_data.get('tests', []))}")
    
    if func_json.exists():
        with open(func_json) as f:
            func_data = json.load(f)
        print(f"  Functional Tests in JSON: {len(func_data.get('tests', []))}")
    
    print()
    print("REMEDIATION NEEDED:")
    print("1. Remove test case ID labels from existing API tests")
    print("2. Organize all tests into proper folder structure")
    print("3. Associate 34 standalone preconditions with tests")
    print("4. Create 38 functional tests from JSON")
    print("5. Add Xray decorators to 66 pytest tests")
    
    # Save detailed inventory
    inventory = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_tests': test_summary.get('total_tests', 0),
            'tests_with_label_issues': len(label_issues),
            'tests_without_folders': len(folder_issues),
            'standalone_preconditions': precondition_summary.get('standalone_preconditions', 0),
            'functional_tests_to_create': 38,
            'pytest_tests_to_decorate': 66
        },
        'label_issues': label_issues,
        'folder_issues': folder_issues,
        'json_truth_files': {
            'api_tests': 55 if api_json.exists() else 0,
            'functional_tests': 38 if func_json.exists() else 0
        }
    }
    
    inventory_file = Path(__file__).parent.parent / "documentation" / "FRAMED_INVENTORY.json"
    with open(inventory_file, 'w') as f:
        json.dump(inventory, f, indent=2)
    
    print(f"\nDetailed inventory saved to: {inventory_file}")

if __name__ == "__main__":
    analyze_existing_data()