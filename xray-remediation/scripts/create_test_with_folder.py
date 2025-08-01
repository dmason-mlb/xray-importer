#!/usr/bin/env python3
"""
Create a test in /FRAMED folder to force folder creation
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir / 'xray-api'))
from auth_utils import XrayAPIClient

def create_test_with_folder():
    client = XrayAPIClient()
    
    print("=== CREATING TEST IN /FRAMED FOLDER ===")
    print("This should implicitly create the folder if it doesn't exist")
    
    # GraphQL mutation to create a test with folder path
    mutation = """
    mutation CreateTest($testType: UpdateTestTypeInput!, $jira: JSON!, $folderPath: String) {
        createTest(testType: $testType, jira: $jira, folderPath: $folderPath) {
            test {
                issueId
                jira(fields: ["key", "summary"])
                folder {
                    path
                    name
                }
            }
            warnings
        }
    }
    """
    
    # Prepare test data
    jira_fields = {
        "fields": {
            "project": {
                "key": "FRAMED"
            },
            "summary": "Folder Creation Test - DELETE ME",
            "labels": ["test_folder_creation", "delete_me"]
        }
    }
    
    variables = {
        "testType": {
            "name": "Manual"
        },
        "jira": jira_fields,
        "folderPath": "/FRAMED"
    }
    
    try:
        result = client.execute_graphql_query(mutation, variables)
        
        if result and 'createTest' in result:
            test_data = result['createTest']['test']
            jira_data = test_data.get('jira', {})
            test_key = jira_data.get('key', 'Unknown')
            folder_data = test_data.get('folder', {})
            
            print(f"\n✓ Successfully created test: {test_key}")
            print(f"  Summary: {jira_data.get('summary')}")
            print(f"  Issue ID: {test_data['issueId']}")
            
            if folder_data:
                print(f"\n✓ Folder information:")
                print(f"  Path: {folder_data.get('path')}")
                print(f"  Name: {folder_data.get('name')}")
                print(f"\nThe /FRAMED folder should now exist!")
            else:
                print(f"\n⚠ No folder information returned")
            
            if result['createTest'].get('warnings'):
                print(f"\nWarnings: {result['createTest']['warnings']}")
                
            return test_data['issueId']
            
        else:
            print(f"✗ Failed to create test")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return None

if __name__ == "__main__":
    test_id = create_test_with_folder()
    if test_id:
        print(f"\nCreated test with ID: {test_id}")
        print("You can now run the folder organization script again.")