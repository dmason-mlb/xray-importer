#!/usr/bin/env python3
"""
Phase 1: Current State Assessment
Xray Remediation Project - July 17, 2025

This script analyzes the current state of the FRAMED project to:
1. Count and categorize all tests
2. Identify standalone preconditions  
3. Analyze label issues
4. Assess folder structure
5. Generate comprehensive assessment report
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import re

# Add the scripts directory to path for imports
sys.path.append(str(Path(__file__).parent))
from auth_utils import XrayAPIClient, log_operation

def analyze_current_state():
    """Perform comprehensive analysis of FRAMED project current state"""
    
    print("🔍 Starting Phase 1: Current State Assessment")
    
    client = XrayAPIClient()
    
    # Create backup first
    print("📦 Creating backup of current state...")
    backup_file = client.backup_current_state("FRAMED")
    
    # Get all tests in FRAMED project
    print("📊 Fetching all tests from FRAMED project...")
    
    tests_query = """
    query GetAllTests($projectKey: String!) {
        getTests(jql: "project = $projectKey", limit: 1000) {
            total
            results {
                issueId
                summary
                testType
                labels
                preconditions {
                    issueId
                    summary
                }
                folder {
                    name
                    path
                }
                customFields {
                    name
                    value
                }
            }
        }
    }
    """
    
    tests_result = client.execute_graphql_query(tests_query, {"projectKey": "FRAMED"})
    all_tests = tests_result['getTests']['results']
    total_tests = tests_result['getTests']['total']
    
    print(f"✅ Found {total_tests} total tests in FRAMED project")
    
    # Get all preconditions
    print("📋 Fetching all preconditions...")
    
    preconditions_query = """
    query GetAllPreconditions($projectKey: String!) {
        getPreconditions(jql: "project = $projectKey", limit: 1000) {
            total
            results {
                issueId
                summary
                definition
            }
        }
    }
    """
    
    preconditions_result = client.execute_graphql_query(preconditions_query, {"projectKey": "FRAMED"})
    all_preconditions = preconditions_result['getPreconditions']['results']
    total_preconditions = preconditions_result['getPreconditions']['total']
    
    print(f"✅ Found {total_preconditions} total preconditions")
    
    # Analyze data
    analysis = analyze_data(all_tests, all_preconditions)
    
    # Generate report
    report = generate_assessment_report(analysis, backup_file)
    
    # Save report
    report_dir = Path(__file__).parent.parent / 'documentation'
    report_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = report_dir / f"phase1_assessment_report_{timestamp}.md"
    
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"📄 Assessment report saved: {report_file}")
    
    # Log operation
    log_operation("Phase 1 Assessment", {
        "total_tests": total_tests,
        "total_preconditions": total_preconditions,
        "backup_file": str(backup_file),
        "report_file": str(report_file)
    })
    
    return analysis

def analyze_data(tests, preconditions):
    """Analyze the fetched data for issues and patterns"""
    
    analysis = {
        "tests": {
            "total": len(tests),
            "by_type": {},
            "with_tc_labels": [],
            "with_lowercase_labels": [],
            "missing_folders": [],
            "api_tests": [],
            "functional_tests": []
        },
        "preconditions": {
            "total": len(preconditions),
            "standalone": [],
            "associated": []
        },
        "labels": {
            "inappropriate_tc": [],
            "lowercase": [],
            "uppercase": []
        },
        "folders": {
            "structure": {},
            "missing_tests": []
        }
    }
    
    # Analyze tests
    for test in tests:
        test_type = test.get('testType', 'Unknown')
        analysis["tests"]["by_type"][test_type] = analysis["tests"]["by_type"].get(test_type, 0) + 1
        
        # Check for API vs Functional tests
        labels = test.get('labels', [])
        if any('api' in label.lower() for label in labels):
            analysis["tests"]["api_tests"].append(test)
        elif any('functional' in label.lower() for label in labels):
            analysis["tests"]["functional_tests"].append(test)
        
        # Check for TC-XXX labels
        tc_labels = [label for label in labels if re.match(r'^TC-\d+', label)]
        if tc_labels:
            analysis["tests"]["with_tc_labels"].append({
                "issueId": test["issueId"],
                "summary": test["summary"],
                "tc_labels": tc_labels
            })
            analysis["labels"]["inappropriate_tc"].extend(tc_labels)
        
        # Check for lowercase labels
        lowercase_labels = [label for label in labels if label.islower() and label.startswith('@')]
        if lowercase_labels:
            analysis["tests"]["with_lowercase_labels"].append({
                "issueId": test["issueId"],
                "summary": test["summary"],
                "lowercase_labels": lowercase_labels
            })
            analysis["labels"]["lowercase"].extend(lowercase_labels)
        
        # Check folder structure
        folder = test.get('folder')
        if folder:
            folder_path = folder.get('path', 'Root')
            if folder_path not in analysis["folders"]["structure"]:
                analysis["folders"]["structure"][folder_path] = []
            analysis["folders"]["structure"][folder_path].append(test["issueId"])
        else:
            analysis["tests"]["missing_folders"].append(test["issueId"])
        
        # Track preconditions
        test_preconditions = test.get('preconditions', [])
        for precond in test_preconditions:
            analysis["preconditions"]["associated"].append(precond["issueId"])
    
    # Identify standalone preconditions
    associated_precondition_ids = set(analysis["preconditions"]["associated"])
    for precond in preconditions:
        if precond["issueId"] not in associated_precondition_ids:
            analysis["preconditions"]["standalone"].append(precond)
    
    return analysis

def generate_assessment_report(analysis, backup_file):
    """Generate comprehensive assessment report"""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report = f"""# Phase 1: Current State Assessment Report

