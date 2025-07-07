# TestRunIterationResults

**Category:** Objects
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/testruniterationresults.doc.html

*menu* Types OBJECT
 # TestRunIterationResults
 Test Run iterations results type

## linkGraphQL Schema definition
 `1type TestRunIterationResults {23#   Total amount of iterations.4total: Int 56#   Index of the first item to return in the page of results (page offset).7start: Int 89#   Maximum amount of iterations to be returned. The maximum is 100.10limit: Int 1112#   Iteration results.13results: [TestRunIteration] 1415}`
## linkRequired by
 - TestRunTest Run type