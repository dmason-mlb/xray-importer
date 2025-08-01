# Xray Remediation Documentation Map

**Last Updated**: 2025-07-31

## Quick Navigation

This guide helps you find the right documentation for your needs.

## 📋 Core Documentation

### [PROJECT_STATUS.md](./PROJECT_STATUS.md)
**What it contains**: Current project status, metrics, completion percentages
**Use when**: You need an executive summary or progress update
**Key sections**: 
- Executive Summary
- Project Metrics (test counts)
- Completion Status by Component
- Known Issues & Next Steps

### [TEAM_PAGE_TEST_CATALOG.md](./TEAM_PAGE_TEST_CATALOG.md)
**What it contains**: Complete list of all 93 tests with details
**Use when**: Looking up specific test IDs, JIRA mappings, or test descriptions
**Key sections**:
- Summary table (test counts by type)
- API Tests (55 tests with JIRA keys)
- Functional Tests (38 tests pending creation)
- Implementation details

### [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md)
**What it contains**: Technical procedures and code examples
**Use when**: Implementing Xray integration, running scripts, or troubleshooting
**Key sections**:
- Environment setup
- Authentication system
- API integration examples
- Script reference
- Troubleshooting guide

### [README.md](./README.md)
**What it contains**: Project overview and quick start
**Use when**: First time setup or understanding project structure
**Key sections**:
- Directory structure
- Basic operations
- Environment variables

### [CLAUDE.md](./CLAUDE.md)
**What it contains**: Instructions for AI assistance
**Use when**: Working with Claude Code or understanding project context
**Key sections**:
- Key context and test sources
- Technical architecture
- Code quality standards

## 📁 Directory Structure

```
xray-remediation/
├── 📄 Core Documentation (You are here)
│   ├── PROJECT_STATUS.md         # Current status
│   ├── TEAM_PAGE_TEST_CATALOG.md # All tests
│   ├── IMPLEMENTATION_GUIDE.md   # How-to guide
│   ├── DOCUMENTATION_MAP.md      # This file
│   ├── README.md                 # Overview
│   └── CLAUDE.md                 # AI instructions
│
├── 📂 scripts/                   # Executable scripts
│   ├── organize_xray_folders.py  # Folder management
│   ├── update_all_pytest_decorators.py # Pytest integration
│   └── [other working scripts]
│
├── 📂 test-data/                 # Test definitions
│   ├── api_tests_xray.json       # 55 API tests
│   └── functional_tests_xray.json # 38 functional tests
│
├── 📂 logs/                      # Execution logs
│   └── comprehensive_pytest_decorator_update_*.json
│
└── 📂 documentation/archive/     # Historical docs
    ├── status_reports/           # Old status files
    └── old_scripts/              # Deprecated scripts
```

## 🔍 Finding Information

### "I need to know..."

**Current project status?**
→ Read [PROJECT_STATUS.md](./PROJECT_STATUS.md)

**What tests exist?**
→ Browse [TEAM_PAGE_TEST_CATALOG.md](./TEAM_PAGE_TEST_CATALOG.md)

**How to run a script?**
→ Check [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md)

**JIRA ticket for a test?**
→ Search in [TEAM_PAGE_TEST_CATALOG.md](./TEAM_PAGE_TEST_CATALOG.md)

**How to set up environment?**
→ See [README.md](./README.md) or [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md)

**Script documentation?**
→ Check script docstrings or [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md)

### "I need to do..."

**Create tests in Xray**
→ Use `scripts/create_missing_xray_tests.py`
→ See [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md#api-integration)

**Organize test folders**
→ Run `scripts/organize_xray_folders.py`
→ See [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md#folder-organization)

**Apply pytest decorators**
→ Run `scripts/update_all_pytest_decorators.py`
→ See [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md#pytest-integration)

**Extract tests from Confluence**
→ Use scripts in `confluence-tools/`
→ See [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md#test-extraction)

## 📊 Key Metrics

- **Total Tests**: 93 unique (55 API + 38 functional)
- **Tests in Xray**: 55 API tests created
- **Pending**: 38 functional tests
- **Preconditions**: 23 total (all organized)
- **Pytest Decorators**: 51 applied

## 🚀 Quick Commands

```bash
# Check current status
cat PROJECT_STATUS.md

# View all tests
cat TEAM_PAGE_TEST_CATALOG.md

# Run folder organization
python scripts/organize_xray_folders.py

# Apply pytest decorators
python scripts/update_all_pytest_decorators.py
```

## 📝 Historical Reference

Archived documentation can be found in:
- `/documentation/archive/status_reports/` - Old progress reports
- `/documentation/archive/old_scripts/` - Deprecated script versions

---

*Use this map to navigate the consolidated documentation. All critical information has been preserved and organized for easy access.*