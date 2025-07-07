# TestRunIterationStepResult

**Category:** Objects
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/testruniterationstepresult.doc.html

*menu* Types OBJECT
 # TestRunIterationStepResult
 Test Run iteration step result type

## linkGraphQL Schema definition
 `1type TestRunIterationStepResult {23#   Id of the Test Run step.4id: String 56#   Status of the Test Run step.7status: StepStatus 89#   Comment of the Test Run step.10comment: String 1112#   Evidence of the Test Run step.13evidence: [Evidence] 1415#   Defects of the Test Run step.16defects: [String] 1718#   Actual Result of the Test Run step.19actualResult: String 2021}`
## linkRequired by
 - TestRunIterationStepResultsTest Run iteration step results results type