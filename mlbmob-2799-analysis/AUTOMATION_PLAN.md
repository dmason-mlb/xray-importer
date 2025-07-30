# COMPREHENSIVE PLAN: Automated XRAY Test Step Updates

## Overview
This plan provides a systematic approach to automatically update 11 XRAY test cases in MLBMOB-2799 with detailed test steps from the Confluence-sourced JSON file, leveraging existing infrastructure while ensuring data integrity and safety.

## Project Structure
```
Input:  mlbmob_2799_confluence_test_steps.json (11 test cases)
Reference: mlbmob/update_xray_tests.py
Output: Updated XRAY test cases with proper test steps
```

## Execution Flow Diagram
```
Phase 1: Data Prep        Phase 2: Script Dev       Phase 3: Validation
    |                          |                         |
    v                          v                         v
[Transform JSON]  --->  [Adapt Scripts]  --->  [Test Single Case]
[Backup Tests]          [Add Functions]        [Verify Rollback]
[Validate Data]         [Dry-Run Mode]         [API Connectivity]
    |                          |                         |
    v                          v                         v
Phase 4: Execution        Phase 5: Verification
    |                          |
    v                          v
[Batch Updates]  --->  [Final Validation]
[Monitor Progress]      [Generate Reports]
[Handle Errors]         [Document Changes]
```

## PHASE 1: DATA PREPARATION & VALIDATION

### 1.1 Data Transformation Script
**Create: `transform_confluence_data.py`**
- Read `mlbmob_2799_confluence_test_steps.json`
- Transform step format to match XRAY GraphQL schema
- Key transformations:
  ```
  Input:  "action": "1. Step1\n2. Step2\n..."
  Output: "action": "1. Step1\n2. Step2\n..."
  ```
- Validate required fields: action, result, data
- Output: `xray_ready_test_steps.json`

### 1.2 Backup Current Test States
**Create: `backup_current_tests.py`**
- Query current state of all 11 test cases
- Save complete test data to `test_backup_TIMESTAMP.json`
- Include: test metadata, existing steps, current status
- Verify backup completeness and integrity

### 1.3 Data Validation Checks
- Confirm all 11 test cases have valid issue IDs
- Check step content length limits (GraphQL constraints)
- Validate special characters that could break API calls
- Ensure JSON structure matches expected format

## PHASE 2: SCRIPT DEVELOPMENT & TESTING

### 2.1 Core Script Development
**Create: `update_test_steps.py`** (adapted from `update_xray_tests.py`)

**Key adaptations:**
- Remove precondition logic
- Focus on test step operations
- Add comprehensive logging
- Implement progress tracking

### 2.2 Essential Functions
```python
def load_test_steps_data(file_path):
    # Load and validate transformed JSON data

def add_test_steps_to_xray(test_id, steps, token):
    # Core function to add steps via GraphQL API

def validate_test_step_format(step):
    # Validate step structure before API call

def check_update_success(test_id, expected_steps, token):
    # Verify steps were added correctly

def generate_progress_report(completed, total, errors):
    # Real-time progress tracking
```

### 2.3 Testing Framework
- **Dry-run mode**: Show exactly what would be updated
- **Single test capability**: Test with one case first
- **Comprehensive error handling**: Graceful failure recovery
- **Detailed logging**: Timestamp all operations

## PHASE 3: SAFETY & VALIDATION FRAMEWORK

### 3.1 Pre-execution Validation
**Validation checklist:**
- [ ] API authentication successful
- [ ] All 11 test cases exist and accessible
- [ ] Tests not locked or in active use
- [ ] Transformed data passes format validation
- [ ] Backup files created and verified

### 3.2 Single Test Validation
**Test case: MLBMOB-1567 (Exec Users)**
1. Execute update in isolated environment
2. Verify step added correctly
3. Check step content matches source
4. Test rollback mechanism
5. Confirm no data corruption

### 3.3 Rollback Implementation
**Create: `rollback_test_steps.py`**
- Use backup data to restore original state
- Remove added steps completely
- Restore original test metadata
- Verify complete restoration
- Test rollback on single case first

## PHASE 4: EXECUTION & MONITORING

### 4.1 Batch Update Execution
**Execution sequence:**
```
For each test case:
1. Load test data
2. Validate step format
3. Execute API call
4. Verify success
5. Log results
6. Handle rate limiting
7. Continue to next test
```

### 4.2 Error Handling & Recovery
**Error scenarios:**
- API rate limiting: Implement exponential backoff
- Network failures: Retry with timeout
- Authentication expiry: Re-authenticate automatically
- Data format errors: Skip and log for manual review
- Critical failures: Trigger immediate rollback

### 4.3 Progress Monitoring
- Real-time progress updates
- Success/failure counters
- Detailed error logs with context
- Checkpoint system for resume capability

## PHASE 5: VERIFICATION & CLEANUP

### 5.1 Final Validation
**Verification checklist:**
- [ ] Query all 11 test cases
- [ ] Confirm steps were added correctly
- [ ] Validate step content matches source
- [ ] Test execution readiness confirmed
- [ ] No data corruption detected

### 5.2 Documentation & Reporting
**Generate comprehensive report:**
- Summary of all changes made
- Test cases updated successfully
- Any errors encountered
- Rollback instructions
- Performance metrics

### 5.3 Cleanup Operations
- Archive backup files
- Organize log files
- Clean up temporary files
- Prepare handoff documentation

## FILES TO CREATE

```
/mlbmob-2799-analysis/
├── transform_confluence_data.py      # Phase 1.1
├── backup_current_tests.py           # Phase 1.2
├── update_test_steps.py              # Phase 2.1
├── rollback_test_steps.py            # Phase 3.3
├── xray_ready_test_steps.json        # Phase 1.1 output
├── test_backup_TIMESTAMP.json       # Phase 1.2 output
├── update_log_TIMESTAMP.txt          # Phase 4 output
└── final_report_TIMESTAMP.md        # Phase 5 output
```

## EXECUTION SEQUENCE

1. **Phase 1**: Run data preparation scripts
2. **Phase 2**: Test scripts in dry-run mode
3. **Phase 3**: Validate with single test case
4. **Phase 4**: Execute batch updates with monitoring
5. **Phase 5**: Complete verification and documentation

## SAFETY MEASURES

- **Backup before any changes**: Complete test state preservation
- **Dry-run validation**: Test all logic before execution
- **Single test validation**: Prove concept before batch
- **Rollback capability**: Full restoration possible
- **Progress checkpoints**: Resume from failure points
- **Comprehensive logging**: Full audit trail

## SUCCESS CRITERIA

- All 11 test cases have proper test steps
- Step content matches source JSON data
- No data loss or corruption
- Complete audit trail maintained
- Rollback tested and available
- MLBMOB-2799 test execution ready

## EXECUTION STATUS

This plan was created on 2025-07-17 and is ready for implementation. The automation will be executed phase by phase with careful validation at each step.