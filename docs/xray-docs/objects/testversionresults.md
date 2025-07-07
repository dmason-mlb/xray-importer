# TestVersionResults

**Category:** Objects
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/testversionresults.doc.html

*menu* Types OBJECT
 # TestVersionResults
 Test version results type

## linkGraphQL Schema definition
 `1type TestVersionResults {23#   Total amount of Test versions.4total: Int 56#   The index of the first item to return in the page of results (page offset).7start: Int 89#   The maximum amount of Test versions to be returned. The maximum is 100.10limit: Int 1112#   Test version results.13results: [TestVersion] 1415}`
## linkRequired by
 - ExpandedTestExpaded test issue typePreconditionPrecondition issue typeTestTest issue type