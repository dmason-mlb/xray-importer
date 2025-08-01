#!/usr/bin/env python3
"""
Create FRAMED folder in Xray Test Repository
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir / 'xray-api'))
from auth_utils import XrayAPIClient

def create_framed_folder():
    client = XrayAPIClient()
    
    print("=== CREATING FRAMED FOLDER IN TEST REPOSITORY ===")
    
    # GraphQL mutation to create a folder
    mutation = """
    mutation CreateFolder($projectId: String!, $folderPath: String!) {
        createTestRepositoryFolder(projectId: $projectId, folderPath: $folderPath) {
            folder {
                path
                name
            }
            warning
        }
    }
    """
    
    variables = {
        "projectId": "FRAMED",
        "folderPath": "/FRAMED"
    }
    
    try:
        result = client.execute_graphql_query(mutation, variables)
        
        if result and 'createTestRepositoryFolder' in result:
            folder_data = result['createTestRepositoryFolder']
            if folder_data.get('folder'):
                folder = folder_data['folder']
                print(f"✓ Successfully created folder: {folder['path']}")
                print(f"  Name: {folder['name']}")
            else:
                print(f"✗ Failed to create folder")
            
            if folder_data.get('warning'):
                print(f"  Warning: {folder_data['warning']}")
        else:
            print(f"✗ No result from mutation")
            
    except Exception as e:
        print(f"✗ Error creating folder: {e}")
        
        # Try alternative mutation format
        print("\n=== TRYING ALTERNATIVE MUTATION FORMAT ===")
        
        mutation2 = """
        mutation CreateFolder($folderName: String!, $projectKey: String!) {
            createTestRepositoryFolder(name: $folderName, projectKey: $projectKey) {
                path
                name
            }
        }
        """
        
        variables2 = {
            "folderName": "FRAMED",
            "projectKey": "FRAMED"
        }
        
        try:
            result2 = client.execute_graphql_query(mutation2, variables2)
            print(f"Alternative result: {result2}")
        except Exception as e2:
            print(f"Alternative also failed: {e2}")

if __name__ == "__main__":
    create_framed_folder()