**Generated**: {timestamp}
**Backup File**: {backup_file.name}

## Executive Summary

This assessment analyzed the current state of the FRAMED project in Xray to identify and quantify the issues requiring remediation.

### Key Findings

- **Total Tests**: {analysis['tests']['total']}
- **Total Preconditions**: {analysis['preconditions']['total']}
- **Standalone Preconditions**: {len(analysis['preconditions']['standalone'])} (❌ Issue #1)
- **Tests with TC-XXX Labels**: {len(analysis['tests']['with_tc_labels'])} (❌ Issue #2)
- **Tests with Lowercase Labels**: {len(analysis['tests']['with_lowercase_labels'])} (❌ Issue #4)
- **API Tests**: {len(analysis['tests']['api_tests'])}
- **Functional Tests**: {len(analysis['tests']['functional_tests'])} (❌ Issue #3 - Expected 38)

## Detailed Analysis

### Test Distribution by Type
"""
    
    for test_type, count in analysis['tests']['by_type'].items():
        report += f"- **{test_type}**: {count} tests\n"
    
    report += f"""
### Issue #1: Standalone Preconditions ({len(analysis['preconditions']['standalone'])})

These preconditions exist as standalone entities and need to be associated with appropriate tests:

"""
    
    for precond in analysis['preconditions']['standalone'][:10]:  # Show first 10
        report += f"- {precond['issueId']}: {precond['summary']}\n"
    
    if len(analysis['preconditions']['standalone']) > 10:
        report += f"... and {len(analysis['preconditions']['standalone']) - 10} more\n"
    
    report += f"""
### Issue #2: Inappropriate TC-XXX Labels ({len(analysis['tests']['with_tc_labels'])})

These tests have test case ID labels that should be removed:

"""
    
    for test in analysis['tests']['with_tc_labels'][:10]:  # Show first 10
        report += f"- {test['issueId']}: {test['summary']} (Labels: {', '.join(test['tc_labels'])})\n"
    
    if len(analysis['tests']['with_tc_labels']) > 10:
        report += f"... and {len(analysis['tests']['with_tc_labels']) - 10} more\n"
    
    report += f"""
### Issue #3: Missing Functional Tests

- **Current Functional Tests**: {len(analysis['tests']['functional_tests'])}
- **Expected Functional Tests**: 38 (from Team Page documentation)
- **Missing**: {38 - len(analysis['tests']['functional_tests'])} functional tests

### Issue #4: Lowercase Labels ({len(analysis['tests']['with_lowercase_labels'])})

These tests have lowercase labels that should be converted to uppercase:

"""
    
    lowercase_labels = set(analysis['labels']['lowercase'])
    for label in sorted(lowercase_labels)[:20]:  # Show first 20 unique labels
        report += f"- {label}\n"
    
    if len(lowercase_labels) > 20:
        report += f"... and {len(lowercase_labels) - 20} more unique labels\n"
    
    report += f"""
### Folder Structure Analysis

Current folder structure in FRAMED project:

"""
    
    for folder_path, test_ids in analysis['folders']['structure'].items():
        report += f"- **{folder_path}**: {len(test_ids)} tests\n"
    
    if analysis['tests']['missing_folders']:
        report += f"\n**Tests without folders**: {len(analysis['tests']['missing_folders'])}\n"
    
    report += f"""
## Remediation Priority

1. **High Priority**: Create backup and assess scope ✅ 
2. **High Priority**: Remove inappropriate TC-XXX labels ({len(analysis['tests']['with_tc_labels'])} tests)
3. **High Priority**: Associate standalone preconditions ({len(analysis['preconditions']['standalone'])} items)
4. **Medium Priority**: Convert lowercase labels to uppercase ({len(analysis['tests']['with_lowercase_labels'])} tests)
5. **Medium Priority**: Create missing functional tests ({38 - len(analysis['tests']['functional_tests'])} tests)
6. **Low Priority**: Add pytest decorators (requires manual file updates)

## Next Steps

1. Proceed to Phase 2: Label cleanup and standardization
2. Proceed to Phase 3: Precondition association
3. Proceed to Phase 4: Functional test creation
4. Proceed to Phase 5: Pytest integration
5. Proceed to Phase 6: Final validation

---

*This report provides the foundation for systematic remediation of all identified issues.*
"""
    
    return report

if __name__ == "__main__":
    try:
        analysis = analyze_current_state()
        print("\n✅ Phase 1 Assessment completed successfully")
        print(f"📊 Key findings:")
        print(f"   - {analysis['tests']['total']} total tests")
        print(f"   - {len(analysis['preconditions']['standalone'])} standalone preconditions")
        print(f"   - {len(analysis['tests']['with_tc_labels'])} tests with TC-XXX labels")
        print(f"   - {len(analysis['tests']['with_lowercase_labels'])} tests with lowercase labels")
        print(f"   - {len(analysis['tests']['functional_tests'])} functional tests (expected 38)")
        
    except Exception as e:
        print(f"❌ Phase 1 Assessment failed: {e}")
        sys.exit(1)