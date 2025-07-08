#!/usr/bin/env python3
"""
Fix required field markers (!) in XRAY GraphQL Postman collection
based on GraphQL schema requirements.
"""

import json
import re
import os

def fix_required_fields(query_string):
    """
    Fix required field markers based on XRAY GraphQL schema requirements.
    """
    
    # Fix known incorrect parameter names
    param_fixes = {
        'addPreconditionsToTest': {
            'preconditionIds': 'preconditionIssueIds'
        }
    }
    
    # Apply parameter name fixes
    for operation, fixes in param_fixes.items():
        if operation in query_string:
            for old_param, new_param in fixes.items():
                # Fix parameter definitions
                query_string = query_string.replace(f'${old_param}:', f'${new_param}:')
                # Fix parameter usage in the mutation/query body
                # Only replace if it's a standalone parameter (not part of another word)
                query_string = re.sub(rf'\b{old_param}\b(?=\s*[,\)])', new_param, query_string)
    
    # Known required fields based on XRAY GraphQL schema
    # Note: getTests does NOT require jql - it's optional
    required_fields = {
        # Mutations
        'createFolder': ['path'],  # projectId is optional when not in test plan
        'createTest': ['jira'],
        'createTestSet': ['jira'],
        'addTestsToTestSet': ['issueId', 'testIssueIds'],
        'addTestsToFolder': ['path', 'projectId', 'issueIds'],
        'updateTestFolder': ['issueId', 'projectId', 'folderPath'],
        'addTestStep': ['issueId', 'action', 'result'],  # data is optional
        'updateTestStep': ['issueId', 'stepId', 'action', 'result'],  # data is optional
        'removeTestStep': ['issueId', 'stepId'],
        'createTestExecution': ['jira'],
        'createTestPlan': ['jira'],
        'addPreconditionsToTest': ['issueId', 'preconditionIssueIds'],
        'addTestEnvironmentsToTestExecution': ['issueId', 'testEnvironments'],
        'addTestExecutionsToTest': ['issueId', 'testExecIssueIds'],
        'addTestExecutionsToTestPlan': ['issueId', 'testExecIssueIds'],
        'addTestPlansToTest': ['issueId', 'testPlanIssueIds'],
        'addTestsToTestExecution': ['issueId', 'testIssueIds'],
        'addTestsToTestPlan': ['issueId', 'testIssueIds'],
        'addTestSetsToTest': ['issueId', 'testSetIssueIds'],
        'addDefectsToTestRun': ['id', 'issues'],
        'addDefectsToTestRunStep': ['testRunId', 'stepId'],
        'addEvidenceToTestRun': ['id', 'evidence'],
        'addEvidenceToTestRunStep': ['testRunId', 'stepId'],
        'addIssuesToFolder': ['projectId', 'path', 'issueIds'],
        'updateTest': ['issueId'],  # jira is optional for updates
        
        # Queries - based on actual GraphQL schema
        'getTest': ['issueId'],
        'getTests': [],  # ALL params optional: jql, limit, start
        'getTestSets': [],  # ALL params optional
        'getTestSet': ['issueId'],
        'getFolder': ['projectId', 'path'],
        'getFolders': ['projectId'],
        'getCoverableIssue': ['issueId'],
        'getCoverableIssues': ['limit'],  # issueIds and jql are optional
        'getDataset': ['testIssueId'],
        'getExpandedTest': ['issueId'],
        'getExpandedTests': ['limit'],
        'getTestExecution': ['issueId'],
        'getTestExecutions': ['limit'],
        'getTestPlan': ['issueId'],
        'getTestPlans': ['limit'],
        'getTestRun': ['id'],
        'getTestRuns': ['limit'],
        'getPrecondition': ['issueId'],
        'getPreconditions': ['limit'],
    }
    
    # Extract operation name from the query body (not the operation definition)
    body_match = re.search(r'\)\s*\{\s*(\w+)\s*\(', query_string)
    if not body_match:
        return query_string
        
    graphql_operation = body_match.group(1)
    
    # Get required fields for this operation
    required = required_fields.get(graphql_operation, [])
    
    # Extract operation definition
    operation_match = re.search(r'^(query|mutation)\s+\w+\s*\([^)]*\)', query_string, re.MULTILINE | re.DOTALL)
    if not operation_match:
        return query_string
        
    operation_def = operation_match.group(0)
    
    # Parse parameters
    params_match = re.search(r'\((.*)\)', operation_def, re.DOTALL)
    if not params_match:
        return query_string
        
    params_str = params_match.group(1)
    
    # Parse each parameter
    new_params = []
    param_pattern = r'\$(\w+):\s*([^,\n$]+)'
    
    for match in re.finditer(param_pattern, params_str):
        var_name = match.group(1)
        var_type = match.group(2).strip()
        
        # Remove any existing ! marks
        clean_type = var_type.replace('!', '')
        
        # Add ! only if this parameter is required
        if var_name in required:
            if clean_type.endswith(']'):
                # For array types, put ! before the closing bracket
                clean_type = clean_type[:-1] + '!]'
            else:
                clean_type += '!'
        
        new_params.append(f'${var_name}: {clean_type}')
    
    # Reconstruct the operation definition
    operation_type = 'query' if operation_def.startswith('query') else 'mutation'
    operation_name = re.search(r'(query|mutation)\s+(\w+)', operation_def).group(2)
    
    if new_params:
        new_operation_def = f'{operation_type} {operation_name}(\n  ' + ',\n  '.join(new_params) + '\n)'
    else:
        new_operation_def = f'{operation_type} {operation_name}()'
    
    # Replace the old definition with the new one
    fixed_query = query_string.replace(operation_def, new_operation_def)
    
    return fixed_query

