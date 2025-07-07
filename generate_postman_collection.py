#!/usr/bin/env python3
"""
Generate Postman Collection 2.1 from Xray GraphQL schema
"""

import json
import re

def load_schema():
    """Load the introspection schema"""
    with open("xray_schema_only.json", "r") as f:
        return json.load(f)

def get_type_string(type_obj, is_input=False):
    """Convert GraphQL type to readable string"""
    if not type_obj:
        return "Unknown"
    
    kind = type_obj.get("kind")
    name = type_obj.get("name")
    
    if kind == "NON_NULL":
        inner = get_type_string(type_obj.get("ofType"), is_input)
        return f"{inner}!"
    elif kind == "LIST":
        inner = get_type_string(type_obj.get("ofType"), is_input)
        return f"[{inner}]"
    else:
        return name or "Unknown"

def get_example_value(type_obj, type_name=None):
    """Generate example value based on type"""
    if not type_obj:
        return None
        
    kind = type_obj.get("kind")
    name = type_obj.get("name", type_name)
    
    if kind == "NON_NULL":
        return get_example_value(type_obj.get("ofType"), type_name)
    elif kind == "LIST":
        inner = get_example_value(type_obj.get("ofType"), type_name)
        return [inner] if inner is not None else []
    elif kind == "SCALAR":
        if name == "String":
            # Provide context-aware examples
            if type_name:
                if "issueId" in type_name:
                    return "12345"
                elif "projectId" in type_name:
                    return "26420"
                elif "path" in type_name:
                    return "/"
                elif "name" in type_name:
                    return "Test Name"
                elif "key" in type_name:
                    return "MLBMOB-123"
                elif "jql" in type_name:
                    return "project = MLBMOB AND issuetype = Test"
                elif "status" in type_name:
                    return "PASS"
            return "string"
        elif name == "Int":
            return 100
        elif name == "Boolean":
            return True if "include" in str(type_name).lower() else False
        elif name == "Float":
            return 1.0
        elif name == "JSON":
            return {"key": "value"}
    elif kind == "ENUM":
        # Return first enum value or a common one
        return name  # Will be replaced with actual enum values later
    elif kind == "INPUT_OBJECT":
        return {}  # Will be filled with actual fields later
    
    return None

def generate_query_example(field, schema_types):
    """Generate a complete GraphQL query example"""
    args = field.get("args", [])
    field_name = field["name"]
    return_type = field.get("type")
    
    # Build arguments
    arg_definitions = []
    arg_uses = []
    variables = {}
    
    for arg in args:
        arg_name = arg["name"]
        arg_type = get_type_string(arg["type"])
        arg_definitions.append(f"${arg_name}: {arg_type}")
        arg_uses.append(f"{arg_name}: ${arg_name}")
        variables[arg_name] = get_example_value(arg["type"], arg_name)
    
    # Build query
    query_name = field_name.capitalize()
    args_str = f"({', '.join(arg_definitions)})" if arg_definitions else ""
    uses_str = f"({', '.join(arg_uses)})" if arg_uses else ""
    
    # Get return type fields
    return_fields = get_return_fields(return_type, schema_types, depth=0)
    
    query = f"""query {query_name}{args_str} {{
  {field_name}{uses_str} {return_fields}
}}"""
    
    return query, variables

def get_return_fields(type_obj, schema_types, depth=0, max_depth=3):
    """Get fields to request for a return type"""
    if depth > max_depth:
        return ""
    
    if not type_obj:
        return ""
    
    # Unwrap NON_NULL and LIST
    current_type = type_obj
    while current_type.get("kind") in ["NON_NULL", "LIST"]:
        current_type = current_type.get("ofType", {})
    
    type_name = current_type.get("name")
    if not type_name:
        return ""
    
    # Find the type definition
    type_def = next((t for t in schema_types if t["name"] == type_name), None)
    if not type_def or type_def.get("kind") != "OBJECT":
        return ""
    
    fields = type_def.get("fields", [])
    if not fields:
        return ""
    
    # Build field selection
    field_selections = []
    for field in fields[:20]:  # Limit fields to avoid huge queries
        field_name = field["name"]
        field_type = field.get("type", {})
        
        # Skip deprecated fields
        if field.get("isDeprecated"):
            continue
        
        # Get the actual type
        inner_type = field_type
        while inner_type.get("kind") in ["NON_NULL", "LIST"]:
            inner_type = inner_type.get("ofType", {})
        
        inner_type_name = inner_type.get("name")
        inner_kind = inner_type.get("kind")
        
        # For scalars and enums, just include the field
        if inner_kind in ["SCALAR", "ENUM"]:
            field_selections.append(field_name)
        # For objects, recurse if not too deep
        elif inner_kind == "OBJECT" and depth < max_depth:
            # Special handling for some fields
            if field_name == "jira":
                field_selections.append('jira(fields: ["summary", "description"])')
            elif field_name in ["tests", "testRuns", "testExecutions"]:
                field_selections.append(f"""{field_name}(limit: 10) {{
    total
    start
    limit
    results {{
      issueId
      key
    }}
  }}""")
            else:
                sub_fields = get_return_fields(inner_type, schema_types, depth + 1, max_depth)
                if sub_fields:
                    field_selections.append(f"{field_name} {sub_fields}")
    
    if not field_selections:
        return "{\n    __typename\n  }"
    
    return "{\n    " + "\n    ".join(field_selections) + "\n  }"

