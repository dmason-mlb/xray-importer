#!/usr/bin/env python3
"""
Minimal Phase 1 Assessment
Get basic information without complex fields
"""

import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent))
from auth_utils import XrayAPIClient, log_operation

def get_basic_test_info(client):
    """Get basic test information that we know works"""
    
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
                preconditions {
                    total
                }
            }
        }
    }
    """
    
    all_tests = []
    start = 0
    limit = 50
    
    # Get first batch
    result = client.execute_graphql_query(query, {
        "jql": "project = FRAMED",
        "limit": limit,
        "start": start
    })
    
    total = result['getTests']['total']
    all_tests.extend(result['getTests']['results'])
    
    print(f"Found {total} total tests")
    
    # Get remaining if needed
    while start + limit < total:
        start += limit
        result = client.execute_graphql_query(query, {
            "jql": "project = FRAMED",
            "limit": limit,
            "start": start
        })
        all_tests.extend(result['getTests']['results'])
    
    return all_tests

def get_basic_precondition_info(client):
    """Get basic precondition information"""
    
    query = """
    query GetPreconditions($jql: String!, $limit: Int!) {
        getPreconditions(jql: $jql, limit: $limit) {
            total
            results {
                issueId
            }
        }
    }
    """
    
    result = client.execute_graphql_query(query, {
        "jql": "project = FRAMED",
        "limit": 200
    })
    
    return result['getPreconditions']['results']

def minimal_assessment():
    """Perform minimal assessment with basic data"""
    
    print("🔍 Starting Minimal Phase 1 Assessment")
    
    client = XrayAPIClient()
    
    # Get basic test info
    print("📊 Fetching basic test information...")
    tests = get_basic_test_info(client)
    print(f"✅ Retrieved {len(tests)} tests")
    
    # Get basic precondition info
    print("📋 Fetching basic precondition information...")
    preconditions = get_basic_precondition_info(client)
    print(f"✅ Retrieved {len(preconditions)} preconditions")
    
    # Basic analysis
    analysis = {
        "tests": {
            "total": len(tests),
            "by_type": {},
            "with_preconditions": 0,
            "without_folders": 0
        },
        "preconditions": {
            "total": len(preconditions),
            "associated": 0,
            "standalone": 0
        },
        "folders": {}
    }
    
    # Analyze tests
    associated_preconditions = 0
    for test in tests:
        test_type = test.get('testType', {}).get('name', 'Unknown')
        analysis["tests"]["by_type"][test_type] = analysis["tests"]["by_type"].get(test_type, 0) + 1
        
        # Count preconditions
        precond_count = test.get('preconditions', {}).get('total', 0)
        if precond_count > 0:
            analysis["tests"]["with_preconditions"] += 1
            associated_preconditions += precond_count
        
        # Count folders
        folder_path = test.get('folder', {}).get('path', 'No folder')
        if folder_path == 'No folder':
            analysis["tests"]["without_folders"] += 1
        else:
            analysis["folders"][folder_path] = analysis["folders"].get(folder_path, 0) + 1
    
    analysis["preconditions"]["associated"] = associated_preconditions
    analysis["preconditions"]["standalone"] = len(preconditions) - associated_preconditions
    
    # Generate simple report
    report = generate_minimal_report(analysis)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save report
    report_dir = Path(__file__).parent.parent / 'documentation'
    report_dir.mkdir(exist_ok=True)
    report_file = report_dir / f"minimal_assessment_{timestamp}.md"
    
    with open(report_file, 'w') as f:
        f.write(report)
    
    # Save raw data
    backup_dir = Path(__file__).parent.parent / 'backups'
    backup_dir.mkdir(exist_ok=True)
    backup_file = backup_dir / f"minimal_backup_{timestamp}.json"
    
    with open(backup_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "tests": tests,
            "preconditions": preconditions,
            "analysis": analysis
        }, f, indent=2)
    
    print(f"📄 Report saved: {report_file}")
    print(f"💾 Data saved: {backup_file}")
    
    log_operation("Minimal Assessment Complete", analysis)
    
    return analysis

def generate_minimal_report(analysis):
    """Generate a minimal assessment report"""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report = f"""# Minimal Phase 1 Assessment Report

**Generated**: {timestamp}
**Project**: FRAMED

## Summary

- **Total Tests**: {analysis['tests']['total']}
- **Total Preconditions**: {analysis['preconditions']['total']}
- **Standalone Preconditions**: {analysis['preconditions']['standalone']} ❌
- **Tests with Preconditions**: {analysis['tests']['with_preconditions']}
- **Tests without Folders**: {analysis['tests']['without_folders']}

## Test Types

"""
    
    for test_type, count in analysis['tests']['by_type'].items():
        report += f"- **{test_type}**: {count} tests\n"
    
    report += f"""
## Folder Distribution

"""
    
    for folder, count in analysis['folders'].items():
        report += f"- **{folder}**: {count} tests\n"
    
    report += f"""
## Issues Identified

1. **Standalone Preconditions**: {analysis['preconditions']['standalone']} preconditions not associated with tests
2. **Tests without Folders**: {analysis['tests']['without_folders']} tests need folder organization

## Next Steps

Need to run detailed assessment to identify:
- Tests with TC-XXX labels
- Tests with lowercase labels  
- Missing functional tests
- Specific label issues

This minimal assessment confirms the project structure and identifies the key issue of {analysis['preconditions']['standalone']} standalone preconditions.
"""
    
    return report

if __name__ == "__main__":
    try:
        analysis = minimal_assessment()
        print("\n✅ Minimal Phase 1 Assessment completed")
        print(f"📊 Key findings:")
        print(f"   - {analysis['tests']['total']} total tests")
        print(f"   - {analysis['preconditions']['standalone']} standalone preconditions")
        print(f"   - {analysis['tests']['without_folders']} tests without folders")
        
    except Exception as e:
        print(f"❌ Assessment failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)