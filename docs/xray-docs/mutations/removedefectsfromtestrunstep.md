# removeDefectsFromTestRunStep

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/removedefectsfromtestrunstep.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    removeDefectsFromTestRunStep(
        testRunId: "5e8489c05f200f3cd45bbaf0",
        stepId: "316eb258-10bb-40c0-ae40-ab76004cc505",
        issues: ["XRAY-1234", "12345"]
    ) {
        removedDefects
        warnings
    }
}

```

## Example

The mutation below removes 2 defects from the Test Run.

```

mutation {
    removeDefectsFromTestRunStep(
        testRunId: "5e8489c05f200f3cd45bbaf0",
        stepId: "316eb258-10bb-40c0-ae40-ab76004cc505",
        issues: ["XRAY-1234", "12345"]
    ) {
        removedDefects
        warnings
    }
}

```