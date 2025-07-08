# JIRA Field Requirements and Validation

This document provides detailed information about JIRA fields used in XRAY GraphQL operations, including requirements, validation rules, and best practices.

## Table of Contents
1. [JIRA Field Overview](#jira-field-overview)
2. [Required Fields](#required-fields)
3. [Standard Optional Fields](#standard-optional-fields)
4. [Custom Fields](#custom-fields)
5. [Field Validation Rules](#field-validation-rules)
6. [Label Management](#label-management)
7. [Component Management](#component-management)
8. [User Fields](#user-fields)
9. [Common Issues and Solutions](#common-issues-and-solutions)

## JIRA Field Overview

JIRA fields in GraphQL mutations are passed as a JSON object within the `jira` parameter. The structure follows JIRA's REST API format:

```json
{
  "fields": {
    "project": { "key": "MLB" },
    "summary": "Test title",
    "issuetype": { "name": "Test" },
    // ... other fields
  }
}
```

## Required Fields

### 1. Project

**Field**: `project`  
**Type**: Object  
**Required**: Yes  
**Formats**:
- By key: `{ "key": "MLB" }`
- By ID: `{ "id": "10000" }`

**Validation**:
- Project must exist in JIRA
- User must have permission to create issues in the project
- Project must have XRAY enabled

### 2. Summary

**Field**: `summary`  
**Type**: String  
**Required**: Yes  
**Max Length**: 255 characters

**Best Practices**:
- Include test ID: `"TC-001: Test Name"`
- Be descriptive but concise
- Follow naming convention: `"[Component] - [Function] - [Expected Outcome]"`

**Examples**:
```json
"summary": "TC-001: Team Selection via Drawer"
"summary": "Browse Menu - Navigation - User can switch teams"
"summary": "API-050: Verify team roster endpoint returns 200"
```

### 3. Issue Type

**Field**: `issuetype`  
**Type**: Object  
**Required**: Yes  
**Formats**:
- By name: `{ "name": "Test" }`
- By ID: `{ "id": "10100" }`

**Valid Values for XRAY**:
- `Test` - For test cases
- `Test Set` - For test sets
- `Test Plan` - For test plans
- `Test Execution` - For test executions
- `Pre-Condition` - For preconditions

## Standard Optional Fields

### 1. Description

**Field**: `description`  
**Type**: String  
**Format**: Plain text, Wiki markup, or Markdown (depending on JIRA config)

**Example**:
```json
"description": "This test verifies that users can successfully select a different team from the team drawer. The test covers both iOS and Android platforms and ensures smooth navigation."
```

### 2. Labels

**Field**: `labels`  
**Type**: Array of Strings  
**Validation**:
- Labels are case-sensitive
- No spaces allowed (use hyphens or underscores)
- Maximum 255 characters per label

**Example**:
```json
"labels": [
  "@team-page",
  "@functional",
  "@critical",
  "@smoke",
  "@navigation",
  "@ios",
  "@android"
]
```

### 3. Priority

**Field**: `priority`  
**Type**: Object  
**Formats**:
- By name: `{ "name": "High" }`
- By ID: `{ "id": "2" }`

**Standard Values**:
- `Critical` (ID: 1)
- `High` (ID: 2)
- `Medium` (ID: 3)
- `Low` (ID: 4)

### 4. Components

**Field**: `components`  
**Type**: Array of Objects  
**Validation**: Components must exist in the project

**Example**:
```json
"components": [
  { "name": "Team Page" },
  { "name": "Navigation" }
]
```

### 5. Fix Versions

**Field**: `fixVersions`  
**Type**: Array of Objects  
**Validation**: Versions must exist in the project

**Example**:
```json
"fixVersions": [
  { "name": "2.0" },
  { "name": "2.1-sprint-15" }
]
```

### 6. Due Date

**Field**: `duedate`  
**Type**: String  
**Format**: `YYYY-MM-DD`

**Example**:
```json
"duedate": "2025-07-15"
```

## Custom Fields

Custom fields are referenced by their ID (e.g., `customfield_10001`). Common XRAY custom fields include:

### Test Type (if exposed as custom field)
```json
"customfield_10200": "Manual"
```

### Test Repository Path
```json
"customfield_10201": "/Team Page/Core Navigation"
```

### Automation Status
```json
"customfield_10202": {
  "value": "Not Automated"
}
```

### Environment
```json
"customfield_10203": ["iOS", "Android"]
```

### Test Category
```json
"customfield_10204": {
  "value": "Regression"
}
```

## Field Validation Rules

### String Fields

| Rule | Description | Example |
|------|-------------|---------|
| Max Length | Summary: 255, Description: 32,767 | Truncate if needed |
| Special Characters | Escape quotes and backslashes | `"Test \"quoted\" text"` |
| Line Breaks | Use `\n` for new lines | `"Line 1\nLine 2"` |

### Array Fields

| Rule | Description | Example |
|------|-------------|---------|
| Empty Arrays | Allowed for optional fields | `"labels": []` |
| Duplicates | Usually filtered by JIRA | `["@ios", "@ios"]` → `["@ios"]` |
| Order | Preserved as submitted | Labels appear in order |

### Object Fields

| Rule | Description | Example |
|------|-------------|---------|
| Reference Format | Use name, key, or id | `{ "name": "High" }` |
| Case Sensitivity | Usually case-sensitive | "High" ≠ "high" |
| Existence | Must exist in JIRA | Component must be created first |

## Label Management

### Label Naming Convention

Based on the SDUI test organization strategy:

```
@<category>-<value>
```

### Label Categories

1. **Feature Labels**
   ```json
   ["@browse-menu", "@team-page", "@gameday", "@scoreboard"]
   ```

2. **Test Type Labels**
   ```json
   ["@functional", "@api", "@integration", "@e2e"]
   ```

3. **Platform Labels**
   ```json
   ["@ios", "@android", "@ipad", "@cross-platform"]
   ```

4. **Priority Labels**
   ```json
   ["@critical", "@high", "@medium", "@low"]
   ```

5. **Execution Labels**
   ```json
   ["@smoke", "@regression", "@nightly", "@release", "@manual-only"]
   ```

6. **Component Labels**
   ```json
   ["@navigation", "@content-display", "@personalization", "@gamecell"]
   ```

7. **Jewel Event Labels**
   ```json
   ["@jewel-event", "@opening-day", "@all-star", "@postseason", "@world-series"]
   ```

8. **Game State Labels**
   ```json
   ["@game-state", "@preview-state", "@live-state", "@final-state", "@state-transition"]
   ```

9. **Data Requirement Labels**
   ```json
   ["@requires-live-game", "@requires-test-account", "@requires-favorite-team"]
   ```

### Label Validation Script

```python
def validate_labels(labels):
    """Validate labels against naming convention"""
    valid_prefixes = [
        '@browse-menu', '@team-page', '@gameday', '@scoreboard',
        '@functional', '@api', '@integration', '@e2e',
        '@ios', '@android', '@ipad', '@cross-platform',
        '@critical', '@high', '@medium', '@low',
        '@smoke', '@regression', '@nightly', '@release',
        '@navigation', '@content-display', '@gamecell',
        '@jewel-event', '@opening-day', '@all-star',
        '@game-state', '@preview-state', '@live-state',
        '@requires-'
    ]
    
    invalid_labels = []
    for label in labels:
        if not any(label.startswith(prefix) for prefix in valid_prefixes):
            invalid_labels.append(label)
    
    return invalid_labels
```

## Component Management

### Creating Components

Components must exist in JIRA before they can be assigned. Based on the SDUI strategy:

**Required Components**:
- Browse Menu
- Team Page
- Gameday
- Scoreboard
- Core Navigation
- Content Display
- Jewel Events
- Game States

### Component Assignment Rules

1. Primary component based on feature area
2. Secondary components for cross-cutting concerns
3. Maximum 3 components per test

**Example**:
```json
"components": [
  { "name": "Team Page" },        // Primary feature
  { "name": "Jewel Events" },     // Secondary concern
  { "name": "Performance" }       // Quality attribute
]
```

## User Fields

### Assignee

**Field**: `assignee`  
**Type**: Object  
**Formats**:
- By username: `{ "name": "jsmith" }`
- By email: `{ "name": "john.smith@example.com" }`
- By account ID: `{ "accountId": "5b10a2844c20165700ede21g" }`

**Validation**:
- User must exist in JIRA
- User must have appropriate permissions
- For unassigned: `null` or omit field

### Reporter

**Field**: `reporter`  
**Type**: Object  
**Format**: Same as assignee  
**Note**: Usually auto-set to API user

### Watchers

**Field**: `watchers`  
**Type**: Not directly settable via create  
**Alternative**: Use separate API call after creation

## Common Issues and Solutions

### 1. "Field 'customfield_X' cannot be set"

**Causes**:
- Field doesn't exist in project
- No permission to edit field
- Field is calculated/read-only

**Solution**:
```python
# Check field availability first
def get_editable_fields(project_key):
    # Use JIRA REST API to get createmeta
    response = requests.get(
        f"{JIRA_URL}/rest/api/2/issue/createmeta",
        params={
            "projectKeys": project_key,
            "issuetypeNames": "Test",
            "expand": "projects.issuetypes.fields"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.json()
```

### 2. "Label value 'X' is not valid"

**Causes**:
- Label contains spaces
- Label too long
- Special characters

**Solution**:
```python
def sanitize_label(label):
    # Replace spaces with hyphens
    label = label.replace(" ", "-")
    # Remove invalid characters
    label = re.sub(r'[^a-zA-Z0-9@_-]', '', label)
    # Truncate if needed
    return label[:255]
```

### 3. "Component with name 'X' does not exist"

**Solution**:
```python
def ensure_component_exists(project_key, component_name):
    # Check if component exists
    components = get_project_components(project_key)
    if component_name not in [c['name'] for c in components]:
        # Create component
        create_component(project_key, component_name)
```

### 4. "The summary is invalid because it contains newline characters"

**Solution**:
```python
def clean_summary(summary):
    # Remove newlines and extra spaces
    summary = summary.replace('\n', ' ').replace('\r', '')
    summary = ' '.join(summary.split())
    # Truncate to 255 characters
    return summary[:255]
```

## Field Dependencies

Some fields may have dependencies or interactions:

### Priority and Labels
If using priority labels (@critical, @high), ensure they match the priority field:

```python
def sync_priority_labels(fields):
    priority = fields.get('priority', {}).get('name', 'Medium')
    labels = fields.get('labels', [])
    
    # Remove old priority labels
    labels = [l for l in labels if not l.startswith('@critical') 
              and not l.startswith('@high') 
              and not l.startswith('@medium') 
              and not l.startswith('@low')]
    
    # Add matching priority label
    labels.append(f"@{priority.lower()}")
    
    fields['labels'] = labels
    return fields
```

### Test Type and Steps
Manual tests require steps, automated tests don't:

```python
def validate_test_type_fields(test_type, fields):
    if test_type == "Manual" and not fields.get('steps'):
        raise ValueError("Manual tests require at least one step")
    if test_type == "Automated" and fields.get('steps'):
        print("Warning: Automated tests typically don't have manual steps")
```

## Best Practices

1. **Validate Before Submission**
   - Check required fields
   - Validate field formats
   - Ensure referenced entities exist

2. **Use Consistent Naming**
   - Follow established conventions
   - Use prefixes for test IDs
   - Maintain label taxonomy

3. **Handle Errors Gracefully**
   - Parse error responses
   - Provide meaningful error messages
   - Implement retry logic for transient failures

4. **Batch Operations**
   - Validate all tests before creating any
   - Use transactions where possible
   - Track successful and failed operations

5. **Maintain Data Quality**
   - Regular label cleanup
   - Component rationalization
   - Version management

## Validation Utility

Complete validation function for JIRA fields:

```python
def validate_jira_fields(fields, test_type="Manual"):
    """Comprehensive JIRA field validation"""
    errors = []
    
    # Required fields
    if not fields.get('project'):
        errors.append("Project is required")
    if not fields.get('summary'):
        errors.append("Summary is required")
    elif len(fields['summary']) > 255:
        errors.append("Summary exceeds 255 characters")
    if not fields.get('issuetype'):
        errors.append("Issue type is required")
    
    # Labels validation
    if 'labels' in fields:
        invalid_labels = validate_labels(fields['labels'])
        if invalid_labels:
            errors.append(f"Invalid labels: {invalid_labels}")
    
    # Priority validation
    if 'priority' in fields:
        valid_priorities = ['Critical', 'High', 'Medium', 'Low']
        priority_name = fields['priority'].get('name')
        if priority_name not in valid_priorities:
            errors.append(f"Invalid priority: {priority_name}")
    
    # Date validation
    if 'duedate' in fields:
        try:
            datetime.strptime(fields['duedate'], '%Y-%m-%d')
        except ValueError:
            errors.append("Due date must be in YYYY-MM-DD format")
    
    return errors
```

This completes the comprehensive documentation of JIRA field requirements and validation rules for XRAY test creation.