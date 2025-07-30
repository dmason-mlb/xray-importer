#!/usr/bin/env python3
"""
Execute bulk closure of remaining Xray tickets.
This script processes the remaining tickets that need to be closed.
"""

import json
import time
from pathlib import Path
from datetime import datetime

# List of remaining tickets to close (excluding the 3 already closed)
remaining_tickets = [
    "FRAMED-1374", "FRAMED-1373", "FRAMED-1372", "FRAMED-1371", "FRAMED-1370",
    "FRAMED-1369", "FRAMED-1368", "FRAMED-1367", "FRAMED-1366", "FRAMED-1365",
    "FRAMED-1364", "FRAMED-1363", "FRAMED-1362", "FRAMED-1361", "FRAMED-1360",
    "FRAMED-1359", "FRAMED-1358", "FRAMED-1357", "FRAMED-1356", "FRAMED-1355",
    "FRAMED-1354", "FRAMED-1353", "FRAMED-1352", "FRAMED-1351", "FRAMED-1350",
    "FRAMED-1349", "FRAMED-1348", "FRAMED-1347", "FRAMED-1346", "FRAMED-1345",
    "FRAMED-1344", "FRAMED-1343", "FRAMED-1342", "FRAMED-1341", "FRAMED-1340",
    "FRAMED-1339", "FRAMED-1338", "FRAMED-1337"
]

def main():
    """Process remaining tickets"""
    print(f"Remaining tickets to close: {len(remaining_tickets)}")
    print("\nThis script will output the MCP commands needed to close all tickets.")
    print("Execute these commands using Claude Code with MCP tools.\n")
    
    # Create log file for tracking
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = Path(__file__).parent.parent / 'logs' / f'bulk_closure_commands_{timestamp}.txt'
    
    with open(log_file, 'w') as f:
        f.write("# MCP Commands to Close Remaining Xray Tickets\n")
        f.write(f"# Generated: {datetime.now().isoformat()}\n")
        f.write(f"# Total tickets: {len(remaining_tickets)}\n\n")
        
        # Process in batches of 5
        batch_size = 5
        for i in range(0, len(remaining_tickets), batch_size):
            batch = remaining_tickets[i:i+batch_size]
            batch_num = (i // batch_size) + 1
            
            f.write(f"\n# Batch {batch_num} ({len(batch)} tickets)\n")
            print(f"Batch {batch_num}:")
            
            for ticket in batch:
                command = f'mcp__mcp-atlassian__jira_transition_issue(issue_key="{ticket}", transition_id="101", comment="Closing Xray ticket - removing from development backlog as part of cleanup operation")'
                f.write(f"{command}\n")
                print(f"  - {ticket}")
            
            if i + batch_size < len(remaining_tickets):
                f.write("# Wait 2 seconds between batches\n")
    
    print(f"\n✓ Commands saved to: {log_file}")
    print("\nTo execute:")
    print("1. Copy each command from the log file")
    print("2. Execute using MCP JIRA tools") 
    print("3. Wait 2 seconds between batches to avoid rate limits")
    
    # Also create a simple JSON file with just the ticket keys
    json_file = Path(__file__).parent.parent / 'logs' / f'remaining_tickets_{timestamp}.json'
    with open(json_file, 'w') as f:
        json.dump(remaining_tickets, f, indent=2)
    print(f"\n✓ Ticket list saved to: {json_file}")

if __name__ == "__main__":
    main()