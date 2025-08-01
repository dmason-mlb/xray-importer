# XRAY Test Label Cleanup Guidelines

## Overview

This document provides guidelines for maintaining clean and consistent labels in XRAY test data to prevent issues during import and execution.

## Label Standards

### 1. No @ Symbols

**Problem**: @ symbols in labels can cause parsing issues in some test management systems.

**Solution**: Remove all @ symbols from labels.

```json
// ❌ Incorrect
"tags": ["@team-page", "@api", "@critical"]

// ✅ Correct
"tags": ["team_page", "api", "critical"]
```

### 2. Use Underscores Instead of Dashes

**Problem**: Dash-separated labels can be inconsistent with naming conventions and may cause issues in some systems.

**Solution**: Convert all dashes to underscores in labels.

```json
// ❌ Incorrect
"labels": ["team-page", "cross-platform", "user-profile"]

// ✅ Correct
"labels": ["team_page", "cross_platform", "user_profile"]
```

### 3. No Test IDs in Labels

**Problem**: Including test case IDs and summaries as labels (e.g., "TC-001: Team Selection via Drawer") creates duplicate information and clutters the label space.

**Solution**: 
- Remove test ID labels entirely
- Use the proper `summary` field for test descriptions
- Keep labels focused on categorization only

```json
// ❌ Incorrect
{
  "summary": "TC-001",
  "labels": ["TC-001: Team Selection via Drawer", "functional", "navigation"]
}

// ✅ Correct
{
  "summary": "Team Selection via Drawer",
  "labels": ["functional", "navigation", "team_page"]
}
```

### 4. Standardized Folder Structure

**Problem**: Inconsistent folder paths make test organization difficult.

**Solution**: Use standardized folder hierarchy:
- API Tests: `Test Repository/Team Page/API Tests`
- Functional Tests: `Test Repository/Team Page/Functional Tests`

## Label Categories

### Recommended Label Types

1. **Feature/Component Labels**
   - `team_page`
   - `user_profile`
   - `navigation`
   - `settings`

2. **Test Type Labels**
   - `functional`
   - `api`
   - `integration`
   - `performance`

3. **Priority Labels**
   - `critical`
   - `high`
   - `medium`
   - `low`

4. **Platform Labels**
   - `ios`
   - `android`
   - `cross_platform`

5. **Test Suite Labels**
   - `smoke`
   - `regression`
   - `manual`
   - `automated`

## Validation Checklist

Before importing test data to XRAY, verify:

- [ ] No @ symbols in any labels
- [ ] All labels use underscores, not dashes
- [ ] No test IDs included as labels
- [ ] Summary fields contain descriptive test names
- [ ] Folder structure follows standard convention
- [ ] Labels are categorized appropriately

## Automated Cleanup Script

A Python script is available to automatically clean test data JSON files:

```python
# Key transformations performed:
1. Remove @ symbols: tag.replace('@', '')
2. Convert dashes: tag.replace('-', '_')
3. Remove test ID labels: Skip labels matching r'TC-\d{3}:'
4. Extract summaries: Parse from test ID labels if needed
5. Standardize folders: Update to consistent paths
```

## Prevention Strategies

1. **Template Usage**: Use standardized templates for new test cases
2. **Validation Scripts**: Run validation before import
3. **Code Reviews**: Check label formatting in PR reviews
4. **Documentation**: Keep this guide updated and accessible
5. **Training**: Ensure team members understand label standards

## Common Mistakes to Avoid

1. **Mixing Conventions**: Don't mix dash and underscore formats
2. **Over-labeling**: Avoid redundant or overly specific labels
3. **Special Characters**: Stick to alphanumeric and underscores only
4. **Case Sensitivity**: Be consistent with capitalization
5. **Duplicate Labels**: Remove redundant labels in the same test

## Example Clean Test Data

### API Test Example
```json
{
  "testCaseId": "API-001",
  "title": "Get Team Page - Valid Team",
  "folderStructure": "Test Repository/Team Page/API Tests",
  "tags": [
    "team_page",
    "api",
    "critical",
    "cross_platform"
  ]
}
```

### Functional Test Example
```json
{
  "testInfo": {
    "summary": "Team Selection via Drawer",
    "labels": [
      "team_page",
      "functional",
      "navigation",
      "high",
      "manual"
    ],
    "folder": "Test Repository/Team Page/Functional Tests"
  }
}
```

## Maintenance

This document should be reviewed and updated:
- After any major test data import issues
- When new label categories are introduced
- During quarterly test management reviews
- When XRAY updates introduce new requirements

Last Updated: 2025-07-31