# CreateTestExecutionResult

**Category:** Objects
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/createtestexecutionresult.doc.html

*menu* Types OBJECT
 # CreateTestExecutionResult
 Create Test Execution Result type

## linkGraphQL Schema definition
 `1type CreateTestExecutionResult {23#   Test Execution that was created.4testExecution: TestExecution 56#   Test Environments that were created.7createdTestEnvironments: [String] 89#   Warnings generated during the operation.10warnings: [String] 1112}`
## linkRequired by
 - createTestExecutionnullMutationnull