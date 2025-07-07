# TestPlanResults

**Category:** Objects
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/testplanresults.doc.html

*menu* Types OBJECT
 # TestPlanResults
 Test Plan Results type

## linkGraphQL Schema definition
 `1type TestPlanResults {23#   Total amount of issues.4total: Int 56#   Index of the first item to return in the page of results (page offset).7start: Int 89#   Maximum amount of Test Plans to be returned. The maximum is 100.10limit: Int 1112#   Test Plan issue results.13results: [TestPlan] 1415#   Warnings generated during the operation.16warnings: [String] 1718}`
## linkRequired by
 - ExpandedTestExpaded test issue typegetTestPlansnullQuerynullTestTest issue typeTestExecutionTest Execution issue type