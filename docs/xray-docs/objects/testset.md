# TestSet

**Category:** Objects
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/testset.doc.html

*menu* Types OBJECT
 # TestSet
 Test Set type

## linkGraphQL Schema definition
 `1type TestSet {23#   Issue id of the Test Set Issue.4issueId: String 56#   Project id of the Test Set Issue.7projectId: String 89#   List of Tests associated with the Test Set Issue.10# 11# Arguments12#   issueIds: Ids of the Tests.13#   limit: Maximum amount of tests to be returned. The maximum is 100.14#   start: Index of the first item to return in the page of results (page offset).15tests(issueIds: [String], limit: Int!, start: Int): TestResults 1617#   List of Xray History results for the issue18# 19# Arguments20#   limit: the maximum amount of entries to be returned. The maximum is 100.21#   start: the index of the first item to return in the page of results (page offset).22history(limit: Int!, start: Int): XrayHistoryResults 2324#   Extra Jira information of the Test Set Issue.25# 26# Arguments27#   fields: List of the fields to be displayed.28#   Check the field 'fields' of this Jira endpoint for more information.29jira(fields: [String]): JSON 3031#   Date when the test set was last modified.32lastModified: String 3334}`
## linkRequired by
 - CreateTestSetResultCreate Test Set Result typegetTestSetnullQuerynullTestSetResultsTest Set Results