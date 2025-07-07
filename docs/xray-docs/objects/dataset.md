# Dataset

**Category:** Objects
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/dataset.doc.html

*menu* Types OBJECT
 # Dataset
 Dataset type
Represents a single Dataset entity with its metadata, parameters, and associated dataset rows.

## linkGraphQL Schema definition
 `1type Dataset {23#   Unique identifier of the Dataset.4id: String 56#   The ID of the test issue associated with the Dataset.7testIssueId: String 89#   The ID of the test execution issue associated with the Dataset.10testExecIssueId: String 1112#   The ID of the test plan issue associated with the Dataset.13testPlanIssueId: String 1415#   The ID of the test step associated with the Dataset (only for test step datasets).16testStepId: String 1718#   The ID of the call test issue (only for test step datasets).19callTestIssueId: String 2021#   Parameters of the Dataset, represented as an array of key-value pairs.22parameters: [Parameter] 2324#   The rows of the Dataset, representing combinatorial data.25rows: [DatasetRow] 2627}`
## linkRequired by
 - ExpandedTestExpaded test issue typegetDatasetnullgetDatasetsnullQuerynullTestTest issue type