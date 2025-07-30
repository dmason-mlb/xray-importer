#!/usr/bin/env python3
"""
Xray Authentication and GraphQL Utilities
For Xray Remediation Project - July 17, 2025
"""

import os
import requests
import json
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path(__file__).parent.parent / 'logs' / 'auth_utils.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Xray API Configuration
XRAY_BASE_URL = "https://xray.cloud.getxray.app/api/v1"
XRAY_GRAPHQL_URL = "https://xray.cloud.getxray.app/api/v2/graphql"

class XrayAPIClient:
    """Xray API Client with authentication and GraphQL support"""
    
    def __init__(self, client_id=None, client_secret=None):
        self.client_id = client_id or os.environ.get('XRAY_CLIENT_ID')
        self.client_secret = client_secret or os.environ.get('XRAY_CLIENT_SECRET')
        
        if not self.client_id or not self.client_secret:
            raise ValueError("XRAY_CLIENT_ID and XRAY_CLIENT_SECRET must be provided")
        
        self.token = None
        self.token_expires = None
        
    def get_auth_token(self):
        """Get authentication token from Xray API"""
        if self.token and self.token_expires and datetime.now() < self.token_expires:
            return self.token
            
        auth_url = f"{XRAY_BASE_URL}/authenticate"
        auth_data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        try:
            response = requests.post(auth_url, json=auth_data)
            response.raise_for_status()
            
            # Token is returned as plain text
            self.token = response.text.strip('"')
            # Tokens typically expire in 1 hour, we'll refresh after 50 minutes
            from datetime import timedelta
            self.token_expires = datetime.now() + timedelta(minutes=50)
            
            logger.info("Successfully obtained Xray authentication token")
            return self.token
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to authenticate with Xray API: {e}")
            raise
    
    def execute_graphql_query(self, query, variables=None):
        """Execute GraphQL query against Xray API"""
        token = self.get_auth_token()
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "query": query,
            "variables": variables or {}
        }
        
        # Debug logging
        logger.debug(f"GraphQL request payload: {json.dumps(payload, indent=2)}")
        
        try:
            response = requests.post(XRAY_GRAPHQL_URL, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            if "errors" in result:
                logger.error(f"GraphQL errors: {result['errors']}")
                raise Exception(f"GraphQL errors: {result['errors']}")
            
            return result.get("data")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"GraphQL request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response body: {e.response.text}")
            raise
    
    def backup_current_state(self, project_key="FRAMED"):
        """Create backup of current project state"""
        backup_dir = Path(__file__).parent.parent / 'backups'
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"{project_key}_backup_{timestamp}.json"
        
        # Query to get all tests and preconditions
        query = """
        query GetProjectData($projectKey: String!) {
            getTests(jql: "project = $projectKey", limit: 1000) {
                total
                results {
                    issueId
                    summary
                    testType
                    labels
                    preconditions {
                        issueId
                        summary
                    }
                    folder {
                        name
                        path
                    }
                }
            }
            getPreconditions(jql: "project = $projectKey", limit: 1000) {
                total
                results {
                    issueId
                    summary
                    definition
                }
            }
        }
        """
        
        try:
            result = self.execute_graphql_query(query, {"projectKey": project_key})
            
            with open(backup_file, 'w') as f:
                json.dump(result, f, indent=2)
            
            logger.info(f"Backup created: {backup_file}")
            return backup_file
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            raise

def log_operation(operation_name, details):
    """Log operation details to audit trail"""
    log_dir = Path(__file__).parent.parent / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    audit_file = log_dir / 'audit_trail.log'
    
    timestamp = datetime.now().isoformat()
    log_entry = {
        "timestamp": timestamp,
        "operation": operation_name,
        "details": details
    }
    
    with open(audit_file, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')
    
    logger.info(f"Operation logged: {operation_name}")

if __name__ == "__main__":
    # Test authentication
    try:
        client = XrayAPIClient()
        token = client.get_auth_token()
        print(f"✅ Authentication successful")
        
        # Test simple query
        test_query = """
        query {
            getTests(jql: "project = FRAMED", limit: 1) {
                total
            }
        }
        """
        
        result = client.execute_graphql_query(test_query)
        print(f"✅ GraphQL connection successful - Found {result['getTests']['total']} tests in FRAMED project")
        
    except Exception as e:
        print(f"❌ Error: {e}")