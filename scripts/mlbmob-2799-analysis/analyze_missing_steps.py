#!/usr/bin/env python3
"""
Analyze tests missing steps from MLBMOB-2799 test execution
"""

import json
import os
from datetime import datetime

def analyze_missing_steps():
    """Analyze the tests missing steps and generate detailed report"""
    
    # Load the analysis results
    try:
        with open('mlbmob_2799_tests_without_steps.json', 'r') as f:
            tests_without_steps = json.load(f)
        
        with open('mlbmob_2799_all_tests.json', 'r') as f:
            all_tests_data = json.load(f)
    except FileNotFoundError:
        print("Error: Please run get_test_execution_tests.py first to generate the data files")
        return
    
    print("MLBMOB-2799 Test Execution Analysis")
    print("=" * 60)
    print(f"Test Execution: {all_tests_data['test_execution']}")
    print(f"Summary: {all_tests_data['test_execution_summary']}")
    print(f"Total Tests: {all_tests_data['total_tests']}")
    print(f"Tests with Steps: {all_tests_data['tests_with_steps']}")
    print(f"Tests without Steps: {all_tests_data['tests_without_steps']}")
    print(f"Percentage Missing Steps: {(all_tests_data['tests_without_steps'] / all_tests_data['total_tests'] * 100):.1f}%")
    
    print("\n" + "=" * 60)
    print("TESTS MISSING STEPS - DETAILED ANALYSIS")
    print("=" * 60)
    
    # Generate detailed analysis
    analysis_report = {
        'analysis_date': datetime.now().isoformat(),
        'test_execution': all_tests_data['test_execution'],
        'test_execution_summary': all_tests_data['test_execution_summary'],
        'summary': {
            'total_tests': all_tests_data['total_tests'],
            'tests_with_steps': all_tests_data['tests_with_steps'],
            'tests_without_steps': all_tests_data['tests_without_steps'],
            'percentage_missing_steps': round(all_tests_data['tests_without_steps'] / all_tests_data['total_tests'] * 100, 1)
        },
        'tests_missing_steps': []
    }
    
    # Analyze each test missing steps
    for i, test in enumerate(tests_without_steps, 1):
        print(f"\n{i:2d}. {test['key']}")
        print(f"    Summary: {test['summary']}")
        print(f"    Type: {test['testType']}")
        print(f"    Status: {test['status']}")
        print(f"    JIRA Link: https://mlbam.atlassian.net/browse/{test['key']}")
        if test['labels']:
            print(f"    Labels: {', '.join(test['labels'])}")
        
        # Add to analysis report
        analysis_report['tests_missing_steps'].append({
            'key': test['key'],
            'summary': test['summary'],
            'testType': test['testType'],
            'status': test['status'],
            'labels': test['labels'],
            'jira_link': f"https://mlbam.atlassian.net/browse/{test['key']}"
        })
    
    # Save detailed analysis report
    with open('mlbmob_2799_missing_steps_analysis.json', 'w') as f:
        json.dump(analysis_report, f, indent=2)
    
    # Generate markdown report
    with open('mlbmob_2799_missing_steps_report.md', 'w') as f:
        f.write("# MLBMOB-2799 Test Execution Analysis\n\n")
        f.write(f"**Test Execution:** {all_tests_data['test_execution']}\n")
        f.write(f"**Summary:** {all_tests_data['test_execution_summary']}\n")
        f.write(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Summary\n\n")
        f.write(f"- **Total Tests:** {all_tests_data['total_tests']}\n")
        f.write(f"- **Tests with Steps:** {all_tests_data['tests_with_steps']}\n")
        f.write(f"- **Tests without Steps:** {all_tests_data['tests_without_steps']}\n")
        f.write(f"- **Percentage Missing Steps:** {(all_tests_data['tests_without_steps'] / all_tests_data['total_tests'] * 100):.1f}%\n\n")
        
        f.write("## Tests Missing Steps\n\n")
        f.write("The following tests are missing test steps and need to be updated:\n\n")
        
        for i, test in enumerate(tests_without_steps, 1):
            f.write(f"### {i}. [{test['key']}](https://mlbam.atlassian.net/browse/{test['key']})\n")
            f.write(f"**Summary:** {test['summary']}\n")
            f.write(f"**Type:** {test['testType']}\n")
            f.write(f"**Status:** {test['status']}\n")
            if test['labels']:
                f.write(f"**Labels:** {', '.join(test['labels'])}\n")
            f.write("\n")
        
        f.write("## Recommendations\n\n")
        f.write("1. **High Priority:** Add detailed test steps to all tests listed above\n")
        f.write("2. **Test Step Format:** Each test should have clear action, data, and expected result\n")
        f.write("3. **Consistency:** Ensure all manual tests have comprehensive step-by-step instructions\n")
        f.write("4. **Review Process:** Consider implementing a review process for test case completeness\n")
        f.write("5. **Template Usage:** Use standardized test step templates for consistency\n\n")
        
        f.write("## Next Steps\n\n")
        f.write("1. Assign test step creation to appropriate team members\n")
        f.write("2. Update each test case with detailed steps\n")
        f.write("3. Review and validate the updated test cases\n")
        f.write("4. Run this analysis again to verify all tests have steps\n")
    
    # Generate CSV for easy import/tracking
    with open('mlbmob_2799_missing_steps.csv', 'w') as f:
        f.write("Test Key,Summary,Type,Status,Labels,JIRA Link\n")
        for test in tests_without_steps:
            labels_str = '|'.join(test['labels']) if test['labels'] else ''
            f.write(f'"{test["key"]}","{test["summary"]}","{test["testType"]}","{test["status"]}","{labels_str}","https://mlbam.atlassian.net/browse/{test["key"]}"\n')
    
    print(f"\n{'='*60}")
    print("ANALYSIS COMPLETE")
    print("="*60)
    print("Files generated:")
    print("- mlbmob_2799_missing_steps_analysis.json (detailed JSON analysis)")
    print("- mlbmob_2799_missing_steps_report.md (markdown report)")
    print("- mlbmob_2799_missing_steps.csv (CSV for tracking)")
    
    print(f"\nSummary: {all_tests_data['tests_without_steps']} of {all_tests_data['total_tests']} tests ({(all_tests_data['tests_without_steps'] / all_tests_data['total_tests'] * 100):.1f}%) are missing test steps")
    
    # Show test type distribution for tests with steps
    all_tests = all_tests_data['all_tests']
    tests_with_steps = [t for t in all_tests if t['stepCount'] > 0]
    
    print(f"\nStep count analysis for tests WITH steps:")
    step_counts = {}
    for test in tests_with_steps:
        count = test['stepCount']
        step_counts[count] = step_counts.get(count, 0) + 1
    
    for count in sorted(step_counts.keys()):
        print(f"- {count} step{'s' if count != 1 else ''}: {step_counts[count]} tests")

if __name__ == "__main__":
    analyze_missing_steps()