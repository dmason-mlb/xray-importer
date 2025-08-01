#!/usr/bin/env python3
"""
Check GraphQL schema for creating tests
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir / 'xray-api'))
from auth_utils import XrayAPIClient

def check_schema():
    client = XrayAPIClient()
    
    # Query to introspect the createTest mutation
    query = """
    query IntrospectCreateTest {
        __type(name: "Mutation") {
            fields {
                name
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
        result = client.execute_graphql_query(query, {})
        
        # Find createTest mutation
        if result and '__type' in result:
            mutations = result['__type']['fields']
            create_test = next((m for m in mutations if m['name'] == 'createTest'), None)
            
            if create_test:
                print("=== createTest Mutation Arguments ===")
                for arg in create_test['args']:
                    arg_type = arg['type']
                    type_name = arg_type.get('name') or (arg_type['ofType']['name'] if arg_type.get('ofType') else 'Unknown')
                    print(f"- {arg['name']}: {type_name}")
            else:
                print("createTest mutation not found")
                
        # Also check for test type enums
        test_type_query = """
        query GetTestTypes {
            __type(name: "UpdateTestTypeInput") {
                inputFields {
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
        """
        
        result2 = client.execute_graphql_query(test_type_query, {})
        if result2 and '__type' in result2 and result2['__type']:
            print("\n=== UpdateTestTypeInput Fields ===")
            for field in result2['__type']['inputFields']:
                field_type = field['type']
                type_name = field_type.get('name') or (field_type['ofType']['name'] if field_type.get('ofType') else 'Unknown')
                print(f"- {field['name']}: {type_name}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_schema()