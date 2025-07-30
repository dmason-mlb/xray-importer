#!/usr/bin/env python3
"""
PHASE 1.3: Validate Data Transformation
Cross-references backup data with transformation data to ensure consistency
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Tuple

def load_backup_data() -> Dict[str, Any]:
    """Load the most recent backup data."""
    backup_files = [f for f in os.listdir('.') if f.startswith('test_backup_') and f.endswith('.json')]
    if not backup_files:
        raise FileNotFoundError("No backup files found")
    
    # Get the most recent backup
    latest_backup = max(backup_files)
    
    with open(latest_backup, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"✓ Loaded backup data from {latest_backup}")
    return data

def load_transformation_data() -> Dict[str, Any]:
    """Load the transformation data."""
    try:
        with open('xray_ready_test_steps.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✓ Loaded transformation data")
        return data
    except FileNotFoundError:
        raise FileNotFoundError("xray_ready_test_steps.json not found")

def validate_test_consistency(backup_data: Dict[str, Any], 
                            transformation_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Validate that backup and transformation data are consistent."""
    validation_results = []
    
    # Create lookup for backup data
    backup_lookup = {test['key']: test for test in backup_data['tests']}
    
    # Check each test in transformation data
    for trans_test in transformation_data['tests']:
        test_key = trans_test['key']
        result = {
            'test_key': test_key,
            'valid': True,
            'issues': [],
            'backup_steps': 0,
            'transformation_steps': trans_test['stepCount']
        }
        
        # Check if test exists in backup
        if test_key not in backup_lookup:
            result['valid'] = False
            result['issues'].append(f"Test {test_key} not found in backup data")
            validation_results.append(result)
            continue
        
        backup_test = backup_lookup[test_key]
        
        # Check if backup was successful
        if not backup_test['backup_successful']:
            result['valid'] = False
            result['issues'].append(f"Backup failed for {test_key}: {backup_test['error']}")
        
        # Check issue ID consistency
        if trans_test['issue_id'] != backup_test['issue_id']:
            result['valid'] = False
            result['issues'].append(f"Issue ID mismatch: transform={trans_test['issue_id']}, backup={backup_test['issue_id']}")
        
        # Check current step count
        if backup_test['backup_successful']:
            backup_steps = len(backup_test['current_data']['steps'])
            result['backup_steps'] = backup_steps
            
            if backup_steps > 0:
                result['issues'].append(f"Test already has {backup_steps} steps - may overwrite existing data")
        
        # Check test type consistency
        if (backup_test['backup_successful'] and 
            trans_test['testType'] != backup_test['current_data']['testType']['name']):
            result['issues'].append(f"Test type mismatch: transform={trans_test['testType']}, backup={backup_test['current_data']['testType']['name']}")
        
        validation_results.append(result)
    
    return validation_results

