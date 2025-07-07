# updateTestRunStepStatus

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/updatetestrunstepstatus.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    updateTestRunStepStatus(
        testRunId: "5e8489c05f200f3cd45bbaf0",
        stepId: "316eb258-10bb-40c0-ae40-ab76004cc505",
        status: "PASSED"
    ) {
        warnings
    }
}

```

## Example

The mutation below updates the status of a Test Run Step.

```

mutation {
    updateTestRunStepStatus(
        testRunId: "5e8489c05f200f3cd45bbaf0",
        stepId: "316eb258-10bb-40c0-ae40-ab76004cc505",
        status: "PASSED"
    ) {
        warnings
    }
}

```