def generate_mutation_example(field, schema_types):
    """Generate a complete GraphQL mutation example"""
    args = field.get("args", [])
    field_name = field["name"]
    return_type = field.get("type")
    
    # Build arguments
    arg_definitions = []
    arg_uses = []
    variables = {}
    
    for arg in args:
        arg_name = arg["name"]
        arg_type_obj = arg["type"]
        arg_type = get_type_string(arg_type_obj)
        arg_definitions.append(f"${arg_name}: {arg_type}")
        arg_uses.append(f"{arg_name}: ${arg_name}")
        
        # Generate appropriate example based on the input type
        example_value = generate_input_example(arg_type_obj, arg_name, schema_types)
        if example_value is not None:
            variables[arg_name] = example_value
    
    # Build mutation
    mutation_name = field_name.capitalize()
    args_str = f"({', '.join(arg_definitions)})" if arg_definitions else ""
    uses_str = f"({', '.join(arg_uses)})" if arg_uses else ""
    
    # Get return type fields
    return_fields = get_return_fields(return_type, schema_types, depth=0)
    
    mutation = f"""mutation {mutation_name}{args_str} {{
  {field_name}{uses_str} {return_fields}
}}"""
    
    return mutation, variables

def generate_input_example(type_obj, field_name, schema_types):
    """Generate example for input types"""
    if not type_obj:
        return None
    
    kind = type_obj.get("kind")
    
    if kind == "NON_NULL":
        return generate_input_example(type_obj.get("ofType"), field_name, schema_types)
    elif kind == "LIST":
        inner = generate_input_example(type_obj.get("ofType"), field_name, schema_types)
        return [inner] if inner is not None else []
    elif kind == "SCALAR":
        return get_example_value(type_obj, field_name)
    elif kind == "INPUT_OBJECT":
        type_name = type_obj.get("name")
        # Find the input type definition
        input_type = next((t for t in schema_types if t["name"] == type_name), None)
        if input_type:
            result = {}
            for field in input_type.get("inputFields", []):
                field_example = generate_input_example(field["type"], field["name"], schema_types)
                if field_example is not None:
                    result[field["name"]] = field_example
            return result
    elif kind == "ENUM":
        # For specific enums, provide appropriate values
        type_name = type_obj.get("name")
        if type_name == "TestTypeKind":
            return "Steps"
        return type_name
    
    return None

