# addDefectsToTestRunStep

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/adddefectstotestrunstep.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    addDefectsToTestRunStep(
        testRunId: "5e8489c05f200f3cd45bbaf0",
        stepId: "316eb258-10bb-40c0-ae40-ab76004cc505",
        issues: ["XRAY-1234", "12345"]
    ) {
        addedDefects
        warnings
    }
}

```

## Example

The mutation below adds 2 defects to the Test Run Step.

```

mutation {
    addDefectsToTestRunStep(
        testRunId: "5e8489c05f200f3cd45bbaf0",
        stepId: "316eb258-10bb-40c0-ae40-ab76004cc505",
        issues: ["XRAY-1234", "12345"]
    ) {
        addedDefects
        warnings
    }
}

```