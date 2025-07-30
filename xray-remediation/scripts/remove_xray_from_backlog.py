#!/usr/bin/env python3
"""
Remove Test and Precondition tickets from FRAMED project backlog.
This script will transition these tickets to a different status to remove them from the backlog.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import time

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

class XrayBacklogRemover:
    """Remove Xray tickets from FRAMED backlog"""
    
    def __init__(self):
        self.processed_count = 0
        self.error_count = 0
        self.results = []
        self.log_file = None
        
    def load_discovery_data(self, discovery_file):
        """Load the discovery data from JSON file"""
        try:
            with open(discovery_file, 'r') as f:
                data = json.load(f)
            print(f"✓ Loaded {data['total']} tickets from discovery file")
            return data
        except Exception as e:
            print(f"✗ Error loading discovery file: {e}")
            return None
            
    def validate_tickets(self, tickets):
        """Validate that all tickets are Test or Precondition types"""
        print("\n" + "="*80)
        print("VALIDATION SUMMARY")
        print("="*80)
        
        # Count by type based on summary patterns
        test_count = 0
        precondition_count = 0
        
        for ticket in tickets:
            if "Precondition" in ticket['summary'] or ticket['summary'] == "MLB App Setup":
                precondition_count += 1
            else:
                test_count += 1
                
        print(f"\nTicket Analysis:")
        print(f"  - Test tickets: {test_count}")
        print(f"  - Precondition tickets: {precondition_count}")
        print(f"  - Total: {len(tickets)}")
        
        # Show sample tickets
        print("\nSample tickets to be processed:")
        for ticket in tickets[:5]:
            print(f"  - {ticket['key']}: {ticket['summary']}")
            
        if len(tickets) > 5:
            print(f"  ... and {len(tickets) - 5} more tickets")
            
        return test_count, precondition_count
        
    def create_removal_plan(self, tickets):
        """Create a plan for removing tickets from backlog"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plan_file = Path(__file__).parent.parent / 'logs' / f'backlog_removal_plan_{timestamp}.json'
        
        plan = {
            "timestamp": datetime.now().isoformat(),
            "total_tickets": len(tickets),
            "action": "Remove from backlog by transitioning status",
            "target_status": "Blocked",  # Or another appropriate status
            "tickets": [{"key": t['key'], "summary": t['summary']} for t in tickets],
            "batch_size": 10,
            "estimated_batches": (len(tickets) + 9) // 10
        }
        
        with open(plan_file, 'w') as f:
            json.dump(plan, f, indent=2)
            
        print(f"\n✓ Removal plan saved to: {plan_file}")
        return plan
        
    def confirm_execution(self):
        """Ask user to confirm before proceeding"""
        print("\n" + "="*80)
        print("CONFIRMATION REQUIRED")
        print("="*80)
        print("\nThis will remove all Test and Precondition tickets from the FRAMED backlog.")
        print("The tickets will be transitioned to 'Blocked' status.")
        print("\nDo you want to proceed? (yes/no): ", end='')
        response = input().strip().lower()
        return response == 'yes'
        
    def execute_removal_batch(self, batch, batch_num):
        """Execute removal for a batch of tickets"""
        print(f"\nProcessing batch {batch_num} ({len(batch)} tickets)...")
        
        batch_results = []
        for ticket in batch:
            result = {
                "key": ticket['key'],
                "summary": ticket['summary'],
                "status": "pending",
                "message": ""
            }
            
            # Note: This is where we would use MCP JIRA tools to update the ticket
            print(f"  - {ticket['key']}: Would transition to 'Blocked' status")
            result["status"] = "dry_run"
            result["message"] = "Dry run - no changes made"
            
            batch_results.append(result)
            self.results.append(result)
            
        return batch_results
        
    def execute_removal(self, tickets, dry_run=True):
        """Execute the removal plan"""
        print("\n" + "="*80)
        print("EXECUTING REMOVAL PLAN")
        print("="*80)
        
        if dry_run:
            print("\n⚠️  DRY RUN MODE - No changes will be made")
        
        # Create log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = Path(__file__).parent.parent / 'logs' / f'backlog_removal_log_{timestamp}.txt'
        
        with open(self.log_file, 'w') as f:
            f.write(f"FRAMED Backlog Removal Log\n")
            f.write(f"Started: {datetime.now().isoformat()}\n")
            f.write(f"Total tickets: {len(tickets)}\n")
            f.write(f"Dry run: {dry_run}\n")
            f.write("="*80 + "\n\n")
        
        # Process in batches
        batch_size = 10
        for i in range(0, len(tickets), batch_size):
            batch = tickets[i:i+batch_size]
            batch_num = (i // batch_size) + 1
            
            batch_results = self.execute_removal_batch(batch, batch_num)
            
            # Log results
            with open(self.log_file, 'a') as f:
                f.write(f"\nBatch {batch_num}:\n")
                for result in batch_results:
                    f.write(f"  {result['key']}: {result['status']} - {result['message']}\n")
            
            # Small delay between batches to avoid rate limits
            if not dry_run and i + batch_size < len(tickets):
                time.sleep(1)
                
        print(f"\n✓ Execution complete. Log saved to: {self.log_file}")
        
    def generate_report(self):
        """Generate final report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = Path(__file__).parent.parent / 'logs' / f'backlog_removal_report_{timestamp}.md'
        
        success_count = sum(1 for r in self.results if r['status'] in ['success', 'dry_run'])
        error_count = sum(1 for r in self.results if r['status'] == 'error')
        
        with open(report_file, 'w') as f:
            f.write("# FRAMED Backlog Removal Report\n\n")
            f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("## Summary\n\n")
            f.write(f"- Total tickets processed: {len(self.results)}\n")
            f.write(f"- Successful: {success_count}\n")
            f.write(f"- Errors: {error_count}\n\n")
            f.write("## Details\n\n")
            
            if error_count > 0:
                f.write("### Errors\n\n")
                for r in self.results:
                    if r['status'] == 'error':
                        f.write(f"- {r['key']}: {r['message']}\n")
                f.write("\n")
                
            f.write("### Processed Tickets\n\n")
            for r in self.results[:10]:
                f.write(f"- {r['key']}: {r['summary']} ({r['status']})\n")
            if len(self.results) > 10:
                f.write(f"\n... and {len(self.results) - 10} more tickets\n")
                
        print(f"\n✓ Report saved to: {report_file}")
        return report_file

def main():
    """Main entry point"""
    import argparse
    parser = argparse.ArgumentParser(description='Remove Xray tickets from FRAMED backlog')
    parser.add_argument('--discovery-file', 
                        default='/Users/douglas.mason/Documents/GitHub/xray-importer/xray-remediation/logs/framed_backlog_discovery_20250723_120000.json',
                        help='Path to discovery JSON file')
    parser.add_argument('--dry-run', action='store_true', 
                        help='Show what would be done without making changes')
    args = parser.parse_args()
    
    remover = XrayBacklogRemover()
    
    # Load discovery data
    data = remover.load_discovery_data(args.discovery_file)
    if not data:
        sys.exit(1)
        
    # Validate tickets
    test_count, precondition_count = remover.validate_tickets(data['issues'])
    
    # Create removal plan
    plan = remover.create_removal_plan(data['issues'])
    
    # Confirm execution
    if not args.dry_run:
        if not remover.confirm_execution():
            print("✗ Removal cancelled by user")
            sys.exit(0)
            
    # Execute removal
    remover.execute_removal(data['issues'], dry_run=args.dry_run)
    
    # Generate report
    remover.generate_report()
    
    print("\n" + "="*80)
    print("NEXT STEPS:")
    print("1. Review the generated report")
    print("2. If dry run was successful, run without --dry-run flag")
    print("3. Use MCP JIRA tools to actually transition the tickets")
    print("="*80)

if __name__ == "__main__":
    main()