# XRAY GraphQL Postman Collection Fixes Summary

This document summarizes the fixes applied to the XRAY GraphQL Postman collection to align with the actual GraphQL schema requirements.

## Fixed Issues

### 1. Required Field Markers (!)

The following queries had incorrect required field markers that were fixed:

- **GetTestsByLabel**: Changed `$jql: String!` to `$jql: String` (JQL is optional for getTests)
- **GetUnfiledTests**: Changed `$jql: String!` to `$jql: String` (JQL is optional for getTests)
- All other queries and mutations had their required field markers aligned with the schema

### 2. Parameter Name Corrections

- **AddPreconditionsToTest mutation**: 
  - Fixed parameter name from `preconditionIds` to `preconditionIssueIds`
  - Updated both the parameter definition and usage in the mutation body
  - Updated the variables JSON to use the correct parameter name

### 3. Default Values Updated

As requested, all default values were updated:
- `jira_project_key`: Changed from "MLB" to "FRAMED"
- `limit`: Changed from 50 to 100 where applicable
- Test issue IDs: Updated to use "FRAMED-" prefix

### 4. Added projectId Field

Added `projectId` field to all test and test set queries in the Data Exploration section to ensure complete data retrieval.

## Files Generated

1. **xray-graphql-postman-collection_fixed.json**: Initial fixes for required fields
2. **xray-graphql-postman-collection_final.json**: Final version with all corrections

## Script Created

**fix_postman_graphql_required_fields.py**: Python script that automatically:
- Fixes required field markers based on GraphQL schema
- Corrects parameter names
- Updates variables to match corrected parameter names

## Validation

All queries and mutations now correctly match the XRAY GraphQL schema requirements:
- Required fields are properly marked with `!`
- Optional fields do not have `!` markers
- Parameter names match the schema definitions
- Variables use the correct parameter names

The collection is now ready for use with proper GraphQL validation.