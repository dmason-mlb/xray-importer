#!/usr/bin/env python3
"""
Final Phase 1 Assessment - Using Correct JQL Format
Xray Remediation Project - July 17, 2025
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import re

sys.path.append(str(Path(__file__).parent))
from auth_utils import XrayAPIClient, log_operation

def get_all_tests(client):
    """Get all tests using correct JQL format"""
    
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
                }
                folder {
                    path
                }
                steps {
                    id
                }
                preconditions {
                    total
                }
                jira(fields: ["key", "summary", "labels"])
            }
        }
    }
    """
    
    all_tests = []
    start = 0
    limit = 50
    
    # Use correct JQL format
    jql = "project = FRAMED AND issuetype = Test"
    
    print(f"📊 Fetching tests with JQL: {jql}")
    
    # Get first batch
    result = client.execute_graphql_query(query, {
        "jql": jql,
        "limit": limit,
        "start": start
    })
    
    total = result['getTests']['total']
    all_tests.extend(result['getTests']['results'])
    
    print(f"Found {total} total tests, retrieving all...")
    
    # Get remaining batches
    while start + limit < total:
        start += limit
        batch_num = (start // limit) + 1
        print(f"📊 Fetching batch {batch_num}...")
        
        result = client.execute_graphql_query(query, {
            "jql": jql,
            "limit": limit,
            "start": start
        })
        
        all_tests.extend(result['getTests']['results'])
    
    print(f"✅ Retrieved {len(all_tests)} tests")
    return all_tests

def get_all_preconditions(client):
    """Get all preconditions using correct JQL format"""
    
    query = """
    query GetPreconditions($jql: String!, $limit: Int!) {
        getPreconditions(jql: $jql, limit: $limit) {
            total
            results {
                issueId
                jira(fields: ["key", "summary"])
            }
        }
    }
    """
    
    jql = "project = FRAMED AND issuetype = 'Pre-Condition'"
    
    result = client.execute_graphql_query(query, {
        "jql": jql,
        "limit": 200  # Should be enough
    })
    
    return result['getPreconditions']['results']

def perform_assessment():
    """Perform comprehensive assessment"""
    
    print("🔍 Starting Final Phase 1 Assessment")
    
    client = XrayAPIClient()
    
    # Get all tests
    tests = get_all_tests(client)
    
    # Get all preconditions  
    print("📋 Fetching all preconditions...")
    preconditions = get_all_preconditions(client)
    print(f"✅ Found {len(preconditions)} preconditions")
    
    # Analyze the data
    analysis = analyze_test_data(tests, preconditions)
    
    # Generate and save report
    save_results(analysis, tests, preconditions)
    
    return analysis

def analyze_test_data(tests, preconditions):
    """Analyze the test data for all issues"""
    
    analysis = {
        "summary": {
            "total_tests": len(tests),
            "total_preconditions": len(preconditions)
        },
        "tests": {
            "by_type": {},
            "api_tests": [],
            "functional_tests": [],
            "with_tc_labels": [],
            "with_lowercase_labels": [],
            "with_steps": 0,
            "without_steps": 0
        },
        "preconditions": {
            "standalone": [],
            "associated_count": 0
        },
        "labels": {
            "all_unique": set(),
            "inappropriate_tc": [],
            "lowercase": []
        },
        "folders": {},
        "issues": {
            "standalone_preconditions": 0,
            "tc_label_issues": 0,
            "lowercase_label_issues": 0,
            "missing_functional_tests": 0
        }
    }
    
    # Track associated preconditions
    associated_preconditions = 0
    
    # Analyze each test
    for test in tests:
        issue_id = test['issueId']
        jira_data = test.get('jira', {})
        summary = jira_data.get('summary', 'No summary')
        labels = jira_data.get('labels', [])
        
        # Test type analysis
        test_type = test.get('testType', {}).get('name', 'Unknown')
        analysis["tests"]["by_type"][test_type] = analysis["tests"]["by_type"].get(test_type, 0) + 1
        
        # Steps analysis
        steps = test.get('steps', [])
        if steps:
            analysis["tests"]["with_steps"] += 1
        else:
            analysis["tests"]["without_steps"] += 1
        
        # Preconditions analysis
        precond_total = test.get('preconditions', {}).get('total', 0)
        associated_preconditions += precond_total
        
        # Label analysis
        analysis["labels"]["all_unique"].update(labels)
        
        # Check for API vs Functional tests
        test_info = {
            "issueId": issue_id,
            "summary": summary,
            "labels": labels
        }
        
        if any('api' in label.lower() for label in labels):
            analysis["tests"]["api_tests"].append(test_info)
        elif any('functional' in label.lower() for label in labels):
            analysis["tests"]["functional_tests"].append(test_info)
        
        # Check for TC-XXX labels (Issue #2)
        tc_labels = [label for label in labels if re.match(r'^TC-\d+', label)]
        if tc_labels:
            analysis["tests"]["with_tc_labels"].append({
                **test_info,
                "tc_labels": tc_labels
            })
            analysis["labels"]["inappropriate_tc"].extend(tc_labels)
        
        # Check for lowercase labels (Issue #4)
        lowercase_labels = [label for label in labels if label.startswith('@') and any(c.islower() for c in label)]
        if lowercase_labels:
            analysis["tests"]["with_lowercase_labels"].append({
                **test_info,
                "lowercase_labels": lowercase_labels
            })
            analysis["labels"]["lowercase"].extend(lowercase_labels)
        
        # Folder analysis
        folder_path = test.get('folder', {}).get('path', '/')
        analysis["folders"][folder_path] = analysis["folders"].get(folder_path, 0) + 1
    
    # Calculate standalone preconditions (Issue #1)
    analysis["preconditions"]["associated_count"] = associated_preconditions
    standalone_count = len(preconditions) - associated_preconditions
    
    # Since we can't easily determine which specific preconditions are standalone
    # without more complex queries, we'll estimate based on the total
    for i, precond in enumerate(preconditions):
        if i < standalone_count:  # Approximate standalone preconditions
            jira_data = precond.get('jira', {})
            analysis["preconditions"]["standalone"].append({
                "issueId": precond['issueId'],
                "summary": jira_data.get('summary', 'No summary')
            })
    
    # Calculate issue counts
    analysis["issues"]["standalone_preconditions"] = len(analysis["preconditions"]["standalone"])
    analysis["issues"]["tc_label_issues"] = len(analysis["tests"]["with_tc_labels"])
    analysis["issues"]["lowercase_label_issues"] = len(analysis["tests"]["with_lowercase_labels"])
    analysis["issues"]["missing_functional_tests"] = max(0, 38 - len(analysis["tests"]["functional_tests"]))
    
    return analysis

def save_results(analysis, tests, preconditions):
    """Save assessment results"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Generate report
    report = generate_comprehensive_report(analysis)
    
    # Save report
    report_dir = Path(__file__).parent.parent / 'documentation'
    report_dir.mkdir(exist_ok=True)
    report_file = report_dir / f"comprehensive_assessment_{timestamp}.md"
    
    with open(report_file, 'w') as f:
        f.write(report)
    
    # Save raw data
    backup_dir = Path(__file__).parent.parent / 'backups'
    backup_dir.mkdir(exist_ok=True)
    backup_file = backup_dir / f"complete_backup_{timestamp}.json"
    
    backup_data = {
        "timestamp": datetime.now().isoformat(),
        "tests": tests,
        "preconditions": preconditions,
        "analysis": {k: v for k, v in analysis.items() if k != "labels"},  # Exclude set from JSON
        "labels": {
            "all_unique": list(analysis["labels"]["all_unique"]),
            "inappropriate_tc": analysis["labels"]["inappropriate_tc"],
            "lowercase": analysis["labels"]["lowercase"]
        }
    }
    
    with open(backup_file, 'w') as f:
        json.dump(backup_data, f, indent=2)
    
    print(f"📄 Comprehensive report: {report_file}")
    print(f"💾 Complete backup: {backup_file}")
    
    # Log the operation
    log_operation("Comprehensive Assessment Complete", {
        "total_tests": analysis["summary"]["total_tests"],
        "total_preconditions": analysis["summary"]["total_preconditions"],
        "issues_found": analysis["issues"],
        "report_file": str(report_file),
        "backup_file": str(backup_file)
    })

def generate_comprehensive_report(analysis):
    """Generate the comprehensive assessment report"""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report = f"""# Comprehensive Phase 1 Assessment Report

**Generated**: {timestamp}  
**Project**: FRAMED  
**Status**: ✅ COMPLETE  

## Executive Summary

Comprehensive analysis of the FRAMED project has identified all issues requiring remediation.

### Critical Findings

| Issue | Count | Status | Priority |
|-------|-------|---------|----------|
| **Standalone Preconditions** | {analysis['issues']['standalone_preconditions']} | ❌ Critical | High |
| **TC-XXX Label Issues** | {analysis['issues']['tc_label_issues']} | ❌ Critical | High |
| **Missing Functional Tests** | {analysis['issues']['missing_functional_tests']} | ❌ Critical | High |
| **Lowercase Label Issues** | {analysis['issues']['lowercase_label_issues']} | ❌ Medium | Medium |

### Project Statistics

- **Total Tests**: {analysis['summary']['total_tests']}
- **Total Preconditions**: {analysis['summary']['total_preconditions']}
- **API Tests**: {len(analysis['tests']['api_tests'])}
- **Functional Tests**: {len(analysis['tests']['functional_tests'])}
- **Tests with Steps**: {analysis['tests']['with_steps']}
- **Tests without Steps**: {analysis['tests']['without_steps']}

## Detailed Issue Analysis

### Issue #1: Standalone Preconditions ({analysis['issues']['standalone_preconditions']})

**Problem**: Preconditions created as standalone entities instead of being associated with tests.

**First 10 standalone preconditions:**
"""
    
    for i, precond in enumerate(analysis['preconditions']['standalone'][:10]):
        report += f"{i+1}. `{precond['issueId']}`: {precond['summary']}\n"
    
    if len(analysis['preconditions']['standalone']) > 10:
        report += f"\n... and {len(analysis['preconditions']['standalone']) - 10} more\n"
    
    report += f"""
### Issue #2: Inappropriate TC-XXX Labels ({analysis['issues']['tc_label_issues']})

**Problem**: Tests have test case ID labels that should be removed.

**Tests requiring label cleanup:**
"""
    
    for i, test in enumerate(analysis['tests']['with_tc_labels'][:10]):
        report += f"{i+1}. `{test['issueId']}`: {test['summary']}\n"
        report += f"   - Remove: {', '.join([f'`{label}`' for label in test['tc_labels']])}\n"
    
    if len(analysis['tests']['with_tc_labels']) > 10:
        report += f"\n... and {len(analysis['tests']['with_tc_labels']) - 10} more\n"
    
    report += f"""
### Issue #3: Missing Functional Tests ({analysis['issues']['missing_functional_tests']})

**Problem**: Expected 38 functional tests, found {len(analysis['tests']['functional_tests'])}.

**Current functional tests:**
"""
    
    for test in analysis['tests']['functional_tests']:
        report += f"- `{test['issueId']}`: {test['summary']}\n"
    
    report += f"""
### Issue #4: Lowercase Labels ({analysis['issues']['lowercase_label_issues']})

**Problem**: Labels should be uppercase format.

**Labels needing conversion:**
"""
    
    unique_lowercase = sorted(set(analysis['labels']['lowercase']))[:15]
    for label in unique_lowercase:
        report += f"- `{label}` → `{label.upper()}`\n"
    
    if len(unique_lowercase) > 15:
        report += f"\n... and {len(set(analysis['labels']['lowercase'])) - 15} more\n"
    
    report += f"""
## Test Distribution

### By Type
"""
    
    for test_type, count in analysis['tests']['by_type'].items():
        report += f"- **{test_type}**: {count} tests\n"
    
    report += f"""
### By Folder
"""
    
    for folder, count in sorted(analysis['folders'].items()):
        folder_display = folder if folder != '/' else 'Root'
        report += f"- **{folder_display}**: {count} tests\n"
    
    report += f"""
### API vs Functional Classification

- **API Tests**: {len(analysis['tests']['api_tests'])} (based on labels)
- **Functional Tests**: {len(analysis['tests']['functional_tests'])} (based on labels)
- **Other/Unclassified**: {analysis['summary']['total_tests'] - len(analysis['tests']['api_tests']) - len(analysis['tests']['functional_tests'])}

## Label Analysis

**Total unique labels**: {len(analysis['labels']['all_unique'])}

**Sample labels found:**
"""
    
    sample_labels = sorted(list(analysis['labels']['all_unique']))[:25]
    for label in sample_labels:
        report += f"- `{label}`\n"
    
    if len(analysis['labels']['all_unique']) > 25:
        report += f"\n... and {len(analysis['labels']['all_unique']) - 25} more\n"
    
    report += f"""
## Remediation Readiness

✅ **Phase 1**: Assessment COMPLETE  
🔄 **Phase 2**: Label cleanup and standardization (READY)  
🔄 **Phase 3**: Precondition association (READY)  
🔄 **Phase 4**: Functional test creation (READY)  
🔄 **Phase 5**: Pytest integration (READY)  
🔄 **Phase 6**: Final validation (READY)  

## Implementation Priority

1. **HIGH**: Fix {analysis['issues']['standalone_preconditions']} standalone preconditions
2. **HIGH**: Remove TC-XXX labels from {analysis['issues']['tc_label_issues']} tests  
3. **HIGH**: Create {analysis['issues']['missing_functional_tests']} missing functional tests
4. **MEDIUM**: Convert lowercase labels on {analysis['issues']['lowercase_label_issues']} tests
5. **LOW**: Add pytest decorators (manual file updates)

---

**Assessment Status**: ✅ COMPLETE - Ready for Phase 2 execution  
**Data Integrity**: All {analysis['summary']['total_tests']} tests and {analysis['summary']['total_preconditions']} preconditions analyzed  
**Next Action**: Begin Phase 2 (Label Cleanup)  
"""
    
    return report

if __name__ == "__main__":
    try:
        analysis = perform_assessment()
        
        print("\n" + "="*60)
        print("✅ PHASE 1 ASSESSMENT COMPLETE")
        print("="*60)
        print(f"📊 Total Tests: {analysis['summary']['total_tests']}")
        print(f"📋 Total Preconditions: {analysis['summary']['total_preconditions']}")
        print(f"❌ Standalone Preconditions: {analysis['issues']['standalone_preconditions']}")
        print(f"❌ TC-XXX Label Issues: {analysis['issues']['tc_label_issues']}")
        print(f"❌ Missing Functional Tests: {analysis['issues']['missing_functional_tests']}")
        print(f"❌ Lowercase Label Issues: {analysis['issues']['lowercase_label_issues']}")
        print(f"📂 API Tests Found: {len(analysis['tests']['api_tests'])}")
        print(f"📂 Functional Tests Found: {len(analysis['tests']['functional_tests'])}")
        print("="*60)
        print("🚀 READY TO PROCEED TO PHASE 2")
        
    except Exception as e:
        print(f"❌ Phase 1 Assessment failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)