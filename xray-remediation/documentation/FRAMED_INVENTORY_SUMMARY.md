# FRAMED Project Inventory Summary

Based on assessment data from 2025-07-16

## Current State in Xray

### Tests
- **Total Tests**: 50 (all Generic type)
- **All tests have test case ID labels** (e.g., API-REG-003, API-DATA-005)
- **All labels are lowercase** (confirmed by user)
- **No tests are in folders** (all at root level)

### Preconditions
- **Total Preconditions**: 42
- **Associated**: 8
- **Standalone**: 34 (need to be associated with tests)

## Issues to Fix

1. **Label Issues**
   - Remove test case ID labels from all 50 tests
   - Keep other lowercase labels as-is
   - Examples: API-REG-003, API-DATA-005, API-INT-001

2. **Folder Organization**
   - All 50 tests need to be moved to proper folders
   - Target structure: /Team Page/API Tests/[subfolder]

3. **Precondition Association**
   - 34 standalone preconditions need to be linked to appropriate tests

4. **Missing Functional Tests**
   - 38 functional tests exist in JSON but not in Xray
   - Need to be created from functional_tests_xray.json

5. **Pytest Decorators**
   - 66 pytest tests need Xray decorators
   - Discrepancy: 66 actual tests vs 51 documented

## JSON Truth Files

- **api_tests_xray.json**: 55 API test definitions
- **functional_tests_xray.json**: 38 functional test definitions
- These are the source of truth for remediation

## Next Steps

1. Create label cleanup script
2. Implement folder organization
3. Associate preconditions
4. Create functional tests
5. Add pytest decorators