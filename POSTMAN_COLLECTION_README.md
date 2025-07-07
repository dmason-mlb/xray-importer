# Xray GraphQL API Postman Collection

This is a complete Postman collection for the Xray GraphQL API, generated directly from the API's introspection schema.

## Features

- **Complete API Coverage**: All queries and mutations from the Xray GraphQL API
- **Organized by Category**: Requests are grouped into folders by functionality
- **GraphQL Mode**: Uses Postman's native GraphQL support for better syntax highlighting
- **Auto-Authentication**: Includes test scripts to automatically save JWT tokens
- **Example Variables**: Pre-filled with sensible example values
- **Proper Field Selection**: Queries include appropriate field selections based on the schema

## Setup Instructions

1. **Import the Collection**
   - Open Postman
   - Click "Import" → "Upload Files"
   - Select `xray-postman-collection-enhanced.json`

2. **Configure Variables**
   - Click on the collection name → "Variables" tab
   - Set these required variables:
     - `xray_client_id`: Your Xray API Client ID
     - `xray_client_secret`: Your Xray API Client Secret
   - Optional: Update `project_id` if not using MLBMOB (default: 26420)

3. **Authenticate**
   - Run the "Get JWT Token" request in the "0. Authentication" folder
   - The token will be automatically saved to the `xray_token` variable
   - Token expiration is tracked and logged in the console

## Collection Structure

```
Xray GraphQL API/
├── 0. Authentication/
│   └── Get JWT Token
├── 1. Queries - Folders/
│   └── getFolder
├── 1. Queries - Tests/
│   ├── getTest
│   ├── getTests
│   └── ...
├── 1. Queries - Test Executions/
│   ├── getTestExecution
│   └── getTestExecutions
├── 1. Queries - Test Plans/
├── 1. Queries - Test Sets/
├── 1. Queries - Test Runs/
├── 1. Queries - Preconditions/
├── 1. Queries - Datasets/
├── 1. Queries - Statuses/
├── 2. Mutations - Folders/
├── 2. Mutations - Tests/
├── 2. Mutations - Test Steps/
└── ... (more mutation categories)
```

## Usage Examples

### Get a Test
1. Navigate to "1. Queries - Tests" → "getTest"
2. Update the `issueId` variable to your test's ID
3. Send the request

### Create a Test
1. Navigate to "2. Mutations - Tests" → "createTest"
2. Review and modify the variables:
   - `testType`: The type of test (Manual, Gherkin, etc.)
   - `steps`: Array of test steps
   - `jira`: JIRA fields for the test
3. Send the request

### Query Folders
1. Navigate to "1. Queries - Folders" → "getFolder"
2. Set variables:
   - `projectId`: Your project ID (or use {{project_id}})
   - `path`: The folder path (e.g., "/" for root)
3. Send the request

## GraphQL Variables

All GraphQL requests use Postman's GraphQL mode with separate query and variables sections:
- **Query**: The GraphQL query/mutation (read-only, defined by the schema)
- **Variables**: JSON object with input values (editable)

You can use Postman variables in the Variables section:
```json
{
  "projectId": "{{project_id}}",
  "issueId": "{{test_id}}"
}
```

## Authentication

The collection uses Bearer token authentication:
- Token is automatically set after running the authentication request
- All GraphQL requests inherit the collection-level auth
- Token expires after 24 hours (logged in console)

## Tips

1. **Use Environment Variables**: Create environments for different projects/instances
2. **Save Responses**: Use "Save Response" to create examples for documentation
3. **Fork for Customization**: Fork the collection to add your own requests
4. **Check Console**: Authentication status and token expiry are logged to console
5. **Bulk Operations**: Many queries support `limit` and `start` for pagination

## Troubleshooting

- **"Token missing or expired"**: Run the authentication request
- **"401 Unauthorized"**: Check your client ID and secret
- **"Field not found"**: The schema may have changed; regenerate the collection
- **Empty responses**: Check if you have access to the requested resources

## Generated from Schema

This collection was automatically generated from the Xray GraphQL schema using introspection. To regenerate with the latest schema:

1. Set `XRAY_CLIENT` and `XRAY_SECRET` environment variables
2. Run `python3 graphql_introspection.py`
3. Run `python3 generate_postman_collection.py`
4. Run `python3 enhance_postman_collection.py`