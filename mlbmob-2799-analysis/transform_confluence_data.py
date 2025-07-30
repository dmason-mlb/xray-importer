#!/usr/bin/env python3
"""
PHASE 1.1: Transform Confluence data to XRAY GraphQL format
Converts mlbmob_2799_confluence_test_steps.json to xray_ready_test_steps.json
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Any

def load_confluence_data(file_path: str) -> Dict[str, Any]:
    """Load and validate the Confluence test steps JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✓ Loaded Confluence data: {data['test_count']} tests")
        return data
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {file_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in input file: {e}")

def validate_step_content(step: Dict[str, str]) -> List[str]:
    """Validate step content for XRAY GraphQL requirements."""
    warnings = []
    
    # Check for required fields
    if not step.get('action'):
        warnings.append("Missing 'action' field")
    if not step.get('result'):
        warnings.append("Missing 'result' field")
    
    # Check content length (GraphQL field limits)
    action_len = len(step.get('action', ''))
    result_len = len(step.get('result', ''))
    data_len = len(step.get('data', ''))
    
    if action_len > 4000:
        warnings.append(f"Action field too long: {action_len} chars (max 4000)")
    if result_len > 4000:
        warnings.append(f"Result field too long: {result_len} chars (max 4000)")
    if data_len > 4000:
        warnings.append(f"Data field too long: {data_len} chars (max 4000)")
    
    # Check for potentially problematic characters
    problematic_chars = ['\\', '"', '\x00', '\x01', '\x02', '\x03', '\x04', '\x05']
    for field_name, content in [('action', step.get('action', '')), 
                               ('result', step.get('result', '')), 
                               ('data', step.get('data', ''))]:
        for char in problematic_chars:
            if char in content:
                warnings.append(f"Potentially problematic character '{char}' in {field_name}")
    
    return warnings

def transform_test_data(test: Dict[str, Any]) -> Dict[str, Any]:
    """Transform a single test case to XRAY format."""
    
    # Extract basic test information
    transformed = {
        'key': test['key'],
        'summary': test['summary'],
        'issue_id': test['issue_id'],
        'testType': test['testType'],
        'stepCount': test['stepCount'],
        'steps': [],
        'validation_warnings': []
    }
    
    # Transform steps
    for step in test.get('steps', []):
        # Validate step content
        warnings = validate_step_content(step)
        if warnings:
            transformed['validation_warnings'].extend([f"Step validation: {w}" for w in warnings])
        
        # Transform step to XRAY format
        xray_step = {
            'action': step.get('action', '').strip(),
            'result': step.get('result', '').strip(),
            'data': step.get('data', '').strip()
        }
        
        # Clean up any extra whitespace
        xray_step['action'] = re.sub(r'\n\s*\n', '\n\n', xray_step['action'])
        xray_step['result'] = re.sub(r'\n\s*\n', '\n\n', xray_step['result'])
        
        transformed['steps'].append(xray_step)
    
    return transformed

def generate_transformation_report(original_data: Dict[str, Any], 
                                 transformed_data: Dict[str, Any]) -> str:
    """Generate a detailed transformation report."""
    report = []
    report.append("CONFLUENCE DATA TRANSFORMATION REPORT")
    report.append("=" * 50)
    report.append(f"Transformation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Source Document: {original_data['source_document']['title']}")
    report.append(f"Source Page ID: {original_data['source_document']['page_id']}")
    report.append(f"Original Test Count: {original_data['test_count']}")
    report.append(f"Transformed Test Count: {len(transformed_data['tests'])}")
    report.append("")
    
    # Summary statistics
    total_warnings = sum(len(test.get('validation_warnings', [])) for test in transformed_data['tests'])
    tests_with_warnings = sum(1 for test in transformed_data['tests'] if test.get('validation_warnings'))
    
    report.append("TRANSFORMATION SUMMARY:")
    report.append(f"- Tests processed: {len(transformed_data['tests'])}")
    report.append(f"- Tests with warnings: {tests_with_warnings}")
    report.append(f"- Total warnings: {total_warnings}")
    report.append("")
    
    # Individual test details
    report.append("TEST DETAILS:")
    for test in transformed_data['tests']:
        report.append(f"- {test['key']}: {test['summary']}")
        report.append(f"  Issue ID: {test['issue_id']}")
        report.append(f"  Steps: {test['stepCount']}")
        
        if test.get('validation_warnings'):
            report.append(f"  WARNINGS:")
            for warning in test['validation_warnings']:
                report.append(f"    - {warning}")
        report.append("")
    
    return "\n".join(report)

def main():
    """Main function to transform Confluence data."""
    print("PHASE 1.1: Confluence Data Transformation")
    print("=" * 50)
    
    # File paths
    input_file = 'mlbmob_2799_confluence_test_steps.json'
    output_file = 'xray_ready_test_steps.json'
    report_file = 'transformation_report.txt'
    
    try:
        # Load original data
        print(f"Loading data from {input_file}...")
        original_data = load_confluence_data(input_file)
        
        # Transform each test case
        print("Transforming test data...")
        transformed_tests = []
        
        for test in original_data['tests']:
            print(f"  Processing {test['key']}...")
            transformed_test = transform_test_data(test)
            transformed_tests.append(transformed_test)
        
        # Create output structure
        transformed_data = {
            'transformation_info': {
                'source_file': input_file,
                'transformation_date': datetime.now().isoformat(),
                'source_document': original_data['source_document']
            },
            'test_count': len(transformed_tests),
            'tests': transformed_tests
        }
        
        # Save transformed data
        print(f"Saving transformed data to {output_file}...")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(transformed_data, f, indent=2, ensure_ascii=False)
        
        # Generate and save report
        print(f"Generating transformation report...")
        report = generate_transformation_report(original_data, transformed_data)
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # Display summary
        print(f"\n✓ Transformation completed successfully!")
        print(f"✓ {len(transformed_tests)} tests transformed")
        print(f"✓ Output saved to: {output_file}")
        print(f"✓ Report saved to: {report_file}")
        
        # Show any warnings
        total_warnings = sum(len(test.get('validation_warnings', [])) for test in transformed_tests)
        if total_warnings > 0:
            print(f"\n⚠️  {total_warnings} validation warnings found")
            print("   Check transformation_report.txt for details")
        
        return True
        
    except Exception as e:
        print(f"✗ Error during transformation: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)