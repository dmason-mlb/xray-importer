#!/usr/bin/env python3
"""
XRAY Test Manager CLI Demo

This script demonstrates all the functionality that would be available in the macOS app
through a command-line interface. It showcases the core features like fetching tests,
filtering, batch operations, and AI-powered step generation.
"""

import os
import sys
import json
import argparse
from typing import List, Dict, Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from test_manager import XrayTestManager, TestSummary, TestStep, BatchOperationResult
from ai_step_generator import AIStepGenerator, StepProposal

class XrayTestManagerCLI:
    """Command-line interface for XRAY Test Manager"""
    
    def __init__(self):
        self.test_manager = XrayTestManager()
        self.step_generator = AIStepGenerator(self.test_manager)
    
    def list_projects(self):
        """List available projects"""
        print("Available Projects:")
        projects = self.test_manager.get_available_projects()
        for project in projects:
            print(f"  {project['key']}: {project['name']}")
    
    def list_tests(self, project_key: str, limit: int = 10, filters: Optional[Dict] = None):
        """List tests for a project"""
        print(f"\nFetching tests for project {project_key}...")
        
        try:
            tests = self.test_manager.fetch_tests_summary(project_key, limit=limit, filters=filters)
            
            if not tests:
                print("No tests found.")
                return
            
            print(f"\nFound {len(tests)} tests:")
            print("-" * 80)
            print(f"{'Key':<12} {'Summary':<30} {'Labels':<20} {'Steps':<8} {'Priority':<10}")
            print("-" * 80)
            
            for test in tests:
                labels_str = ", ".join(test.labels[:3]) if test.labels else "None"
                if len(labels_str) > 20:
                    labels_str = labels_str[:17] + "..."
                
                summary_str = test.summary[:30] if len(test.summary) > 30 else test.summary
                steps_str = f"{test.steps_count} steps" if test.has_steps else "No steps"
                
                print(f"{test.key:<12} {summary_str:<30} {labels_str:<20} {steps_str:<8} {test.priority:<10}")
            
            print("-" * 80)
            
        except Exception as e:
            print(f"Error fetching tests: {e}")
    
    def search_tests(self, project_key: str, keywords: str):
        """Search tests by keywords"""
        print(f"\nSearching for tests containing '{keywords}' in project {project_key}...")
        
        try:
            tests = self.test_manager.search_tests_by_keywords(project_key, keywords)
            
            if not tests:
                print("No tests found matching the search criteria.")
                return
            
            print(f"\nFound {len(tests)} tests matching '{keywords}':")
            print("-" * 60)
            
            for test in tests:
                print(f"  {test.key}: {test.summary}")
                if test.labels:
                    print(f"    Labels: {', '.join(test.labels)}")
                print(f"    Steps: {test.steps_count}, Priority: {test.priority}")
                print()
            
        except Exception as e:
            print(f"Error searching tests: {e}")
    
    def show_tests_without_steps(self, project_key: str, limit: int = 10):
        """Show tests that don't have steps"""
        print(f"\nFetching tests without steps for project {project_key}...")
        
        try:
            tests = self.test_manager.get_tests_without_steps(project_key, limit=limit)
            
            if not tests:
                print("All tests have steps defined!")
                return
            
            print(f"\nFound {len(tests)} tests without steps:")
            print("-" * 60)
            
            for test in tests:
                print(f"  {test.key}: {test.summary}")
                if test.labels:
                    print(f"    Labels: {', '.join(test.labels)}")
                if test.folder_path:
                    print(f"    Folder: {test.folder_path}")
                print()
            
        except Exception as e:
            print(f"Error fetching tests without steps: {e}")
    
    def show_test_details(self, issue_id: str):
        """Show detailed information for a specific test"""
        print(f"\nFetching details for test {issue_id}...")
        
        try:
            details = self.test_manager.get_test_details(issue_id)
            
            if not details:
                print("Test not found.")
                return
            
            jira_data = details.get("jira", {})
            
            print(f"\n=== Test Details ===")
            print(f"Key: {jira_data.get('key', 'N/A')}")
            print(f"Summary: {jira_data.get('summary', 'N/A')}")
            print(f"Priority: {jira_data.get('priority', {}).get('name', 'N/A')}")
            print(f"Assignee: {jira_data.get('assignee', {}).get('displayName', 'Unassigned')}")
            
            if jira_data.get('labels'):
                print(f"Labels: {', '.join(jira_data['labels'])}")
            
            if details.get('folder', {}).get('path'):
                print(f"Folder: {details['folder']['path']}")
            
            print(f"\nDescription:")
            print(jira_data.get('description', 'No description'))
            
            steps = details.get('steps', [])
            if steps:
                print(f"\nTest Steps ({len(steps)}):")
                for i, step in enumerate(steps, 1):
                    print(f"  {i}. {step.get('action', 'N/A')}")
                    if step.get('data'):
                        print(f"     Data: {step['data']}")
                    if step.get('result'):
                        print(f"     Expected: {step['result']}")
                    print()
            else:
                print("\nNo test steps defined.")
            
        except Exception as e:
            print(f"Error fetching test details: {e}")
    
    def generate_step_proposals(self, project_key: str, limit: int = 5):
        """Generate AI-powered step proposals for tests without steps"""
        print(f"\nGenerating step proposals for tests without steps in project {project_key}...")
        
        try:
            # Get tests without steps
            tests_without_steps = self.test_manager.get_tests_without_steps(project_key, limit=limit)
            
            if not tests_without_steps:
                print("All tests already have steps defined!")
                return
            
            print(f"Found {len(tests_without_steps)} tests without steps. Generating proposals...")
            
            # Generate proposals
            proposals = self.step_generator.generate_steps_for_multiple_tests(tests_without_steps)
            
            if not proposals:
                print("No proposals generated.")
                return
            
            print(f"\nGenerated proposals for {len(proposals)} tests:")
            print("=" * 80)
            
            for proposal in proposals:
                print(f"\n{proposal.test_key}: {proposal.test_summary}")
                print(f"Overall Confidence: {proposal.overall_confidence:.2f}")
                print(f"Primary Category: {proposal.metadata['primary_category']}")
                print(f"Complexity: {proposal.metadata['complexity']}")
                
                print("\nProposed Steps:")
                for i, step in enumerate(proposal.proposed_steps, 1):
                    print(f"  {i}. {step.action}")
                    if step.data:
                        print(f"     Data: {step.data}")
                    if step.result:
                        print(f"     Expected: {step.result}")
                    print(f"     Confidence: {step.confidence:.2f}")
                    print(f"     Reasoning: {step.reasoning}")
                    print()
                
                print("-" * 60)
            
            # Ask if user wants to export proposals
            response = input("\nWould you like to export these proposals to JSON? (y/n): ").lower().strip()
            if response == 'y':
                filename = f"step_proposals_{project_key}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                self.step_generator.export_proposals_to_json(proposals, filename)
                print(f"Proposals exported to {filename}")
            
        except Exception as e:
            print(f"Error generating step proposals: {e}")
    
    def show_project_labels(self, project_key: str):
        """Show all labels used in a project"""
        print(f"\nFetching labels for project {project_key}...")
        
        try:
            labels = self.test_manager.get_all_labels(project_key)
            
            if not labels:
                print("No labels found.")
                return
            
            print(f"\nFound {len(labels)} unique labels:")
            print("-" * 40)
            
            # Group labels by first letter for better display
            current_letter = ""
            for label in labels:
                first_letter = label[0].upper()
                if first_letter != current_letter:
                    current_letter = first_letter
                    print(f"\n{current_letter}:")
                
                print(f"  {label}")
            
        except Exception as e:
            print(f"Error fetching labels: {e}")
    
    def batch_move_tests(self, project_key: str, test_keys: List[str], folder_path: str):
        """Demonstrate batch moving tests to a folder"""
        print(f"\nMoving {len(test_keys)} tests to folder '{folder_path}'...")
        
        try:
            # Convert test keys to issue IDs (simplified - in real app would need lookup)
            issue_ids = test_keys  # Assuming keys are passed as issue IDs for demo
            
            result = self.test_manager.batch_move_to_folder(project_key, issue_ids, folder_path)
            
            print(f"\nBatch Move Results:")
            print(f"  Successful: {len(result.successful)}")
            print(f"  Failed: {len(result.failed)}")
            print(f"  Total: {result.total}")
            
            if result.failed:
                print("\nFailed operations:")
                for issue_id, error in result.failed:
                    print(f"  {issue_id}: {error}")
            
        except Exception as e:
            print(f"Error during batch move: {e}")
    
    def export_tests(self, project_key: str, output_file: str, filters: Optional[Dict] = None):
        """Export tests to JSON file"""
        print(f"\nExporting tests from project {project_key} to {output_file}...")
        
        try:
            count = self.test_manager.export_tests_to_json(project_key, output_file, filters)
            print(f"Successfully exported {count} tests to {output_file}")
            
        except Exception as e:
            print(f"Error exporting tests: {e}")

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="XRAY Test Manager CLI Demo")
    parser.add_argument("command", choices=[
        "list-projects", "list-tests", "search-tests", "tests-without-steps", 
        "test-details", "generate-proposals", "project-labels", "export-tests"
    ])
    parser.add_argument("--project", "-p", help="Project key")
    parser.add_argument("--limit", "-l", type=int, default=10, help="Limit results")
    parser.add_argument("--keywords", "-k", help="Search keywords")
    parser.add_argument("--issue-id", "-i", help="Issue ID for test details")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--labels", nargs="+", help="Filter by labels")
    parser.add_argument("--priority", help="Filter by priority")
    
    args = parser.parse_args()
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Create CLI instance
    cli = XrayTestManagerCLI()
    
    try:
        if args.command == "list-projects":
            cli.list_projects()
        
        elif args.command == "list-tests":
            if not args.project:
                print("Error: --project is required for list-tests command")
                return
            
            filters = {}
            if args.labels:
                filters["labels"] = args.labels
            if args.priority:
                filters["priority"] = args.priority
            
            cli.list_tests(args.project, args.limit, filters)
        
        elif args.command == "search-tests":
            if not args.project or not args.keywords:
                print("Error: --project and --keywords are required for search-tests command")
                return
            
            cli.search_tests(args.project, args.keywords)
        
        elif args.command == "tests-without-steps":
            if not args.project:
                print("Error: --project is required for tests-without-steps command")
                return
            
            cli.show_tests_without_steps(args.project, args.limit)
        
        elif args.command == "test-details":
            if not args.issue_id:
                print("Error: --issue-id is required for test-details command")
                return
            
            cli.show_test_details(args.issue_id)
        
        elif args.command == "generate-proposals":
            if not args.project:
                print("Error: --project is required for generate-proposals command")
                return
            
            cli.generate_step_proposals(args.project, args.limit)
        
        elif args.command == "project-labels":
            if not args.project:
                print("Error: --project is required for project-labels command")
                return
            
            cli.show_project_labels(args.project)
        
        elif args.command == "export-tests":
            if not args.project or not args.output:
                print("Error: --project and --output are required for export-tests command")
                return
            
            filters = {}
            if args.labels:
                filters["labels"] = args.labels
            if args.priority:
                filters["priority"] = args.priority
            
            cli.export_tests(args.project, args.output, filters)
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()