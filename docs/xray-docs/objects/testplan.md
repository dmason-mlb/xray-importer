# TestPlan

**Category:** Objects
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/testplan.doc.html

*menu* Types OBJECT
 # TestPlan
 Test Plan issue type

## linkGraphQL Schema definition
 `1type TestPlan {23#   Id of the Test Plan issue.4issueId: String 56#   Project id of the Test Plan issue.7projectId: String 89#   List of Tests associated with the Test Plan issue.10# 11# Arguments12#   issueIds: the issue ids of the Tests.13#   limit: the maximum amount of tests to be returned. The maximum is 100.14#   start: the index of the first item to return in the page of results (page offset).15tests(issueIds: [String], limit: Int!, start: Int): TestResults 1617#   List of Test Executions associated with the Test Plan issue.18# 19# Arguments20#   issueIds: issue ids of the Test Executions.21#   limit: the maximum amount of tests to be returned. The maximum is 100.22#   start: the index of the first item to return in the page of results (page offset).23testExecutions(issueIds: [String], limit: Int!, start: Int): TestExecutionResults 2425#   List of Xray History results for the issue26# 27# Arguments28#   limit: the maximum amount of entries to be returned. The maximum is 100.29#   start: the index of the first item to return in the page of results (page offset).30history(limit: Int!, start: Int): XrayHistoryResults 3132#   Extra Jira information of the Test Plan issue.33# 34# Arguments35#   fields: list of the fields to be displayed.36#   Check the field 'fields' of this Jira endpoint for more information.37jira(fields: [String]): JSON 3839#   Folder structure of the Test Plan.40folders: FolderResults 4142#   Date when the test plan was last modified.43lastModified: String 4445}`
## linkRequired by
 - CreateTestPlanResultCreate Test Plan Result typegetTestPlannullQuerynullTestPlanResultsTest Plan Results type