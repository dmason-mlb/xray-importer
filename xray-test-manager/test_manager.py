"""
XRAY Test Manager - Main Application Logic

This module provides high-level test management operations that combine
multiple GraphQL API calls to accomplish complex tasks like batch operations,
test organization, and label management.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed

from xray_client import XrayGraphQLClient, create_client_from_env

logger = logging.getLogger(__name__)

@dataclass
class TestSummary:
    """Simplified test information for UI display"""
    issue_id: str
    key: str
    summary: str
    labels: List[str]
    priority: str
    assignee: Optional[str]
    steps_count: int
    folder_path: Optional[str]
    last_modified: str
    has_steps: bool

@dataclass
class TestStep:
    """Test step information"""
    id: Optional[str]
    action: str
    data: str
    result: str
    attachments: List[Dict] = None

@dataclass
class BatchOperationResult:
    """Result of a batch operation"""
    successful: List[str]
    failed: List[Tuple[str, str]]  # (issue_id, error_message)
    total: int

class XrayTestManager:
    """High-level test management operations"""
    
    def __init__(self, client: XrayGraphQLClient = None):
        self.client = client or create_client_from_env()
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    def get_available_projects(self) -> List[Dict]:
        """Get list of available JIRA projects (mock implementation)"""
        # In a real implementation, this would call JIRA REST API
        # For now, return common MLB projects
        return [
            {"key": "MLB", "name": "MLB Mobile App"},
            {"key": "CALC", "name": "Calculator App"},
            {"key": "FRAMED", "name": "Framed App"},
            {"key": "BALLPARK", "name": "Ballpark App"}
        ]
    
    def fetch_tests_summary(self, project_key: str, limit: int = 100, start: int = 0,
                           filters: Optional[Dict] = None) -> List[TestSummary]:
        """
        Fetch test summaries with optional filtering
        
        Args:
            project_key: JIRA project key
            limit: Maximum number of tests to return
            start: Starting offset for pagination
            filters: Optional filters (labels, folder_path, has_steps, etc.)
        """
        jql = self._build_jql_from_filters(project_key, filters)
        
        try:
            result = self.client.get_tests(project_key, limit, start, jql)
            tests = result.get("getTests", {}).get("results", [])
            
            summaries = []
            for test in tests:
                jira_data = test.get("jira", {})
                steps = test.get("steps", [])
                
                summary = TestSummary(
                    issue_id=test.get("issueId", ""),
                    key=jira_data.get("key", ""),
                    summary=jira_data.get("summary", ""),
                    labels=jira_data.get("labels", []),
                    priority=jira_data.get("priority", {}).get("name", ""),
                    assignee=jira_data.get("assignee", {}).get("displayName") if jira_data.get("assignee") else None,
                    steps_count=len(steps),
                    folder_path=test.get("folder", {}).get("path") if test.get("folder") else None,
                    last_modified=test.get("lastModified", ""),
                    has_steps=len(steps) > 0
                )
                summaries.append(summary)
            
            return summaries
            
        except Exception as e:
            logger.error(f"Failed to fetch tests: {e}")
            raise
    
    def _build_jql_from_filters(self, project_key: str, filters: Optional[Dict]) -> str:
        """Build JQL query from filter parameters"""
        jql_parts = [f'project = "{project_key}"', 'issuetype = "Test"']
        
        if not filters:
            return " AND ".join(jql_parts)
        
        # Label filters
        if "labels" in filters and filters["labels"]:
            label_conditions = [f'labels = "{label}"' for label in filters["labels"]]
            jql_parts.append(f'({" OR ".join(label_conditions)})')
        
        # Priority filter
        if "priority" in filters and filters["priority"]:
            jql_parts.append(f'priority = "{filters["priority"]}"')
        
        # Assignee filter
        if "assignee" in filters and filters["assignee"]:
            jql_parts.append(f'assignee = "{filters["assignee"]}"')
        
        # Modified since filter
        if "modified_since" in filters and filters["modified_since"]:
            jql_parts.append(f'updated >= "{filters["modified_since"]}"')
        
        # Custom JQL
        if "custom_jql" in filters and filters["custom_jql"]:
            jql_parts.append(f'({filters["custom_jql"]})')
        
        return " AND ".join(jql_parts)
    
    def get_tests_without_steps(self, project_key: str, limit: int = 100, start: int = 0) -> List[TestSummary]:
        """Get tests that don't have any test steps defined"""
        try:
            result = self.client.get_tests_without_steps(project_key, limit, start)
            tests = result.get("getTests", {}).get("results", [])
            
            summaries = []
            for test in tests:
                jira_data = test.get("jira", {})
                
                summary = TestSummary(
                    issue_id=test.get("issueId", ""),
                    key=jira_data.get("key", ""),
                    summary=jira_data.get("summary", ""),
                    labels=jira_data.get("labels", []),
                    priority=jira_data.get("priority", {}).get("name", ""),
                    assignee=jira_data.get("assignee", {}).get("displayName") if jira_data.get("assignee") else None,
                    steps_count=0,
                    folder_path=test.get("folder", {}).get("path") if test.get("folder") else None,
                    last_modified=test.get("lastModified", ""),
                    has_steps=False
                )
                summaries.append(summary)
            
            return summaries
            
        except Exception as e:
            logger.error(f"Failed to fetch tests without steps: {e}")
            raise
    
    def get_test_details(self, issue_id: str) -> Dict:
        """Get detailed test information including steps"""
        try:
            result = self.client.get_test_details(issue_id)
            return result.get("getTest", {})
            
        except Exception as e:
            logger.error(f"Failed to fetch test details for {issue_id}: {e}")
            raise
    
    def search_tests_by_keywords(self, project_key: str, keywords: str, limit: int = 100) -> List[TestSummary]:
        """Search tests by keywords in summary or description"""
        # Build JQL for text search
        jql = f'project = "{project_key}" AND issuetype = "Test" AND (summary ~ "{keywords}" OR description ~ "{keywords}")'
        
        try:
            result = self.client.get_tests(project_key, limit, 0, jql)
            tests = result.get("getTests", {}).get("results", [])
            
            summaries = []
            for test in tests:
                jira_data = test.get("jira", {})
                steps = test.get("steps", [])
                
                summary = TestSummary(
                    issue_id=test.get("issueId", ""),
                    key=jira_data.get("key", ""),
                    summary=jira_data.get("summary", ""),
                    labels=jira_data.get("labels", []),
                    priority=jira_data.get("priority", {}).get("name", ""),
                    assignee=jira_data.get("assignee", {}).get("displayName") if jira_data.get("assignee") else None,
                    steps_count=len(steps),
                    folder_path=test.get("folder", {}).get("path") if test.get("folder") else None,
                    last_modified=test.get("lastModified", ""),
                    has_steps=len(steps) > 0
                )
                summaries.append(summary)
            
            return summaries
            
        except Exception as e:
            logger.error(f"Failed to search tests: {e}")
            raise
    
    def add_test_steps(self, issue_id: str, steps: List[TestStep]) -> BatchOperationResult:
        """Add multiple test steps to a test"""
        successful = []
        failed = []
        
        for step in steps:
            try:
                result = self.client.add_test_step(
                    issue_id=issue_id,
                    action=step.action,
                    data=step.data,
                    result=step.result
                )
                
                if result.get("addTestStep", {}).get("step"):
                    successful.append(step.action)
                else:
                    failed.append((step.action, "Failed to add step"))
                    
            except Exception as e:
                failed.append((step.action, str(e)))
        
        return BatchOperationResult(
            successful=successful,
            failed=failed,
            total=len(steps)
        )
    
    def update_test_steps(self, issue_id: str, steps: List[TestStep]) -> BatchOperationResult:
        """Update multiple test steps"""
        successful = []
        failed = []
        
        for step in steps:
            if not step.id:
                failed.append((step.action, "Missing step ID"))
                continue
                
            try:
                result = self.client.update_test_step(
                    issue_id=issue_id,
                    step_id=step.id,
                    action=step.action,
                    data=step.data,
                    result=step.result
                )
                
                if result.get("updateTestStep", {}).get("step"):
                    successful.append(step.id)
                else:
                    failed.append((step.id, "Failed to update step"))
                    
            except Exception as e:
                failed.append((step.id, str(e)))
        
        return BatchOperationResult(
            successful=successful,
            failed=failed,
            total=len(steps)
        )
    
    def batch_add_labels(self, issue_ids: List[str], labels: List[str]) -> BatchOperationResult:
        """Add labels to multiple tests (requires JIRA REST API)"""
        # This would need to be implemented using JIRA REST API
        # since GraphQL doesn't support label operations directly
        successful = []
        failed = []
        
        logger.warning("Batch label operations require JIRA REST API implementation")
        
        return BatchOperationResult(
            successful=successful,
            failed=failed,
            total=len(issue_ids)
        )
    
    def batch_remove_labels(self, issue_ids: List[str], labels: List[str]) -> BatchOperationResult:
        """Remove labels from multiple tests (requires JIRA REST API)"""
        # This would need to be implemented using JIRA REST API
        successful = []
        failed = []
        
        logger.warning("Batch label operations require JIRA REST API implementation")
        
        return BatchOperationResult(
            successful=successful,
            failed=failed,
            total=len(issue_ids)
        )
    
    def batch_move_to_folder(self, project_key: str, issue_ids: List[str], folder_path: str) -> BatchOperationResult:
        """Move multiple tests to a folder"""
        try:
            result = self.client.add_tests_to_folder(project_key, folder_path, issue_ids)
            
            if result.get("addTestsToFolder", {}).get("folder"):
                return BatchOperationResult(
                    successful=issue_ids,
                    failed=[],
                    total=len(issue_ids)
                )
            else:
                return BatchOperationResult(
                    successful=[],
                    failed=[(id, "Failed to move to folder") for id in issue_ids],
                    total=len(issue_ids)
                )
                
        except Exception as e:
            logger.error(f"Failed to move tests to folder: {e}")
            return BatchOperationResult(
                successful=[],
                failed=[(id, str(e)) for id in issue_ids],
                total=len(issue_ids)
            )
    
    def get_all_labels(self, project_key: str) -> List[str]:
        """Get all unique labels from tests in a project"""
        try:
            # Fetch all tests to get labels
            result = self.client.get_tests(project_key, limit=100)
            tests = result.get("getTests", {}).get("results", [])
            
            all_labels = set()
            for test in tests:
                jira_data = test.get("jira", {})
                labels = jira_data.get("labels", [])
                all_labels.update(labels)
            
            return sorted(list(all_labels))
            
        except Exception as e:
            logger.error(f"Failed to get labels: {e}")
            return []
    
    def get_folder_structure(self, project_key: str, folder_path: str = "/") -> Dict:
        """Get folder structure for a project"""
        try:
            result = self.client.get_folder_structure(project_key, folder_path)
            return result.get("getFolder", {})
            
        except Exception as e:
            logger.error(f"Failed to get folder structure: {e}")
            return {}
    
    def export_tests_to_json(self, project_key: str, output_file: str, filters: Optional[Dict] = None) -> int:
        """Export tests to JSON file"""
        try:
            tests = self.fetch_tests_summary(project_key, limit=1000, filters=filters)
            
            # Convert to dictionaries for JSON serialization
            test_data = [asdict(test) for test in tests]
            
            export_data = {
                "project_key": project_key,
                "export_date": datetime.now().isoformat(),
                "total_tests": len(test_data),
                "filters": filters or {},
                "tests": test_data
            }
            
            with open(output_file, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"Exported {len(test_data)} tests to {output_file}")
            return len(test_data)
            
        except Exception as e:
            logger.error(f"Failed to export tests: {e}")
            raise

# Example usage and testing
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    # Create test manager
    manager = XrayTestManager()
    
    try:
        # Example: Get tests without steps
        print("=== Tests without steps ===")
        tests_without_steps = manager.get_tests_without_steps("MLB", limit=5)
        for test in tests_without_steps:
            print(f"- {test.key}: {test.summary}")
        
        # Example: Search tests by keywords
        print("\n=== Search tests by keywords ===")
        search_results = manager.search_tests_by_keywords("MLB", "login", limit=5)
        for test in search_results:
            print(f"- {test.key}: {test.summary}")
        
        # Example: Get all labels
        print("\n=== Project labels ===")
        labels = manager.get_all_labels("MLB")
        print(f"Found {len(labels)} labels: {labels[:10]}...")  # Show first 10
        
    except Exception as e:
        print(f"Error: {e}")