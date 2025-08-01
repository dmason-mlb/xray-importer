#!/usr/bin/env python3
"""
Upload tests to XRAY using MCP JIRA tools.
This script interfaces with the actual JIRA API through MCP.
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import html

# This script is designed to be called from Claude Code with MCP tools available

class MCPXrayUploader:
    """Manages test upload to XRAY using MCP JIRA tools"""
    
    def __init__(self, project_key: str = "FRAMED"):
        self.project_key = project_key
        self.state_file = Path(__file__).parent.parent / 'logs' / 'mcp_upload_state.json'
        self.state = self._load_or_create_state()
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def _load_or_create_state(self) -> Dict:
        """Load existing state or create new one"""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        
        return {
            "started": datetime.now().isoformat(),
            "phase": "initial",
            "existing_tests": {},
            "existing_preconditions": {},
            "precondition_map": {},
            "uploaded_tests": {},
            "failed_tests": [],
            "folders_created": [],
            "statistics": {
                "api_tests_uploaded": 0,
                "functional_tests_uploaded": 0,
                "preconditions_created": 0,
                "preconditions_reused": 0,
                "duplicates_skipped": 0
            }
        }
    
    def _save_state(self):
        """Save current state to file"""
        self.state_file.parent.mkdir(exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def get_discovery_jql(self) -> Dict[str, str]:
        """Get JQL queries for discovery phase"""
        return {
            "tests": f'project = {self.project_key} AND issuetype = Test AND labels in (team_page)',
            "preconditions": f'project = {self.project_key} AND issuetype = Precondition'
        }
    
    def prepare_test_for_upload(self, test_data: Dict, test_source: str) -> Dict:
        """Prepare test data for JIRA creation"""
        if test_source == "api":
            return self._prepare_api_test(test_data)
        else:
            return self._prepare_functional_test(test_data)
    
    def _prepare_api_test(self, test: Dict) -> Dict:
        """Prepare API test for JIRA creation"""
        # Extract precondition if exists
        precondition_text = test.get('preconditions', '')
        
        # Build description
        description_parts = [
            f"Test ID: {test['testCaseId']}",
            f"Priority: {test['priority']}",
            f"Platforms: {', '.join(test.get('platforms', []))}",
            f"Folder: {test['folderStructure']}"
        ]
        
        if precondition_text:
            description_parts.append(f"\nPrecondition: {precondition_text}")
        
        # Format test steps
        steps_text = "\nTest Steps:\n"
        for i, step in enumerate(test.get('testSteps', []), 1):
            step_text = html.unescape(step.get('step', ''))
            expected = html.unescape(step.get('expectedResult', ''))
            steps_text += f"\n{i}. {step_text}\n   Expected: {expected}\n"
        
        return {
            "project_key": self.project_key,
            "summary": test['title'],
            "issue_type": "Test",
            "description": '\n'.join(description_parts) + steps_text,
            "labels": test['tags'],
            "priority": test['priority'],
            "additional_fields": {
                "customfield_10100": "Generic"  # Test Type field (may vary by instance)
            }
        }
    
    def _prepare_functional_test(self, test: Dict) -> Dict:
        """Prepare functional test for JIRA creation"""
        test_info = test['testInfo']
        
        # Build description including folder info
        description = test_info.get('description', '')
        if test.get('folder'):
            description = f"Folder: {test['folder']}\n{description}"
        
        # Format test steps
        steps_text = "\nTest Steps:\n"
        for step in test_info.get('steps', []):
            action = html.unescape(step.get('action', ''))
            data = html.unescape(step.get('data', ''))
            result = html.unescape(step.get('result', ''))
            
            steps_text += f"\n{step.get('index', 1)}. {action}"
            if data:
                steps_text += f"\n   Data: {data}"
            if result:
                steps_text += f"\n   Expected: {result}"
            steps_text += "\n"
        
        return {
            "project_key": self.project_key,
            "summary": test_info['summary'],
            "issue_type": "Test",
            "description": description + steps_text,
            "labels": test_info['labels'],
            "priority": test_info.get('priority', 'Medium'),
            "additional_fields": {
                "customfield_10100": "Manual"  # Test Type field
            }
        }
    
    def prepare_precondition(self, precondition_text: str) -> Dict:
        """Prepare precondition for JIRA creation"""
        return {
            "project_key": self.project_key,
            "summary": f"Precondition: {precondition_text[:100]}...",
            "issue_type": "Precondition",
            "description": precondition_text
        }
    
    def get_upload_summary(self) -> Dict:
        """Get current upload statistics"""
        return {
            "phase": self.state["phase"],
            "statistics": self.state["statistics"],
            "failed_count": len(self.state["failed_tests"]),
            "total_uploaded": (self.state["statistics"]["api_tests_uploaded"] + 
                             self.state["statistics"]["functional_tests_uploaded"])
        }
    
    def record_upload_success(self, test_summary: str, jira_key: str, test_type: str):
        """Record successful test upload"""
        self.state["uploaded_tests"][test_summary] = jira_key
        
        if test_type == "api":
            self.state["statistics"]["api_tests_uploaded"] += 1
        else:
            self.state["statistics"]["functional_tests_uploaded"] += 1
        
        self._save_state()
    
    def record_upload_failure(self, test_summary: str, test_type: str, error: str):
        """Record failed test upload"""
        self.state["failed_tests"].append({
            "summary": test_summary,
            "type": test_type,
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
        self._save_state()
    
    def record_duplicate_skip(self, test_summary: str):
        """Record skipped duplicate"""
        self.state["statistics"]["duplicates_skipped"] += 1
        self._save_state()
    
    def check_if_exists(self, test_summary: str) -> Optional[str]:
        """Check if test already exists"""
        # Check in uploaded tests first
        if test_summary in self.state["uploaded_tests"]:
            return self.state["uploaded_tests"][test_summary]
        
        # Check in existing tests from discovery
        if test_summary in self.state["existing_tests"]:
            return self.state["existing_tests"][test_summary]
        
        return None
    
    def update_existing_tests(self, jira_results: List[Dict]):
        """Update existing tests from JIRA search results"""
        for issue in jira_results:
            summary = issue.get('fields', {}).get('summary', '')
            key = issue.get('key', '')
            if summary and key:
                self.state["existing_tests"][summary] = key
        self._save_state()
    
    def update_existing_preconditions(self, jira_results: List[Dict]):
        """Update existing preconditions from JIRA search results"""
        for issue in jira_results:
            summary = issue.get('fields', {}).get('summary', '')
            key = issue.get('key', '')
            if summary and key:
                self.state["existing_preconditions"][summary] = key
        self._save_state()

def main():
    """Main entry point - provides helper information"""
    print("""
MCP XRAY Uploader Helper Script
==============================

This script provides helper functions for uploading tests to XRAY using MCP JIRA tools.

Usage from Claude Code:
1. Initialize the uploader: uploader = MCPXrayUploader()
2. Use discovery JQL: queries = uploader.get_discovery_jql()
3. Prepare tests: test_data = uploader.prepare_test_for_upload(test, "api")
4. Record results: uploader.record_upload_success(summary, key, "api")

The script maintains state in: logs/mcp_upload_state.json
""")

if __name__ == "__main__":
    main()