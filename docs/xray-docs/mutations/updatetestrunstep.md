# updateTestRunStep

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/updatetestrunstep.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    updateTestRunStep(
        testRunId: "5e8489c05f200f3cd45bbaf0",
        stepId: "316eb258-10bb-40c0-ae40-ab76004cc505",
        updateData: {
            comment: "Step failed"
            status: "FAILED"
            defects: {
                add: ["12345"]
            }
        }
    ) {
        addedDefects
        warnings
    }
}

```

## Example

The mutation below will change the status, update the comment and add a defect to the Test Run Step.

```

mutation {
    updateTestRunStep(
        testRunId: "5e8489c05f200f3cd45bbaf0",
        stepId: "316eb258-10bb-40c0-ae40-ab76004cc505",
        updateData: {
            comment: "Step failed"
            status: "FAILED"
            defects: {
                add: ["12345"]
            }
        }
    ) {
        addedDefects
        warnings
    }
}

```