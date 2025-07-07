# TestExecution

**Category:** Objects
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/testexecution.doc.html

*menu* Types OBJECT
 # TestExecution
 Test Execution issue type

## linkGraphQL Schema definition
 `1type TestExecution {23#   Id of the Test Execution issue.4issueId: String 56#   Project id of the Test Execution issue.7projectId: String 89#   Test Environments of the Test Execution.10testEnvironments: [String] 1112#   List of Tests associated with the Test Execution Issue.13# 14# Arguments15#   issueIds: the issue ids of the Tests.16#   limit: the maximum amount of tests to be returned. The maximum is 100.17#   start: the index of the first item to return in the page of results (page offset).18tests(issueIds: [String], limit: Int!, start: Int): TestResults 1920#   List of Test Plans associated with the Test Execution Issue.21# 22# Arguments23#   issueIds: Ids of the Test Plans.24#   limit: the maximum amount of Test Plans to be returned. The maximum is 100.25#   start: the index of the first item to return in the page of results (page offset).26testPlans(issueIds: [String], limit: Int!, start: Int): TestPlanResults 2728#   List of Test Runs for the Test Execution Issue.29# 30# Arguments31#   limit: the maximum amount of tests to be returned. The maximum is 100.32#   start: the index of the first item to return in the page of results (page offset).33testRuns(limit: Int!, start: Int): TestRunResults 3435#   List of Xray History results for the issue36# 37# Arguments38#   limit: the maximum amount of entries to be returned. The maximum is 100.39#   start: the index of the first item to return in the page of results (page offset).40history(limit: Int!, start: Int): XrayHistoryResults 4142#   Extra Jira information of the Test Execution Issue.43# 44# Arguments45#   fields: List of the fields to be displayed.46#   Check the field 'fields' of this Jira endpoint for more information.47jira(fields: [String]): JSON 4849#   Date when the test exec was last modified.50lastModified: String 5152}`
## linkRequired by
 - CreateTestExecutionResultCreate Test Execution Result typegetTestExecutionnullQuerynullTestExecutionResultsTest Execution Results TypeTestRunTest Run type