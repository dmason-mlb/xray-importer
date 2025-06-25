# XRAY test case import capabilities for JIRA

XRAY provides robust test case import functionality with specific capabilities and limitations that teams must understand for successful implementation. The choice between CSV and API import methods, along with proper organization strategies, significantly impacts test management efficiency.

## Test type requirements reveal critical version dependencies

**Test cases do not have to be "Manual" type**, but the import method you choose dramatically affects which types are supported. The XRAY Test Case Importer (CSV) historically supported only Manual tests until version 6.2. Currently, it supports Manual, Generic, and Cucumber test types. However, if you need to import Automated test types or have mixed test types, the REST API offers complete flexibility, supporting all XRAY test types including Manual, Cucumber, Generic, and Automated variants.

For organizations using the CSV importer, this limitation means you'll need to either separate your test types into different import batches or upgrade to version 6.2+ for broader support. The REST API endpoint `/rest/raven/1.0/import/test/bulk` handles all test types seamlessly, making it the preferred choice for heterogeneous test suites.

## Metadata field support exceeds standard expectations

XRAY's metadata field support during import is comprehensive and includes all the fields you mentioned plus many more. **Priority, created by, updated by, created date, and updated date are all fully supported**, along with standard JIRA fields like components, fix versions, assignee, and reporter. The system also supports XRAY-specific fields such as Test Repository Path for folder organization, Test Sets for grouping, and precondition associations.

Custom fields receive extensive support, including single-value fields, multi-select fields with delimiter configuration, cascading select lists using "parent -> child" format, and date/datetime pickers with configurable formats. However, there's a critical encoding requirement: while you might expect UTF-8, **XRAY requires ISO-8859-1 encoding** for proper display of special characters like umlauts or accents in CSV imports.

The import process validates that all referenced entities (components, priorities, users) exist in the target project before import execution, preventing partial imports due to missing references.

## Physical organization demands strategic hierarchy planning

Organizing test cases by physical features, screens, or locations works best using XRAY's Test Repository feature, which provides a hierarchical folder structure similar to a file system. The recommended approach creates top-level folders for major application areas (Frontend, Backend, Mobile), then subdivides by specific screens or functional areas.

For a web application, an effective structure might include:
- Frontend → Authentication → Login Screen, Registration Screen, Password Reset
- Frontend → Dashboard → Main Dashboard, User Profile, Settings
- Frontend → E-commerce → Product Catalog, Shopping Cart, Checkout Process

**Each test can only belong to one folder** in the Test Repository, enforcing clear ownership and preventing duplication. Complement this with Test Sets for cross-cutting concerns like regression testing or smoke tests, where tests can belong to multiple sets. Keep Test Sets small (maximum 15 tests) for maintainability, and use clear, descriptive folder names without special characters.

## Import limitations require careful planning and workarounds

The most significant limitation is the **1000 test maximum per import operation**, which applies to both CSV and API methods. Additionally, you can only import 2000 issue links (excluding the first link per test) in a single batch. These constraints mean large test suite migrations require careful batch planning.

Common issues include the "Test type not present" error, often caused by formatting problems even when the field appears correct. Permission-related errors frequently occur when users lack "Bulk Change" or "Create Issues" permissions. Field mapping errors arise when mandatory custom fields aren't properly mapped or when link fields aren't available on the appropriate screens.

Performance degrades with large test suites due to JIRA storage limitations and real-time indexing. To mitigate these issues, split large imports into sub-1000 test batches, validate all mandatory fields before import, test with small samples first, and schedule imports during off-peak hours.

## Optimal browsing structure combines multiple organization strategies

Creating an effective browsing and discovery structure requires leveraging multiple XRAY features in combination. Use the Test Repository for primary organization by application structure or feature areas. Apply consistent naming conventions following the pattern `[Component] - [Function] - [Expected Outcome]`, such as "Login Screen - Valid Credentials - Successful Authentication".

Implement a comprehensive labeling strategy with functional labels (login, payment, search), type labels (smoke, regression, e2e), and priority labels (critical, high, medium). Configure custom fields for additional categorization dimensions, and use JQL filtering capabilities for advanced searches like `project = PROJ AND issue type = Test AND labels in (smoke, critical)`.

The key is balancing hierarchical organization (Test Repository) with flexible grouping (Test Sets and labels) to support different access patterns and user needs.

## CSV import wins for reliability, API excels at automation

**For most organizations, CSV import via the Test Case Importer is more reliable** due to its built-in validation, intuitive wizard interface, and comprehensive error reporting. It provides pre-import validation, visual field mapping, and downloadable error logs with line-by-line details. The learning curve is minimal, making it accessible to non-technical team members.

The REST API is more reliable for automated processes when properly implemented with robust error handling. It offers superior performance (200-500 tests/minute vs 50-100 for CSV), native CI/CD integration, and programmatic control. However, it requires development expertise, thorough testing, and careful error handling implementation.

Choose CSV import for one-time migrations, manual test imports, non-technical users, and when data validation is critical. Select API import for CI/CD integration, high-volume operations requiring multiple batches, automated synchronization between systems, and custom integration development.

## Test step import requires specific formatting strategies

Test steps in CSV imports use a multi-row structure where each step is a separate row sharing the same Test Case Identifier (TCID). The mandatory fields include TCID (for grouping), Summary (JIRA requirement), and Action (step description). Optional fields encompass Data (test inputs), Expected Result (validation criteria), and up to 6 custom fields per step.

A properly formatted CSV structures test steps as:
```
TCID;Summary;Priority;Action;Data;Expected Result
TC001;Login Test;High;Open login page;;Login page displays
TC001;;;Enter username;testuser;
TC001;;;Enter password;pass123;
TC001;;;Click Submit;;User logged in successfully
```

For parameterized tests, use `${PARAMETER_NAME}` syntax in step fields, enabling data-driven testing with multiple iterations. The system supports datasets for combinatorial testing and modular test steps that reference other test cases.

BDD-style tests (Given/When/Then) import differently via .feature files through API endpoints, while traditional step-by-step tests use the CSV format. Each approach has distinct advantages: BDD for behavior-driven automated tests, traditional for detailed manual test execution.

## Implementation recommendations prioritize pragmatic choices

Start with the CSV Test Case Importer for initial migrations and manual test management, as it provides the best balance of functionality and usability. Implement clear organizational hierarchies using Test Repository for specification organization and Test Sets for execution grouping. Establish and document naming conventions and labeling strategies before beginning imports.

For technical teams, develop REST API integration for ongoing test synchronization and CI/CD pipelines, but maintain CSV import capability for ad-hoc needs. Always use ISO-8859-1 encoding for CSV files, validate mandatory fields before import, and test with small batches before full migration.

Monitor system performance during large imports and be prepared to adjust batch sizes. Save import configurations for reuse, and maintain detailed documentation of your organization's specific field mappings and custom field usage.

The key to successful XRAY test case imports lies in understanding these capabilities and limitations upfront, then designing your import strategy to work within these constraints while maximizing the tool's organizational and automation features.