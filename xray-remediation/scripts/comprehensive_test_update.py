#!/usr/bin/env python3
"""
Comprehensive update for all functional tests:
1. Update labels from 'functional' to 'functional_test'
2. Set priorities based on labels
3. Clean up test steps (remove HTML entities, arrows, add expected results)
"""
import json
import sys
import time
import html
import re
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir / 'xray-api'))
from auth_utils import XrayAPIClient, log_operation

def clean_step_text(text):
    """Clean HTML entities and arrow artifacts from step text"""
    # Decode HTML entities
    text = html.unescape(text)
    
    # Replace arrow variants with clean arrow
    text = text.replace('&rarr;', ' → ')
    text = text.replace('&nbsp;', ' ')
    text = text.replace('  ', ' ')  # Multiple spaces to single
    
    return text.strip()

def parse_step_with_result(action_text):
    """Parse step text and extract action and expected result"""
    action_text = clean_step_text(action_text)
    
    # Split by arrow to get action and results
    parts = [p.strip() for p in action_text.split('→')]
    
    if len(parts) > 1:
        # First part is action, rest are expected results
        action = parts[0]
        expected = ' → '.join(parts[1:])
    else:
        # No arrow found, try to infer expected result
        action = action_text
        expected = infer_expected_result(action)
    
    return action, expected

def infer_expected_result(action):
    """Infer expected result based on action context"""
    action_lower = action.lower()
    
    if 'tap' in action_lower or 'click' in action_lower:
        return "Action is performed successfully"
    elif 'wait' in action_lower:
        return "System responds within expected time"
    elif 'verify' in action_lower or 'check' in action_lower:
        return "Verification passes"
    elif 'navigate' in action_lower:
        return "Navigation completes successfully"
    elif 'display' in action_lower or 'show' in action_lower:
        return "Content displays correctly"
    elif 'scroll' in action_lower:
        return "Scrolling works smoothly"
    elif 'open' in action_lower:
        return "Opens successfully"
    elif 'close' in action_lower:
        return "Closes properly"
    elif 'load' in action_lower:
        return "Loads successfully"
    else:
        return "Expected behavior occurs"

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

