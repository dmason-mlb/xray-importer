# TestRunResults

**Category:** Objects
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/testrunresults.doc.html

*menu* Types OBJECT
 # TestRunResults
 Test Run Results type

## linkGraphQL Schema definition
 `1type TestRunResults {23#   Total amount of Test Runs.4total: Int 56#   The index of the first item to return in the page of results (page offset).7start: Int 89#   The maximum amount of Test Runs to be returned. The maximum is 100.10limit: Int 1112#   Test Run results.13results: [TestRun] 1415}`
## linkRequired by
 - ExpandedTestExpaded test issue typegetTestRunsnullgetTestRunsByIdnullQuerynullTestTest issue typeTestExecutionTest Execution issue typeTestVersionnull