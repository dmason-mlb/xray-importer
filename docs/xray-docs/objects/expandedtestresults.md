# ExpandedTestResults

**Category:** Objects
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/expandedtestresults.doc.html

*menu* Types OBJECT
 # ExpandedTestResults
 Expanded tests results type

## linkGraphQL Schema definition
 `1type ExpandedTestResults {23#   Total amount of issues.4total: Int 56#   The index of the first item to return in the page of results (page offset).7start: Int 89#   The maximum amount of Tests to be returned. The maximum is 100.10limit: Int 1112#   Expanded test issue results.13results: [ExpandedTest] 1415}`
## linkRequired by
 - getExpandedTestsnullQuerynull