def comprehensive_test_update():
    client = XrayAPIClient()
    
    # Load the functional tests data
    tests_path = Path(__file__).parent.parent / "test-data" / "functional_tests_xray.json"
    with open(tests_path, 'r') as f:
        test_data = json.load(f)
    
    # Get all tests
    all_tests = []
    for test in test_data['tests']:
        if 'jiraKey' in test:
            all_tests.append({
                'key': test['jiraKey'],
                'test_info': test['testInfo']
            })
    
    print(f"=== COMPREHENSIVE FUNCTIONAL TEST UPDATE ===")
    print(f"Total tests to process: {len(all_tests)}")
    
    # Results tracking
    results = {
        'timestamp': datetime.now().isoformat(),
        'total_tests': len(all_tests),
        'updates': [],
        'errors': []
    }
    
    # Process each test
    for i, test_data in enumerate(all_tests, 1):
        key = test_data['key']
        test_info = test_data['test_info']
        
        print(f"\n[{i}/{len(all_tests)}] Processing {key}...")
        
        try:
            # First, get the test details including issueId
            query = """
            query GetTest($jql: String!) {
                getTests(jql: $jql, limit: 1) {
                    results {
                        issueId
                        jira(fields: ["key", "labels", "priority"])
                        testType {
                            name
                        }
                        steps {
                            id
                            action
                            result
                            data
                        }
                    }
                }
            }
            """
            
            variables = {
                "jql": f"key = {key}"
            }
            
            result = client.execute_graphql_query(query, variables)
            
            if not result or 'getTests' not in result or not result['getTests']['results']:
                print(f"  ✗ Test not found")
                results['errors'].append({
                    'key': key,
                    'error': 'Test not found'
                })
                continue
            
            test = result['getTests']['results'][0]
            issue_id = test['issueId']
            current_labels = test['jira'].get('labels', [])
            current_priority = test['jira'].get('priority', {}).get('name', 'None')
            current_steps = test.get('steps', [])
            
            print(f"  Issue ID: {issue_id}")
            print(f"  Current labels: {current_labels}")
            print(f"  Current priority: {current_priority}")
            print(f"  Current steps: {len(current_steps)}")
            
            # Prepare updates
            updates_needed = []
            
            # 1. Check labels
            new_labels = []
            label_update_needed = False
            for label in current_labels:
                if label == 'functional':
                    new_labels.append('functional_test')
                    label_update_needed = True
                else:
                    new_labels.append(label)
            
            if label_update_needed:
                updates_needed.append(f"Update labels: functional → functional_test")
            
            # 2. Check priority
            expected_priority = determine_priority(new_labels)
            priority_update_needed = (current_priority != expected_priority)
            
            if priority_update_needed:
                updates_needed.append(f"Update priority: {current_priority} → {expected_priority}")
            
            # 3. Check steps for cleanup
            steps_need_update = False
            cleaned_steps = []
            
            for step in current_steps:
                action = step.get('action', '')
                result = step.get('result', '')
                
                # Check if cleanup needed
                if ('&nbsp;' in action or '&rarr;' in action or 
                    '&nbsp;' in result or '&rarr;' in result or
                    not result.strip()):
                    steps_need_update = True
                
                # Clean and parse
                if '→' in action and not result:
                    # Action contains both action and result
                    clean_action, clean_result = parse_step_with_result(action)
                else:
                    clean_action = clean_step_text(action)
                    clean_result = clean_step_text(result) if result else infer_expected_result(clean_action)
                
                cleaned_steps.append({
                    'id': step.get('id'),
                    'action': clean_action,
                    'result': clean_result,
                    'data': step.get('data', '')
                })
            
            if steps_need_update:
                updates_needed.append(f"Clean up {len(cleaned_steps)} steps")
            
            # Apply updates if needed
            if updates_needed:
                print(f"  Updates needed: {', '.join(updates_needed)}")
                
                # Since we can't use updateTest, we'll need to delete and recreate
                # For now, let's just document what needs to be done
                update_record = {
                    'key': key,
                    'issueId': issue_id,
                    'updates_needed': updates_needed,
                    'new_labels': new_labels if label_update_needed else None,
                    'new_priority': expected_priority if priority_update_needed else None,
                    'cleaned_steps': cleaned_steps if steps_need_update else None
                }
                
                results['updates'].append(update_record)
                print(f"  ✓ Update plan created")
            else:
                print(f"  ✓ No updates needed")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            results['errors'].append({
                'key': key,
                'error': str(e)
            })
        
        # Rate limiting
        time.sleep(0.3)
    
    # Save results
    output_path = Path(__file__).parent.parent / "logs" / "comprehensive_update_plan.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Summary
    print(f"\n=== SUMMARY ===")
    print(f"Total tests processed: {len(all_tests)}")
    print(f"Tests needing updates: {len(results['updates'])}")
    print(f"Errors: {len(results['errors'])}")
    
    # Count update types
    label_updates = sum(1 for u in results['updates'] if u.get('new_labels'))
    priority_updates = sum(1 for u in results['updates'] if u.get('new_priority'))
    step_updates = sum(1 for u in results['updates'] if u.get('cleaned_steps'))
    
    print(f"\nUpdate breakdown:")
    print(f"  Label updates needed: {label_updates}")
    print(f"  Priority updates needed: {priority_updates}")
    print(f"  Step cleanup needed: {step_updates}")
    
    print(f"\nUpdate plan saved to: {output_path}")
    
    # Create a script to apply updates via delete/recreate
    create_update_script(results)

def create_update_script(results):
    """Create a script to apply the updates by recreating tests"""
    script_content = '''#!/usr/bin/env python3
"""
Apply comprehensive updates by deleting and recreating tests
Generated: {timestamp}
"""
import json
import sys
import time
from pathlib import Path

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir / 'xray-api'))
from auth_utils import XrayAPIClient

def apply_updates():
    client = XrayAPIClient()
    
    # Load update plan
    plan_path = Path(__file__).parent.parent / "logs" / "comprehensive_update_plan.json"
    with open(plan_path, 'r') as f:
        plan = json.load(f)
    
    updates = plan['updates']
    print(f"=== APPLYING COMPREHENSIVE UPDATES ===")
    print(f"Tests to update: {{len(updates)}}")
    
    # NOTE: This is a placeholder script
    # The actual implementation would:
    # 1. Delete the test
    # 2. Recreate it with updated labels, priority, and steps
    # 3. Reassociate preconditions
    
    print("\\nThis script is a placeholder.")
    print("To apply updates, use the Xray UI or implement delete/recreate logic.")
    
if __name__ == "__main__":
    apply_updates()
'''.format(timestamp=datetime.now().isoformat())
    
    script_path = Path(__file__).parent.parent / "scripts" / "apply_comprehensive_updates.py"
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    print(f"\nUpdate script created: {script_path}")

if __name__ == "__main__":
    comprehensive_test_update()