def create_postman_collection(schema):
    """Create Postman collection from GraphQL schema"""
    types = schema.get("types", [])
    
    # Find Query and Mutation types
    query_type_name = schema.get("queryType", {}).get("name", "Query")
    mutation_type_name = schema.get("mutationType", {}).get("name", "Mutation")
    
    query_type = next((t for t in types if t["name"] == query_type_name), None)
    mutation_type = next((t for t in types if t["name"] == mutation_type_name), None)
    
    # Create collection structure
    collection = {
        "info": {
            "_postman_id": "xray-graphql-collection",
            "name": "Xray GraphQL API",
            "description": "Complete Xray GraphQL API collection with all queries and mutations",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "auth": {
            "type": "bearer",
            "bearer": [
                {
                    "key": "token",
                    "value": "{{xray_token}}",
                    "type": "string"
                }
            ]
        },
        "item": [],
        "variable": [
            {
                "key": "base_url",
                "value": "https://xray.cloud.getxray.app/api/v2",
                "type": "string"
            },
            {
                "key": "xray_token",
                "value": "",
                "type": "string"
            }
        ]
    }
    
    # Add authentication folder
    auth_folder = {
        "name": "0. Authentication",
        "item": [
            {
                "name": "Get JWT Token",
                "request": {
                    "auth": {
                        "type": "noauth"
                    },
                    "method": "POST",
                    "header": [
                        {
                            "key": "Content-Type",
                            "value": "application/json"
                        }
                    ],
                    "body": {
                        "mode": "raw",
                        "raw": json.dumps({
                            "client_id": "{{xray_client_id}}",
                            "client_secret": "{{xray_client_secret}}"
                        }, indent=2)
                    },
                    "url": {
                        "raw": "{{base_url}}/authenticate",
                        "host": ["{{base_url}}"],
                        "path": ["authenticate"]
                    }
                },
                "response": []
            }
        ]
    }
    collection["item"].append(auth_folder)
    
    # Process queries
    if query_type:
        query_folders = {}
        
        for field in query_type.get("fields", []):
            if field.get("isDeprecated"):
                continue
            
            field_name = field["name"]
            
            # Categorize queries
            if "folder" in field_name.lower():
                category = "Folders"
            elif "test" in field_name.lower() and "execution" not in field_name.lower() and "plan" not in field_name.lower() and "set" not in field_name.lower() and "run" not in field_name.lower():
                category = "Tests"
            elif "execution" in field_name.lower():
                category = "Test Executions"
            elif "plan" in field_name.lower():
                category = "Test Plans"
            elif "set" in field_name.lower():
                category = "Test Sets"
            elif "run" in field_name.lower():
                category = "Test Runs"
            elif "precondition" in field_name.lower():
                category = "Preconditions"
            elif "dataset" in field_name.lower():
                category = "Datasets"
            elif "status" in field_name.lower():
                category = "Statuses"
            else:
                category = "Other"
            
            folder_name = f"1. Queries - {category}"
            
            if folder_name not in query_folders:
                query_folders[folder_name] = {
                    "name": folder_name,
                    "item": []
                }
            
            # Generate query example
            query, variables = generate_query_example(field, types)
            
            request_item = {
                "name": field["name"],
                "request": {
                    "method": "POST",
                    "header": [],
                    "body": {
                        "mode": "graphql",
                        "graphql": {
                            "query": query,
                            "variables": json.dumps(variables, indent=2)
                        }
                    },
                    "url": {
                        "raw": "{{base_url}}/graphql",
                        "host": ["{{base_url}}"],
                        "path": ["graphql"]
                    },
                    "description": field.get("description", "")
                },
                "response": []
            }
            
            query_folders[folder_name]["item"].append(request_item)
        
        # Add query folders to collection
        for folder in sorted(query_folders.values(), key=lambda x: x["name"]):
            collection["item"].append(folder)
    
    # Process mutations
    if mutation_type:
        mutation_folders = {}
        
        for field in mutation_type.get("fields", []):
            if field.get("isDeprecated"):
                continue
            
            field_name = field["name"]
            
            # Categorize mutations
            if "folder" in field_name.lower():
                category = "Folders"
            elif "test" in field_name.lower() and "execution" not in field_name.lower() and "plan" not in field_name.lower() and "set" not in field_name.lower() and "run" not in field_name.lower():
                category = "Tests"
            elif "execution" in field_name.lower():
                category = "Test Executions"
            elif "plan" in field_name.lower():
                category = "Test Plans"
            elif "set" in field_name.lower():
                category = "Test Sets"
            elif "run" in field_name.lower():
                category = "Test Runs"
            elif "precondition" in field_name.lower():
                category = "Preconditions"
            elif "step" in field_name.lower():
                category = "Test Steps"
            else:
                category = "Other"
            
            folder_name = f"2. Mutations - {category}"
            
            if folder_name not in mutation_folders:
                mutation_folders[folder_name] = {
                    "name": folder_name,
                    "item": []
                }
            
            # Generate mutation example
            mutation, variables = generate_mutation_example(field, types)
            
            request_item = {
                "name": field["name"],
                "request": {
                    "method": "POST",
                    "header": [],
                    "body": {
                        "mode": "graphql",
                        "graphql": {
                            "query": mutation,
                            "variables": json.dumps(variables, indent=2)
                        }
                    },
                    "url": {
                        "raw": "{{base_url}}/graphql",
                        "host": ["{{base_url}}"],
                        "path": ["graphql"]
                    },
                    "description": field.get("description", "")
                },
                "response": []
            }
            
            mutation_folders[folder_name]["item"].append(request_item)
        
        # Add mutation folders to collection
        for folder in sorted(mutation_folders.values(), key=lambda x: x["name"]):
            collection["item"].append(folder)
    
    return collection

def main():
    """Main function"""
    print("Loading schema...")
    schema = load_schema()
    
    print("Generating Postman collection...")
    collection = create_postman_collection(schema)
    
    # Save collection
    with open("xray-postman-collection.json", "w") as f:
        json.dump(collection, f, indent=2)
    
    print("Postman collection saved to xray-postman-collection.json")

if __name__ == "__main__":
    main()