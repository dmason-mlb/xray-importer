# TestExecutionResults

**Category:** Objects
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/testexecutionresults.doc.html

*menu* Types OBJECT
 # TestExecutionResults
 Test Execution Results Type

## linkGraphQL Schema definition
 `1type TestExecutionResults {23#   Total amount of issues.4total: Int 56#   Index of the first item to return in the page of results (page offset).7start: Int 89#   Maximum amount of Test Executions to be returned. The maximum is 100.10limit: Int 1112#   Test Execution issue results.13results: [TestExecution] 1415}`
## linkRequired by
 - ExpandedTestExpaded test issue typegetTestExecutionsnullQuerynullTestTest issue typeTestPlanTest Plan issue typeTestVersionnull