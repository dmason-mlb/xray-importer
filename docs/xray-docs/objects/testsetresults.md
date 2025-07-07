# TestSetResults

**Category:** Objects
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/testsetresults.doc.html

*menu* Types OBJECT
 # TestSetResults
 Test Set Results

## linkGraphQL Schema definition
 `1type TestSetResults {23#   Total amount of issues.4total: Int 56#   Index of the first item to return in the page of results (page offset).7start: Int 89#   Maximum amount of test sets to be returned. The maximum is 100.10limit: Int 1112#   Test Set issue results.13results: [TestSet] 1415}`
## linkRequired by
 - ExpandedTestExpaded test issue typegetTestSetsnullQuerynullTestTest issue type