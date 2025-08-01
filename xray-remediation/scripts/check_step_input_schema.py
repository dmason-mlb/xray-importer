#!/usr/bin/env python3
"""
Check GraphQL schema for CreateStepInput
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir / 'xray-api'))
from auth_utils import XrayAPIClient

def check_schema():
    client = XrayAPIClient()
    
    # Query to introspect CreateStepInput
    query = """
    query IntrospectStepInput {
        __type(name: "CreateStepInput") {
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
    
    try:
        result = client.execute_graphql_query(query, {})
        
        if result and '__type' in result and result['__type']:
            print("=== CreateStepInput Fields ===")
            for field in result['__type']['inputFields']:
                field_type = field['type']
                type_name = field_type.get('name') or (field_type['ofType']['name'] if field_type.get('ofType') else 'Unknown')
                kind = field_type.get('kind', '')
                required = '!' if kind == 'NON_NULL' else ''
                print(f"- {field['name']}: {type_name}{required}")
        else:
            print("CreateStepInput type not found")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_schema()