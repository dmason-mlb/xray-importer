# TestRunIteration

**Category:** Objects
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/testruniteration.doc.html

*menu* Types OBJECT
 # TestRunIteration
 Test Run iteration type

## linkGraphQL Schema definition
 `1type TestRunIteration {23#   Rank of the iteration.4rank: String 56#   Parameters of the iteration.7parameters: [TestRunParameter] 89#   Status of the iteration.10status: StepStatus 1112#   Step results of the iteration.13# 14# Arguments15#   limit: the maximum amount of step results to be returned. The maximum is 100.16#   start: the index of the first item to return in the page of results (page offset).17stepResults(limit: Int!, start: Int): TestRunIterationStepResults 1819}`
## linkRequired by
 - TestRunIterationResultsTest Run iterations results type