def fix_postman_collection(file_path):
    """
    Fix all GraphQL queries and mutations in the Postman collection.
    """
    
    # Read the collection
    with open(file_path, 'r') as f:
        collection = json.load(f)
    
    fixed_count = 0
    
    # Process all items recursively
    def process_item(item):
        nonlocal fixed_count
        
        if 'request' in item and 'body' in item['request']:
            body = item['request']['body']
            if body.get('mode') == 'graphql' and 'graphql' in body:
                graphql = body['graphql']
                if 'query' in graphql:
                    original_query = graphql['query']
                    fixed_query = fix_required_fields(original_query)
                    
                    if original_query != fixed_query:
                        graphql['query'] = fixed_query
                        fixed_count += 1
                        print(f"Fixed: {item.get('name', 'Unknown')}")
                        # Show what changed
                        print(f"  Original params: {re.search(r'\\(([^)]+)\\)', original_query, re.DOTALL).group(1) if re.search(r'\\(([^)]+)\\)', original_query, re.DOTALL) else 'None'}")
                        print(f"  Fixed params: {re.search(r'\\(([^)]+)\\)', fixed_query, re.DOTALL).group(1) if re.search(r'\\(([^)]+)\\)', fixed_query, re.DOTALL) else 'None'}")
                
                # Also fix variables if needed
                if 'variables' in graphql and isinstance(graphql['variables'], str):
                    try:
                        vars_obj = json.loads(graphql['variables'])
                        if 'preconditionIds' in vars_obj and 'addPreconditionsToTest' in graphql.get('query', ''):
                            vars_obj['preconditionIssueIds'] = vars_obj.pop('preconditionIds')
                            graphql['variables'] = json.dumps(vars_obj, indent=2)
                            print(f"  Fixed variables for: {item.get('name', 'Unknown')}")
                    except:
                        pass
        
        # Process sub-items
        if 'item' in item:
            for sub_item in item['item']:
                process_item(sub_item)
    
    # Process all items in the collection
    if 'item' in collection:
        for item in collection['item']:
            process_item(item)
    
    # Write the fixed collection
    output_path = file_path.replace('.json', '_fixed.json')
    with open(output_path, 'w') as f:
        json.dump(collection, f, indent=2)
    
    print(f"\nFixed {fixed_count} queries/mutations")
    print(f"Output saved to: {output_path}")
    
    return output_path

def main():
    """Main function"""
    
    file_path = "/Users/douglas.mason/Documents/GitHub/xray-importer/sdui-test-creation/xray-graphql-postman-collection.json"
    
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return
    
    print("Fixing GraphQL required field markers in Postman collection...")
    print("=" * 60)
    
    output_path = fix_postman_collection(file_path)
    
    print("\nComplete!")
    print(f"Please review the fixed collection at: {output_path}")

if __name__ == "__main__":
    main()