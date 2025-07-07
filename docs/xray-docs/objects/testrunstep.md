# TestRunStep

**Category:** Objects
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/testrunstep.doc.html

*menu* Types OBJECT
 # TestRunStep
 Test Run Step Type

## linkGraphQL Schema definition
 `1type TestRunStep {23#   Id of the Test Run Step.4id: String 56#   Status of the Test Run Step.7status: StepStatus 89#   Action of the Test Run Step.10action: String 1112#   Data of the Test Run Step.13data: String 1415#   Result of the Test Run Step.16result: String 1718#   Custom Fields of the Test Run Step.19customFields: [TestRunCustomStepField] 2021#   Comment of the Test Run Step.22comment: String 2324#   Evidence of the Test Run Step.25evidence: [Evidence] 2627#   Attachments of the Test Run Step.28attachments: [Attachment] 2930#   Defects of the Test Run Step.31defects: [String] 3233#   Actual Result of the Test Run Step.34actualResult: String 3536}`
## linkRequired by
 - TestRunTest Run type