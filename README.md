# XRAY Importer Utilities

This repository contains various scripts and reference documents used while experimenting with the XRAY GraphQL API and test case imports.

The project has been cleaned up to make it easier to navigate.  All operational scripts now live under the `scripts/` directory and the documentation has been consolidated under `docs/`.

## Repository layout

```
import_data/     CSV files and sample data
scripts/         Python and shell utilities
    integration/  Postman helper scripts
    mlbmob/       MLBMOB test updates
    xray-upload/  Bulk upload tools
    ...          other helpers
xray-remediation/ **untouched remediation work**
docs/            Reference guides and API documentation
```

See the documents in `docs/` for details on the original import strategies and API examples.  The previous script summary has been moved to `docs/SCRIPTS_README.md`.

## Quick start
1. Install dependencies as needed by individual scripts (typically `requests` and `python-dotenv`).
2. Export your XRAY and JIRA credentials as environment variables before running any scripts.

```bash
export JIRA_BASE_URL="https://your-domain.atlassian.net"
export JIRA_EMAIL="user@example.com"
export ATLASSIAN_TOKEN="your-token"
export XRAY_CLIENT_ID="client_id"
export XRAY_CLIENT_SECRET="client_secret"
```

Each script in `scripts/` is self-contained.  Review the script header comments for usage instructions.
