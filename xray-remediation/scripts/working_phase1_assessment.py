#!/usr/bin/env python3
"""
Phase 1: Current State Assessment (Working Version)
Xray Remediation Project - July 17, 2025
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import re

sys.path.append(str(Path(__file__).parent))
from auth_utils import XrayAPIClient, log_operation

def get_all_tests_with_details(client):
    """Get all tests with detailed information in batches"""
    
    all_tests = []
    start = 0
    limit = 50
    
    query = """
    query GetTests($jql: String!, $limit: Int!, $start: Int!) {
        getTests(jql: $jql, limit: $limit, start: $start) {
            total
            start
            limit
            results {
                issueId
                testType {
                    name
                    kind
                }
                folder {
                    name
                    path
                }
                preconditions {
                    total
                    results {
                        issueId
                    }
                }
                jira(fields: ["labels", "summary"])
            }
        }
    }
    """
    
    # Get first batch to determine total
    print(f"📊 Fetching batch 1...")
    result = client.execute_graphql_query(query, {
        "jql": "project = FRAMED",
        "limit": limit,
        "start": start
    })
    
    total = result['getTests']['total']
    all_tests.extend(result['getTests']['results'])
    
    print(f"Found {total} total tests, fetching remaining...")
    
    # Get remaining batches
    while start + limit < total:
        start += limit
        batch_num = (start // limit) + 1
        print(f"📊 Fetching batch {batch_num}...")
        
        result = client.execute_graphql_query(query, {
            "jql": "project = FRAMED",
            "limit": limit,
            "start": start
        })
        
        all_tests.extend(result['getTests']['results'])
    
    print(f"✅ Fetched {len(all_tests)} tests total")
    return all_tests

def get_all_preconditions(client):
    """Get all preconditions"""
    
    query = """
    query GetPreconditions($jql: String!, $limit: Int!) {
        getPreconditions(jql: $jql, limit: $limit) {
            total
            results {
                issueId
                jira(fields: ["summary"])
            }
        }
    }
    """
    
    result = client.execute_graphql_query(query, {
        "jql": "project = FRAMED",
        "limit": 200  # Should be enough for preconditions
    })
    
    return result['getPreconditions']['results']

def analyze_current_state():
    """Perform comprehensive analysis of FRAMED project current state"""
    
    print("🔍 Starting Phase 1: Current State Assessment")
    
    client = XrayAPIClient()
    
    # Get all tests
    all_tests = get_all_tests_with_details(client)
    
    # Get all preconditions  
    print("📋 Fetching all preconditions...")
    all_preconditions = get_all_preconditions(client)
    print(f"✅ Found {len(all_preconditions)} total preconditions")
    
    # Analyze data
    analysis = analyze_data(all_tests, all_preconditions)
    
    # Generate report
    report = generate_assessment_report(analysis, len(all_tests), len(all_preconditions))
    
    # Save report
    report_dir = Path(__file__).parent.parent / 'documentation'
    report_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = report_dir / f"phase1_assessment_report_{timestamp}.md"
    
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"📄 Assessment report saved: {report_file}")
    
    # Save raw data as backup
    backup_dir = Path(__file__).parent.parent / 'backups'
    backup_dir.mkdir(exist_ok=True)
    
    backup_data = {
        "timestamp": datetime.now().isoformat(),
        "tests": all_tests,
        "preconditions": all_preconditions,
        "analysis": analysis
    }
    
    backup_file = backup_dir / f"framed_state_backup_{timestamp}.json"
    with open(backup_file, 'w') as f:
        json.dump(backup_data, f, indent=2)
    
    print(f"💾 Raw data backup saved: {backup_file}")
    
    # Log operation
    log_operation("Phase 1 Assessment Complete", {
        "total_tests": len(all_tests),
        "total_preconditions": len(all_preconditions),
        "standalone_preconditions": len(analysis['preconditions']['standalone']),
        "tc_label_issues": len(analysis['tests']['with_tc_labels']),
        "lowercase_label_issues": len(analysis['tests']['with_lowercase_labels']),
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
            "all_unique": set()
        },
        "folders": {
            "structure": {},
            "missing_tests": []
        }
    }
    
    # Track which preconditions are associated
    associated_precondition_ids = set()
    
    # Analyze tests
    for test in tests:
        test_type = test.get('testType', {}).get('name', 'Unknown')
        analysis["tests"]["by_type"][test_type] = analysis["tests"]["by_type"].get(test_type, 0) + 1
        
        # Extract labels from JIRA data
        jira_data = test.get('jira', {})
        labels = jira_data.get('labels', []) if jira_data else []
        summary = jira_data.get('summary', 'No summary') if jira_data else 'No summary'
        
        # Add all labels to unique set
        analysis["labels"]["all_unique"].update(labels)
        
        # Check for API vs Functional tests based on labels
        if any('api' in label.lower() for label in labels):
            analysis["tests"]["api_tests"].append({
                "issueId": test["issueId"],
                "summary": summary,
                "labels": labels
            })
        elif any('functional' in label.lower() for label in labels):
            analysis["tests"]["functional_tests"].append({
                "issueId": test["issueId"],
                "summary": summary,
                "labels": labels
            })
        
        # Check for TC-XXX labels (inappropriate test case IDs)
        tc_labels = [label for label in labels if re.match(r'^TC-\d+', label)]
        if tc_labels:
            analysis["tests"]["with_tc_labels"].append({
                "issueId": test["issueId"],
                "summary": summary,
                "tc_labels": tc_labels,
                "all_labels": labels
            })
            analysis["labels"]["inappropriate_tc"].extend(tc_labels)
        
        # Check for lowercase labels that should be uppercase (starting with @)
        lowercase_labels = [label for label in labels if label.startswith('@') and any(c.islower() for c in label)]
        if lowercase_labels:
            analysis["tests"]["with_lowercase_labels"].append({
                "issueId": test["issueId"],
                "summary": summary,
                "lowercase_labels": lowercase_labels,
                "all_labels": labels
            })
            analysis["labels"]["lowercase"].extend(lowercase_labels)
        
        # Check folder structure
        folder = test.get('folder')
        if folder:
            folder_path = folder.get('path', '/')
            if folder_path not in analysis["folders"]["structure"]:
                analysis["folders"]["structure"][folder_path] = []
            analysis["folders"]["structure"][folder_path].append({
                "issueId": test["issueId"],
                "summary": summary
            })
        else:
            analysis["tests"]["missing_folders"].append({
                "issueId": test["issueId"],
                "summary": summary
            })
        
        # Track associated preconditions
        test_preconditions = test.get('preconditions', {}).get('results', [])
        for precond in test_preconditions:
            associated_precondition_ids.add(precond["issueId"])
            analysis["preconditions"]["associated"].append(precond["issueId"])
    
    # Identify standalone preconditions
    for precond in preconditions:
        if precond["issueId"] not in associated_precondition_ids:
            jira_data = precond.get('jira', {})
            analysis["preconditions"]["standalone"].append({
                "issueId": precond["issueId"],
                "summary": jira_data.get('summary', 'No summary') if jira_data else 'No summary'
            })
    
    return analysis

def generate_assessment_report(analysis, total_tests, total_preconditions):
    """Generate comprehensive assessment report"""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report = f"""# Phase 1: Current State Assessment Report

