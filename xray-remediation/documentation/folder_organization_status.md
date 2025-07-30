# Folder Organization Status

**Date**: 2025-07-18
**Time**: 12:03 PM

## Issue Identified
The Xray GraphQL API for folder operations is not working as expected. The mutations we're trying to use:
- `createFolder` - Has different parameters than documented
- `getTestRepositoryFolders` - Query doesn't exist
- `moveTestToFolder` - Needs verification

## Error Details
1. `createFolder` mutation requires:
   - `path` parameter (not `testRepositoryPath`)
   - Doesn't accept `projectKey` or `name` directly
   - May need `projectId` instead of `projectKey`

2. Query for folders is not `getTestRepositoryFolders`

## Current State
- 39 tests need to be organized into folders
- All tests are currently at root level ("/")
- Folder structure has been planned but not implemented

## Alternative Approaches
1. Use Xray UI to manually create folder structure
2. Find correct GraphQL API documentation
3. Use REST API if available
4. Check if tests can be organized via JIRA labels/components instead

## Recommendation
Given the API issues, we should:
1. Complete the label cleanup for remaining tests (38 more)
2. Move on to precondition association (which should work)
3. Return to folder organization once we have correct API documentation

The folder organization is not blocking other tasks and can be done manually if needed.