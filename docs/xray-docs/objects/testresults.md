# TestResults

**Category:** Objects
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/testresults.doc.html

*menu* Types OBJECT
 # TestResults
 Test Results type

## linkGraphQL Schema definition
 `1type TestResults {23#   Total amount of issues.4total: Int 56#   The index of the first item to return in the page of results (page offset).7start: Int 89#   The maximum amount of Tests to be returned. The maximum is 100.10limit: Int 1112#   Test issue results.13results: [Test] 1415#   Warnings generated if you have a invalid Test16warnings: [String] 1718}`
## linkRequired by
 - CoverableIssuenullgetTestsnullPreconditionPrecondition issue typeQuerynullTestExecutionTest Execution issue typeTestPlanTest Plan issue typeTestSetTest Set type