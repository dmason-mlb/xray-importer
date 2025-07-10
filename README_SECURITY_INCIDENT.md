# Security Incident: XRAY Credentials Exposure

## Summary
XRAY API credentials were accidentally hardcoded and committed to the repository in the following files:
- `get_test_set_and_compare.py`
- `get_all_test_set_tests.py`

## Remediation Steps Completed

### 1. Created Environment Variable Configuration
- Created `.env` file with the credentials (now in .gitignore)
- Created `.env.example` template for other users
- Updated `.gitignore` to exclude `.env` file

### 2. Updated Python Scripts
Both affected scripts now use environment variables instead of hardcoded credentials:
```python
from dotenv import load_dotenv
load_dotenv()

XRAY_CLIENT = os.getenv('XRAY_CLIENT_ID')
XRAY_SECRET = os.getenv('XRAY_CLIENT_SECRET')
```

### 3. Git History Cleanup Script
Created `remove_credentials_from_history.sh` to remove credentials from git history.

## Required Actions

### Immediate Actions Required:
1. **Run the cleanup script** to remove credentials from git history:
   ```bash
   ./remove_credentials_from_history.sh
   ```

2. **Regenerate XRAY credentials** immediately after cleanup:
   - Log into your XRAY account
   - Revoke the exposed credentials
   - Generate new credentials
   - Update the `.env` file with new credentials

3. **Force push to remote** (after running cleanup script):
   ```bash
   git push origin --force --all
   git push origin --force --tags
   ```

### Team Communication Required:
1. Notify all team members about the security incident
2. Have them delete their local clones and re-clone the repository
3. Share the new credentials securely (never via git)

### Additional Security Measures:
1. Review any CI/CD systems that may have cached the old credentials
2. Check any logs or artifacts that might contain the exposed credentials
3. If this is a public repository, contact GitHub support to purge cached views

## Prevention Measures
1. Always use environment variables for sensitive data
2. Use `.env` files locally (never commit them)
3. Provide `.env.example` templates with dummy values
4. Add pre-commit hooks to scan for credentials
5. Regular security audits of the codebase

## Using the Updated Scripts
To use the updated scripts:
1. Copy `.env.example` to `.env`
2. Fill in your XRAY credentials in `.env`
3. Install python-dotenv: `pip install python-dotenv`
4. Run the scripts as before

The scripts will now load credentials from the environment instead of having them hardcoded.