# Step

**Category:** Objects
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/step.doc.html

*menu* Types OBJECT
 # Step
 Test Step type

## linkGraphQL Schema definition
 `1type Step {23#   Id of the Step.4id: String 56#   Action of the Step.7action: String 89#   Data of the Step.10data: String 1112#   Result of the Step.13result: String 1415#   Attachments of the Step.16attachments: [Attachment] 1718#   Custom Fields of the Step.19customFields: [CustomStepField] 2021#   The issue id of the test being called in the step.22callTestIssueId: String 2324}`
## linkRequired by
 - addTestStepnullMutationnullTestTest issue typeTestVersionnull