# Xray Test Filtering and Modification Tools

This directory contains tools for fetching, filtering, and modifying Xray test cases.

## fetch_all_xray_tests.py

A robust script for fetching all test cases from an Xray project and categorizing them based on whether they have test steps.

### Features

- **Automatic retry logic** with exponential backoff for handling network issues
- **Rate limiting protection** to avoid overwhelming the Xray API
- **Progress tracking** allows resuming interrupted fetches
- **Token management** automatically refreshes expired authentication tokens
- **Comprehensive error handling** with clear error messages
- **Environment variable configuration** for easy customization
- **Detailed logging** shows progress and any issues encountered

### Setup

1. Copy the example environment file and add your credentials:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your Xray API credentials:
   ```
   XRAY_CLIENT=your_client_id_here
   XRAY_SECRET=your_client_secret_here
   ```

3. Install required dependencies:
   ```bash
   pip install requests python-dotenv
   ```

### Usage

Run the script:
```bash
python fetch_all_xray_tests.py
```

The script will:
1. Authenticate with the Xray API
2. Fetch all tests in batches of 100 (configurable)
3. Categorize tests into those with and without steps
4. Save results to JSON files
5. Track progress in case of interruption

### Output Files

- **tests_with_steps.json**: Contains all tests that have defined test steps
- **tests_without_steps.json**: Contains all tests without test steps
- **fetch_progress.json**: Tracks progress (automatically deleted on successful completion)

### Configuration Options

All configuration can be set via environment variables in the `.env` file:

- `PROJECT_ID`: The Xray project ID (default: 26420 for MLBMOB)
- `BATCH_SIZE`: Number of tests to fetch per API request (default: 100)
- `MAX_RETRIES`: Maximum retry attempts for failed requests (default: 5)
- `RETRY_WAIT`: Base wait time in seconds between retries (default: 2)
- `RATE_LIMIT_DELAY`: Delay in seconds between successful requests (default: 1)

### Resuming Interrupted Fetches

If the script is interrupted (network failure, Ctrl+C, etc.), it automatically saves progress. When you run it again, it will:

1. Detect the saved progress
2. Ask if you want to resume
3. Continue from where it left off

### Error Handling

The script handles various error scenarios:

- **Authentication failures**: Clear message about invalid credentials
- **Rate limiting**: Automatically waits and retries
- **Network timeouts**: Retries with exponential backoff
- **Invalid responses**: Validates response structure
- **Token expiration**: Automatically refreshes tokens

### Example Output

```
Xray Test Fetcher
================
Project ID: 26420
Batch Size: 100
Max Retries: 5
Rate Limit Delay: 1.0s

Authenticating with Xray API (attempt 1/5)...
✓ Successfully authenticated with Xray API

Fetching first batch to determine total count...
  Fetching batch starting at 0 (attempt 1/5)...
  ✓ Successfully fetched 100 tests

Total tests in project: 1919
Batches to fetch: 19
Estimated time: 40 seconds

Batch 1/19: Fetching tests 100 to 200...
  Fetching batch starting at 100 (attempt 1/5)...
  ✓ Successfully fetched 100 tests
...

==================================================
FETCH SUMMARY
==================================================
Total tests fetched: 1919
Tests with steps: 1453 (75.7%)
Tests without steps: 466 (24.3%)

Example tests without steps:
  - MLBMOB-1234: Login functionality test
  - MLBMOB-1235: Performance test for home screen
  ... and 461 more

✓ Results saved to:
  - /path/to/tests_with_steps.json
  - /path/to/tests_without_steps.json

✓ Fetch completed successfully. Progress file removed.
```

### Troubleshooting

1. **"Missing XRAY_CLIENT or XRAY_SECRET environment variables"**
   - Make sure you've created a `.env` file with your credentials
   - Check that the `.env` file is in the same directory as the script

2. **"Invalid credentials"**
   - Verify your client ID and secret are correct
   - Ensure your Xray license is active

3. **Rate limiting errors**
   - The script handles this automatically, but you can increase `RATE_LIMIT_DELAY` if needed

4. **Network timeouts**
   - The script retries automatically
   - If timeouts persist, check your internet connection

### Next Steps

After fetching the tests, you can:
1. Analyze tests without steps to identify which need to be updated
2. Use the data to bulk update tests
3. Generate reports on test coverage
4. Filter tests by various criteria (labels, priority, etc.)