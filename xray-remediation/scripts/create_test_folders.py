#!/usr/bin/env python3
"""
Create test folders in Xray Test Repository
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir / 'xray-api'))
from auth_utils import XrayAPIClient

def create_test_folders():
    client = XrayAPIClient()
    
    # First, let's check what folders exist
    query = """
    query GetFolders($projectId: String!, $folderPath: String) {
        getTestRepositoryFolders(projectId: $projectId, folderPath: $folderPath) {
            path
            name
            testsCount
            folders {
                path
                name
                testsCount
            }
        }
    }
    """
    
    # Need project key
    variables = {
        "projectId": "FRAMED",
        "folderPath": "/"
    }
    
    try:
        result = client.execute_graphql_query(query, variables)
        
        if result and 'getTestRepositoryFolders' in result:
            root_folder = result['getTestRepositoryFolders']
            folders = root_folder.get('folders', [])
            
            print("=== EXISTING TEST REPOSITORY FOLDERS ===")
            print(f"Total folders found: {len(folders)}")
            
            for folder in folders:
                print(f"\nPath: {folder['path']}")
                print(f"  Name: {folder['name']}")
                print(f"  Tests: {folder['testsCount']}")
            
            # Check if /FRAMED exists
            framed_exists = any(f['path'] == '/FRAMED' for f in folders)
            
            if not framed_exists:
                print("\n=== CREATING /FRAMED FOLDER ===")
                create_folder(client, "FRAMED", "/")
            else:
                print("\n✓ /FRAMED folder already exists")
                
    except Exception as e:
        print(f"Error: {e}")

def create_folder(client, folder_name, parent_path):
    """Create a folder in the test repository"""
    mutation = """
    mutation CreateTestRepositoryFolder($folderName: String!, $parentPath: String!) {
        createTestRepositoryFolder(folderName: $folderName, parentPath: $parentPath) {
            folder {
                path
                name
            }
            warning
        }
    }
    """
    
    variables = {
        "folderName": folder_name,
        "parentPath": parent_path
    }
    
    try:
        result = client.execute_graphql_query(mutation, variables)
        
        if result and 'createTestRepositoryFolder' in result:
            folder_data = result['createTestRepositoryFolder']
            if folder_data.get('folder'):
                folder = folder_data['folder']
                print(f"✓ Created folder: {folder['path']}")
                if folder_data.get('warning'):
                    print(f"  Warning: {folder_data['warning']}")
            else:
                print(f"✗ Failed to create folder")
                if folder_data.get('warning'):
                    print(f"  Warning: {folder_data['warning']}")
        else:
            print(f"✗ No result from mutation")
            
    except Exception as e:
        print(f"✗ Error creating folder: {e}")

if __name__ == "__main__":
    create_test_folders()