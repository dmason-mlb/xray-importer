# TestRunIterationStepResults

**Category:** Objects
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/testruniterationstepresults.doc.html

*menu* Types OBJECT
 # TestRunIterationStepResults
 Test Run iteration step results results type

## linkGraphQL Schema definition
 `1type TestRunIterationStepResults {23#   Total amount of steps.4total: Int 56#   Index of the first item to return in the page of results (page offset).7start: Int 89#   Maximum amount of step results to be returned. The maximum is 100.10limit: Int 1112#   Step results.13results: [TestRunIterationStepResult] 1415}`
## linkRequired by
 - TestRunIterationTest Run iteration type