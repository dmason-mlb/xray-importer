#!/usr/bin/env python3
"""
Generate update commands for functional tests
Creates a report with the exact updates needed for each test
"""
import json
import sys
from pathlib import Path
from datetime import datetime

def determine_priority(labels):
    """Determine priority based on labels"""
    if 'critical' in labels:
        return 'Critical'
    elif 'high' in labels:
        return 'High'
    elif 'low' in labels:
        return 'Low'
    else:
        return 'Medium'  # Default

def main():
    # Load comprehensive update plan
    plan_path = Path(__file__).parent.parent / "logs" / "comprehensive_update_plan.json"
    with open(plan_path, 'r') as f:
        plan = json.load(f)
    
    # Load test keys
    tests_file = Path(__file__).parent.parent / "logs" / "tests_to_update_labels.json"
    with open(tests_file, 'r') as f:
        test_data = json.load(f)
    
    print(f"=== UPDATE COMMANDS FOR FUNCTIONAL TESTS ===")
    print(f"Generated: {datetime.now().isoformat()}")
    print(f"Total tests to update: {len(plan['updates'])}\n")
    
    # Generate commands for each test
    commands = []
    
    for update in plan['updates']:
        key = update['key']
        cmd = {
            'key': key,
            'updates': []
        }
        
        # Labels update
        if update.get('new_labels'):
            cmd['updates'].append({
                'type': 'labels',
                'old': [l for l in update['new_labels'] if l == 'functional'],
                'new': update['new_labels']
            })
        
        # Priority update
        if update.get('new_priority'):
            cmd['updates'].append({
                'type': 'priority',
                'new': update['new_priority']
            })
        
        commands.append(cmd)
    
    # Create update report
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_tests': len(commands),
        'commands': commands,
        'summary': {
            'label_updates': sum(1 for c in commands if any(u['type'] == 'labels' for u in c['updates'])),
            'priority_updates': sum(1 for c in commands if any(u['type'] == 'priority' for u in c['updates']))
        }
    }
    
    # Save report
    output_path = Path(__file__).parent.parent / "logs" / "update_commands.json"
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("LABEL UPDATES NEEDED:")
    print("-" * 50)
    for cmd in commands:
        for update in cmd['updates']:
            if update['type'] == 'labels':
                print(f"{cmd['key']}: functional → functional_test")
    
    print(f"\nPRIORITY UPDATES NEEDED:")
    print("-" * 50)
    for cmd in commands:
        for update in cmd['updates']:
            if update['type'] == 'priority':
                print(f"{cmd['key']}: None → {update['new']}")
    
    print(f"\nUpdate commands saved to: {output_path}")
    
    # Create a simple shell script for manual updates
    create_shell_script(commands)

def create_shell_script(commands):
    """Create a shell script with curl commands for manual updates"""
    script_content = """#!/bin/bash
# Manual update script for functional tests
# Generated: {}
# NOTE: Requires JIRA_EMAIL and JIRA_API_TOKEN environment variables

if [ -z "$JIRA_EMAIL" ] || [ -z "$JIRA_API_TOKEN" ]; then
    echo "Error: JIRA_EMAIL and JIRA_API_TOKEN environment variables must be set"
    exit 1
fi

JIRA_BASE_URL="https://jira.mlbinfra.com"

echo "=== UPDATING FUNCTIONAL TESTS ==="
""".format(datetime.now().isoformat())
    
    for cmd in commands:
        key = cmd['key']
        
        # Get the labels from the first update
        new_labels = None
        new_priority = None
        
        for update in cmd['updates']:
            if update['type'] == 'labels':
                new_labels = update['new']
            elif update['type'] == 'priority':
                new_priority = update['new']
        
        if new_labels or new_priority:
            script_content += f"\necho \"Updating {key}...\"\n"
            
            # Build the JSON payload
            fields = {}
            if new_labels:
                fields['labels'] = new_labels
            if new_priority:
                # Note: This would need to map priority names to IDs
                fields['priority'] = {'name': new_priority}
            
            json_payload = json.dumps({'fields': fields})
            
            script_content += f"""curl -X PUT \\
  -H "Content-Type: application/json" \\
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \\
  -d '{json_payload}' \\
  "$JIRA_BASE_URL/rest/api/2/issue/{key}"
"""
            script_content += "echo\n"
    
    script_content += "\necho \"\\n=== UPDATE COMPLETE ===\"\n"
    
    # Save the script
    script_path = Path(__file__).parent.parent / "scripts" / "manual_update_functional_tests.sh"
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    # Make it executable
    import os
    os.chmod(script_path, 0o755)
    
    print(f"\nManual update script created: {script_path}")

if __name__ == "__main__":
    main()