**Generated**: {timestamp}
**Project**: FRAMED

## Executive Summary

This assessment analyzed the current state of the FRAMED project in Xray to identify and quantify the issues requiring remediation.

### Key Findings

- **Total Tests**: {total_tests}
- **Total Preconditions**: {total_preconditions}
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
    
    for i, precond in enumerate(analysis['preconditions']['standalone'][:15]):  # Show first 15
        report += f"{i+1}. `{precond['issueId']}`: {precond['summary']}\n"
    
    if len(analysis['preconditions']['standalone']) > 15:
        report += f"\n... and {len(analysis['preconditions']['standalone']) - 15} more\n"
    
    report += f"""
### Issue #2: Inappropriate TC-XXX Labels ({len(analysis['tests']['with_tc_labels'])})

These tests have test case ID labels that should be removed:

"""
    
    for i, test in enumerate(analysis['tests']['with_tc_labels'][:15]):  # Show first 15
        report += f"{i+1}. `{test['issueId']}`: {test['summary']}\n"
        report += f"   - TC Labels to remove: {', '.join([f'`{label}`' for label in test['tc_labels']])}\n"
    
    if len(analysis['tests']['with_tc_labels']) > 15:
        report += f"\n... and {len(analysis['tests']['with_tc_labels']) - 15} more\n"
    
    report += f"""
### Issue #3: Missing Functional Tests

- **Current Functional Tests**: {len(analysis['tests']['functional_tests'])}
- **Expected Functional Tests**: 38 (from Team Page documentation)
- **Missing**: {38 - len(analysis['tests']['functional_tests'])} functional tests

**Current functional tests found:**
"""
    
    for test in analysis['tests']['functional_tests']:
        report += f"- `{test['issueId']}`: {test['summary']}\n"
    
    report += f"""
### Issue #4: Lowercase Labels ({len(analysis['tests']['with_lowercase_labels'])})

These tests have lowercase labels that should be converted to uppercase:

"""
    
    lowercase_labels = set(analysis['labels']['lowercase'])
    for i, label in enumerate(sorted(lowercase_labels)[:20]):  # Show first 20 unique labels
        report += f"{i+1}. `{label}` → `{label.upper()}`\n"
    
    if len(lowercase_labels) > 20:
        report += f"\n... and {len(lowercase_labels) - 20} more unique labels\n"
    
    report += f"""
### Folder Structure Analysis

Current folder structure in FRAMED project:

"""
    
    for folder_path, test_list in analysis['folders']['structure'].items():
        report += f"- **{folder_path}**: {len(test_list)} tests\n"
    
    if analysis['tests']['missing_folders']:
        report += f"\n**Tests without folders**: {len(analysis['tests']['missing_folders'])}\n"
    
    report += f"""
### Label Analysis

**Total unique labels found**: {len(analysis['labels']['all_unique'])}

**Sample of all labels:**
"""
    
    sample_labels = sorted(list(analysis['labels']['all_unique']))[:30]
    for i, label in enumerate(sample_labels):
        report += f"- `{label}`\n"
    
    if len(analysis['labels']['all_unique']) > 30:
        report += f"\n... and {len(analysis['labels']['all_unique']) - 30} more\n"
    
    report += f"""
## Issues Summary

| Issue | Current Count | Target | Status | Priority |
|-------|---------------|---------|---------|----------|
| Standalone Preconditions | {len(analysis['preconditions']['standalone'])} | 0 | ❌ Needs Fix | High |
| TC-XXX Labels | {len(analysis['tests']['with_tc_labels'])} | 0 | ❌ Needs Fix | High |
| Functional Tests | {len(analysis['tests']['functional_tests'])} | 38 | ❌ Needs Creation | High |
| Lowercase Labels | {len(analysis['tests']['with_lowercase_labels'])} | 0 | ❌ Needs Fix | Medium |

## Remediation Plan Status

✅ **Phase 1**: Assessment completed  
🔄 **Phase 2**: Label cleanup and standardization (Ready)  
🔄 **Phase 3**: Precondition association (Ready)  
🔄 **Phase 4**: Functional test creation (Ready)  
🔄 **Phase 5**: Pytest integration (Ready)  
🔄 **Phase 6**: Final validation (Ready)  

---

*Assessment data backed up and ready for remediation phases.*
"""
    
    return report

if __name__ == "__main__":
    try:
        analysis = analyze_current_state()
        print("\n✅ Phase 1 Assessment completed successfully")
        print(f"📊 Key findings:")
        print(f"   - {analysis['tests']['total']} total tests analyzed")
        print(f"   - {len(analysis['preconditions']['standalone'])} standalone preconditions")
        print(f"   - {len(analysis['tests']['with_tc_labels'])} tests with TC-XXX labels")
        print(f"   - {len(analysis['tests']['with_lowercase_labels'])} tests with lowercase labels")
        print(f"   - {len(analysis['tests']['functional_tests'])} functional tests (expected 38)")
        print(f"   - {len(analysis['tests']['api_tests'])} API tests")
        
    except Exception as e:
        print(f"❌ Phase 1 Assessment failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)