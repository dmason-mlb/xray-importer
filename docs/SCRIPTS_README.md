# XRAY Test Management Scripts

## Active Scripts

After successful import and labeling of 1,407 tests from TestRail to XRAY, these scripts remain useful:

### 1. **`list_organizational_labels.py`**
- Lists all organizational labels (surface-* and feature-*) and their test counts
- Shows sample tests for each label
- Useful for understanding test distribution
```bash
python3 list_organizational_labels.py
```

### 2. **`delete_test.py`**
- Deletes a specific XRAY test issue from JIRA
- Requires confirmation before deletion
- Use with caution - deletion cannot be undone
```bash
python3 delete_test.py MLBAPP-XXXX
```

### 3. **`check_xray_issue_types.py`**
- Checks available XRAY issue types in MLBAPP project
- Useful for understanding what XRAY entities are available
```bash
python3 check_xray_issue_types.py
```

### 4. **`check_test_sets.py`** & **`delete_test_sets.py`**
- Emergency scripts to fix Test Set loading issues
- Use if the Testing Board won't load after bulk Test Set creation
```bash
# Check what Test Sets exist
python3 check_test_sets.py

# Delete auto-generated Test Sets if needed
python3 delete_test_sets.py --confirm
```

## Test Organization

All 1,407 tests are now organized using labels:

### Surface Labels (Primary):
- `surface-home` - 608 tests
- `surface-core` - 556 tests
- `surface-news` - 243 tests

### Feature Labels (Secondary):
- `feature-stories` - 185 tests
- `feature-video` - 157 tests
- `feature-configuration` - 138 tests
- And 19 more feature categories...

### Using Labels in JIRA/XRAY:

To filter tests by label, use JQL queries like:
```
project = MLBAPP AND issuetype = "Xray Test" AND labels = "surface-home"
project = MLBAPP AND issuetype = "Xray Test" AND labels = "feature-video"
project = MLBAPP AND issuetype = "Xray Test" AND labels = "surface-home" AND labels = "feature-authentication"
```

## Archived Scripts

All import, migration, and setup scripts have been moved to `archive_scripts/` directory since the import is complete.

## Environment Variables

Required for all scripts:
```bash
export JIRA_EMAIL="your-email@example.com"
export ATLASSIAN_TOKEN="your-api-token"
```