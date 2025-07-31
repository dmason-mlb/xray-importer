# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository contains documentation and data files related to XRAY test case importing for JIRA. It appears to be primarily a data/documentation repository focused on test management strategies and CSV data files for test imports.

## Key Files

- `compass_artifact_wf-64449a48-b915-43f2-b41b-7163ba511108_text_markdown.md` - Comprehensive documentation on XRAY test case import capabilities, limitations, and best practices
- `*.csv` files - Test case data files (home_surface.csv, mlbapp.csv, news_surface.csv)

## Important Context

This repository deals with JIRA XRAY test management, specifically:
- Test case import strategies (CSV vs REST API)
- Test organization using XRAY's Test Repository feature
- Metadata field support and encoding requirements (ISO-8859-1 for CSV imports)
- Import limitations (1000 test maximum per operation)

## Key Technical Details

- CSV imports require ISO-8859-1 encoding (not UTF-8) for special characters
- Maximum 1000 tests per import operation
- Test Repository uses hierarchical folder structure with single folder membership per test
- Test Sets allow multiple membership for cross-cutting concerns
- CSV importer supports Manual, Generic, and Cucumber test types (as of v6.2+)
- REST API endpoint `/rest/raven/1.0/import/test/bulk` supports all test types

## Working with Test Data

When working with the CSV files in this repository:
- Ensure proper encoding (ISO-8859-1) for special characters
- Validate that all referenced entities (components, priorities, users) exist in target JIRA project
- Follow naming convention: `[Component] - [Function] - [Expected Outcome]`
- Keep Test Sets small (maximum 15 tests) for maintainability