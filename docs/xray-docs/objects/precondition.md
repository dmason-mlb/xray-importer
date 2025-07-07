# Precondition

**Category:** Objects
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/precondition.doc.html

*menu* Types OBJECT
 # Precondition
 Precondition issue type

## linkGraphQL Schema definition
 `1type Precondition {23#   Id of the Precondition issue.4issueId: String 56#   Project id of the Precondition issue.7projectId: String 89#   Precondition Type of the Precondition issue.10preconditionType: TestType 1112#   Definition of the Precondition issue.13definition: String 1415#   List of the Tests associated with the Precondition issue.16# 17# Arguments18#   issueIds: the issue ids of the Tests.19#   limit: the maximum amount of Tests to be returned. The maximum is 100.20#   start: the index of the first item to return in the page of results (page offset).21tests(issueIds: [String], limit: Int!, start: Int): TestResults 2223#   List of the Test versions associated with the Precondition issue.24# 25# Arguments26#   limit: the maximum amount of Test versions to be returned. The maximum is 100.27#   start: the index of the first item to return in the page of results (page offset).28#   archived: if should include archived Test versions in the result.29#   testTypeId: to filter Test versions by Test Type30testVersions(limit: Int!, start: Int, archived: Boolean, testTypeId: String): TestVersionResults 3132#   List of Xray History results for the issue33# 34# Arguments35#   limit: the maximum amount of entries to be returned. The maximum is 100.36#   start: the index of the first item to return in the page of results (page offset).37history(limit: Int!, start: Int): XrayHistoryResults 3839#   Extra Jira information of the Precondition Issue.40# 41# Arguments42#   fields: list of the fields to be displayed.43#   Check the field 'fields' of this Jira endpoint for more information.44jira(fields: [String]): JSON 4546#   Date when the precondition was last modified.47lastModified: String 4849#   Test Repository folder of the Precondition.50folder: Folder 5152}`
## linkRequired by
 - CreatePreconditionResultCreate Precondition Response typegetPreconditionnullMutationnullPreconditionResultsPrecondition Results typeQuerynullTestRunPreconditionTest Run Precondition typeupdatePreconditionnull