#!/usr/bin/env python3
"""
Test Xray folder operations to determine correct API usage.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "xray-api"))

from auth_utils import XrayAPIClient

def test_introspection():
    """Test GraphQL introspection to discover schema."""
    client = XrayAPIClient()
    
    # Get auth token
    token = client.get_auth_token()
    print("✓ Authentication successful")
    
    # Introspection query for folder operations
    query = """
    query IntrospectFolderOperations {
        __type(name: "Mutation") {
            fields {
                name
                description
                args {
                    name
                    type {
                        name
                        kind
                        ofType {
                            name
                            kind
                        }
                    }
                }
            }
        }
    }
    """
    
    try:
        response = client.execute_graphql_query(query, {})
        if response and '__type' in response:
            mutations = response['__type']['fields']
            folder_mutations = [m for m in mutations if 'folder' in m['name'].lower()]
            
            print("\nFolder-related mutations found:")
            for mutation in folder_mutations:
                print(f"\n{mutation['name']}:")
                if mutation.get('description'):
                    print(f"  Description: {mutation['description']}")
                print("  Arguments:")
                for arg in mutation.get('args', []):
                    arg_type = arg['type']
                    type_name = arg_type.get('name') or arg_type.get('ofType', {}).get('name', 'Unknown')
                    print(f"    - {arg['name']}: {type_name}")
        else:
            print("Failed to get introspection data")
    except Exception as e:
        print(f"Introspection error: {e}")

def test_get_folders():
    """Test getting existing folders."""
    client = XrayAPIClient()
    token = client.get_auth_token()
    
    # Try different queries
    queries = [
        {
            "name": "getFolders",
            "query": """
            query GetFolders($projectId: String!) {
                getFolders(projectId: $projectId) {
                    folders {
                        id
                        name
                        path
                    }
                }
            }
            """
        },
        {
            "name": "getTestRepository", 
            "query": """
            query GetTestRepository($projectKey: String!) {
                getTestRepository(projectKey: $projectKey) {
                    folders {
                        id
                        name
                        path
                    }
                }
            }
            """
        }
    ]
    
    print("\n\nTesting folder queries:")
    for q in queries:
        print(f"\nTrying {q['name']}...")
        try:
            # Try with project key
            response = client.execute_graphql_query(q['query'], {"projectKey": "FRAMED", "projectId": "FRAMED"})
            if response:
                print(f"✓ {q['name']} succeeded")
                print(f"Response: {response}")
            else:
                print(f"✗ {q['name']} returned empty response")
        except Exception as e:
            print(f"✗ {q['name']} failed: {e}")

def test_create_folder():
    """Test creating a folder with different parameter combinations."""
    client = XrayAPIClient()
    token = client.get_auth_token()
    
    # Different parameter combinations to try
    mutations = [
        {
            "name": "createFolder with path",
            "query": """
            mutation CreateFolder($path: String!, $projectId: String!) {
                createFolder(path: $path, projectId: $projectId) {
                    folder {
                        id
                        name
                        path
                    }
                }
            }
            """,
            "variables": {"path": "/Test Folder", "projectId": "FRAMED"}
        },
        {
            "name": "createFolder with projectKey and name",
            "query": """
            mutation CreateFolder($projectKey: String!, $name: String!) {
                createFolder(projectKey: $projectKey, name: $name) {
                    folder {
                        id
                        name  
                        path
                    }
                }
            }
            """,
            "variables": {"projectKey": "FRAMED", "name": "Test Folder"}
        }
    ]
    
    print("\n\nTesting folder creation mutations:")
    for m in mutations:
        print(f"\nTrying {m['name']}...")
        try:
            response = client.execute_graphql_query(m['query'], m['variables'])
            if response:
                print(f"✓ {m['name']} succeeded")
                print(f"Response: {response}")
            else:
                print(f"✗ {m['name']} returned empty response")
        except Exception as e:
            print(f"✗ {m['name']} failed: {e}")

def main():
    """Main execution."""
    print("Testing Xray Folder Operations")
    print("=" * 50)
    
    # Test introspection first
    test_introspection()
    
    # Test getting folders
    test_get_folders()
    
    # Test creating folders
    test_create_folder()

if __name__ == "__main__":
    main()