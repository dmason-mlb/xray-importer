# removeEvidenceFromTestRunStep

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/removeevidencefromtestrunstep.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    removeEvidenceFromTestRunStep(
        testRunId: "5e8489c05f200f3cd45bbaf0",
        stepId: "316eb258-10bb-40c0-ae40-ab76004cc505",
        evidenceFilenames: ["evidence.txt"]
    ) {
        removedEvidence
        warnings
    }
}

```

## Example

The mutation below removes an evidence from the Test Run Step.

```

mutation {
    removeEvidenceFromTestRunStep(
        testRunId: "5e8489c05f200f3cd45bbaf0",
        stepId: "316eb258-10bb-40c0-ae40-ab76004cc505",
        evidenceFilenames: ["evidence.txt"]
    ) {
        removedEvidence
        warnings
    }
}

```