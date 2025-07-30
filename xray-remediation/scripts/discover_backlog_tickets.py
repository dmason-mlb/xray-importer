#!/usr/bin/env python3
"""
Discover all Test and Precondition tickets in FRAMED project backlog.
Uses JIRA MCP tools to query and export results.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "xray-api"))

def discover_backlog_tickets():
    """Query FRAMED project for Test and Precondition issues in backlog"""
    
    # JQL to find Test and Precondition issues in any sprint (backlog)
    # Note: In JIRA, items in backlog typically have Sprint field set
    jql = 'project = FRAMED AND issuetype in (Test, Precondition) AND Sprint is not EMPTY'
    
    print("="*80)
    print("FRAMED BACKLOG DISCOVERY - Test and Precondition Issues")
    print("="*80)
    print(f"\nExecuting JQL query: {jql}")
    print("\nNOTE: This script requires MCP JIRA tools to be available.")
    print("Please use Claude Code with MCP tools to execute the JIRA search.")
    print("\n" + "="*80)
    
    # Instructions for MCP execution
    print("\nTo execute this discovery:")
    print("1. Use MCP JIRA search tool with the JQL query above")
    print("2. Request fields: key, summary, issuetype, labels, sprint")
    print("3. Set limit to 1000 to get all results")
    print("4. Save results to JSON file")
    
    # Prepare output file
    output_dir = Path(__file__).parent.parent / 'logs'
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f'framed_backlog_discovery_{timestamp}.json'
    
    print(f"\nResults should be saved to: {output_file}")
    
    # Sample structure for the expected output
    sample_structure = {
        "timestamp": datetime.now().isoformat(),
        "jql": jql,
        "total": 0,
        "issues": [
            {
                "key": "FRAMED-XXX",
                "summary": "Test case summary",
                "issuetype": "Test",
                "labels": [],
                "sprint": "Sprint name or ID"
            }
        ],
        "statistics": {
            "Test": 0,
            "Precondition": 0
        }
    }
    
    print("\nExpected JSON structure:")
    print(json.dumps(sample_structure, indent=2))
    
    return output_file

def main():
    """Main entry point"""
    output_file = discover_backlog_tickets()
    
    print("\n" + "="*80)
    print("NEXT STEPS:")
    print("1. Execute the JIRA search using MCP tools")
    print("2. Save results to the specified JSON file")
    print("3. Run validate_removal_plan.py to analyze the results")
    print("="*80)

if __name__ == "__main__":
    main()