def check_api_readiness(transformation_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Check if transformation data is ready for API calls."""
    api_readiness = []
    
    for test in transformation_data['tests']:
        result = {
            'test_key': test['key'],
            'ready': True,
            'issues': [],
            'warnings': test.get('validation_warnings', [])
        }
        
        # Check required fields
        if not test.get('issue_id'):
            result['ready'] = False
            result['issues'].append("Missing issue_id")
        
        if not test.get('steps'):
            result['ready'] = False
            result['issues'].append("No steps defined")
        
        # Check each step
        for i, step in enumerate(test.get('steps', [])):
            if not step.get('action'):
                result['ready'] = False
                result['issues'].append(f"Step {i+1}: Missing action")
            
            if not step.get('result'):
                result['ready'] = False
                result['issues'].append(f"Step {i+1}: Missing result")
        
        api_readiness.append(result)
    
    return api_readiness

def generate_validation_report(validation_results: List[Dict[str, Any]], 
                             api_readiness: List[Dict[str, Any]]) -> str:
    """Generate a comprehensive validation report."""
    report = []
    report.append("DATA TRANSFORMATION VALIDATION REPORT")
    report.append("=" * 60)
    report.append(f"Validation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # Summary statistics
    total_tests = len(validation_results)
    valid_tests = sum(1 for r in validation_results if r['valid'])
    ready_tests = sum(1 for r in api_readiness if r['ready'])
    tests_with_warnings = sum(1 for r in api_readiness if r['warnings'])
    
    report.append("VALIDATION SUMMARY:")
    report.append(f"- Total tests: {total_tests}")
    report.append(f"- Valid tests: {valid_tests}")
    report.append(f"- API-ready tests: {ready_tests}")
    report.append(f"- Tests with warnings: {tests_with_warnings}")
    report.append("")
    
    # Data consistency check
    report.append("DATA CONSISTENCY CHECK:")
    for result in validation_results:
        if result['valid']:
            report.append(f"✓ {result['test_key']}: VALID")
        else:
            report.append(f"✗ {result['test_key']}: INVALID")
            for issue in result['issues']:
                report.append(f"    - {issue}")
        
        if result['backup_steps'] > 0:
            report.append(f"    ⚠️  Has {result['backup_steps']} existing steps")
        
        report.append(f"    Steps to add: {result['transformation_steps']}")
        report.append("")
    
    # API readiness check
    report.append("API READINESS CHECK:")
    for result in api_readiness:
        if result['ready']:
            report.append(f"✓ {result['test_key']}: READY")
        else:
            report.append(f"✗ {result['test_key']}: NOT READY")
            for issue in result['issues']:
                report.append(f"    - {issue}")
        
        if result['warnings']:
            report.append(f"    Warnings:")
            for warning in result['warnings']:
                report.append(f"      - {warning}")
        report.append("")
    
    # Final recommendations
    report.append("RECOMMENDATIONS:")
    if valid_tests == total_tests and ready_tests == total_tests:
        report.append("✓ All tests are valid and ready for API updates")
        report.append("✓ Safe to proceed to Phase 2.1")
    else:
        report.append(f"⚠️  {total_tests - valid_tests} tests have validation issues")
        report.append(f"⚠️  {total_tests - ready_tests} tests are not API-ready")
        report.append("   Review and fix issues before proceeding")
    
    if tests_with_warnings > 0:
        report.append(f"⚠️  {tests_with_warnings} tests have validation warnings")
        report.append("   Review warnings for potential issues")
    
    report.append("")
    report.append("NEXT STEPS:")
    report.append("1. Review all validation issues")
    report.append("2. Fix any critical problems")
    report.append("3. Proceed to Phase 2.1: Create update_test_steps.py")
    
    return "\n".join(report)

def main():
    """Main function to validate data transformation."""
    print("PHASE 1.3: Data Transformation Validation")
    print("=" * 60)
    
    try:
        # Load data
        print("Loading data files...")
        backup_data = load_backup_data()
        transformation_data = load_transformation_data()
        
        # Validate consistency
        print("Validating data consistency...")
        validation_results = validate_test_consistency(backup_data, transformation_data)
        
        # Check API readiness
        print("Checking API readiness...")
        api_readiness = check_api_readiness(transformation_data)
        
        # Generate report
        print("Generating validation report...")
        report = generate_validation_report(validation_results, api_readiness)
        
        # Save report
        report_file = 'validation_report.txt'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # Display summary
        print(f"\n✓ Validation completed!")
        print(f"✓ Report saved to: {report_file}")
        
        # Show key metrics
        total_tests = len(validation_results)
        valid_tests = sum(1 for r in validation_results if r['valid'])
        ready_tests = sum(1 for r in api_readiness if r['ready'])
        
        print(f"\n📊 SUMMARY:")
        print(f"   Valid tests: {valid_tests}/{total_tests}")
        print(f"   API-ready tests: {ready_tests}/{total_tests}")
        
        if valid_tests == total_tests and ready_tests == total_tests:
            print(f"\n✅ All tests validated successfully!")
            print(f"   Ready to proceed to Phase 2.1")
            return True
        else:
            print(f"\n⚠️  Validation issues found")
            print(f"   Review {report_file} for details")
            return False
    
    except Exception as e:
        print(f"✗ Validation failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)