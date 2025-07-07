# TestRunPreconditionResults

**Category:** Objects
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/testrunpreconditionresults.doc.html

*menu* Types OBJECT
 # TestRunPreconditionResults
 Precondition Results type

## linkGraphQL Schema definition
 `1type TestRunPreconditionResults {23#   Total amount of preconditions.4total: Int 56#   Index of the first item to return in the page of results (page offset).7start: Int 89#   Maximum amount of Preconditions to be returned. The maximum is 100.10limit: Int 1112#   Precondition results.13results: [TestRunPrecondition] 1415}`
## linkRequired by
 - TestRunTest Run type