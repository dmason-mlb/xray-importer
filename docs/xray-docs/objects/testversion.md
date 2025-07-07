# TestVersion

**Category:** Objects
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/testversion.doc.html

*menu* Types OBJECT
 # TestVersion

## linkGraphQL Schema definition
 `1type TestVersion {23#   Number of the Test version.4id: Int! 56#   Name of the Test version.7name: String! 89#   If is the default Test version.10default: Boolean! 1112#   If is an archived Test version.13archived: Boolean! 1415#   Test type of the Test version.16testType: TestType 1718#   Step definition of the Test version.19steps: [Step] 2021#   Unstructured definition of the Test version.22unstructured: String 2324#   Gherkin definition of the Test version.25gherkin: String 2627#   Gherkin type of the Test version.28#   Possible values: 'scenario' or 'scenario_outline'.29scenarioType: String 3031test: Test! 3233# Arguments34#   issueIds: the ids of the Preconditions.35#   limit: the maximum amount of Preconditions to be returned. The maximum is 100.36#   start: the index of the first item to return in the page of results (page offset).37preconditions(issueIds: [String], limit: Int!, start: Int): PreconditionResults 3839#   List of Test Executions associated with the Test version.40# 41# Arguments42#   issueIds: the issue ids of the Test Executions43#   limit: the maximum amount of Test Executions to be returned. The maximum is 100.44#   start: the index of the first item to return in the page of results (page offset).45testExecutions(issueIds: [String], limit: Int!, start: Int): TestExecutionResults 4647# Arguments48#   limit: the maximum amount of Test Runs to be returned. The maximum is 100.49#   start: the index of the first item to return in the page of results (page offset).50testRuns(limit: Int!, start: Int): TestRunResults 5152#   Date when the Test version was last modified.53lastModified: String 5455}`
## linkRequired by
 - TestRunTest Run typeTestVersionResultsTest version results type