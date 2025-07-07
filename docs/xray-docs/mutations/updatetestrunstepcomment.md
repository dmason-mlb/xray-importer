# updateTestRunStepComment

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/updatetestrunstepcomment.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    updateTestRunStepComment(
        testRunId: "5e8489c05f200f3cd45bbaf0",
        stepId: "316eb258-10bb-40c0-ae40-ab76004cc505",
        comment: "This step is OK."
    )
}

```

## Example

The mutation below updates the comment of a Test Run Step.

```

mutation {
    updateTestRunStepComment(
        testRunId: "5e8489c05f200f3cd45bbaf0",
        stepId: "316eb258-10bb-40c0-ae40-ab76004cc505",
        comment: "This step is OK."
    )
}

```