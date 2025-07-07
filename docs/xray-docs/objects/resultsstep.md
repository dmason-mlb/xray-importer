# ResultsStep

**Category:** Objects
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/resultsstep.doc.html

*menu* Types OBJECT
 # ResultsStep
 Results Step

## linkGraphQL Schema definition
 `1type ResultsStep {23#   If a gherkin step, keyword of the gherkin step.4keyword: String 56#   Name of the step.7name: String 89#   Embeddings of the step.10embeddings: [ResultsEmbedding] 1112#   Duration of the step.13duration: Float 1415#   Error of the step.16error: String 1718#   Status of the step.19status: StepStatus 2021#   If a Robot step, output of the Robot step.22log: String 2324}`
## linkRequired by
 - ResultResult TypeResultsExampleResults Example Type