# addEvidenceToTestRunStep

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/addevidencetotestrunstep.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    addEvidenceToTestRunStep(
        testRunId: "5e8489c05f200f3cd45bbaf0",
        stepId: "316eb258-10bb-40c0-ae40-ab76004cc505",
        evidence: [
            {
                filename: "evidence.txt"
                mimeType: "text/plain"
                data: "SGVsbG8gV29ybGQ="
            }
        ]
    ) {
        addedEvidence
        warnings
    }
}

```

## Example

The mutation below adds an evidence to the Test Run Step.

```

mutation {
    addEvidenceToTestRunStep(
        testRunId: "5e8489c05f200f3cd45bbaf0",
        stepId: "316eb258-10bb-40c0-ae40-ab76004cc505",
        evidence: [
            {
                filename: "evidence.txt"
                mimeType: "text/plain"
                data: "SGVsbG8gV29ybGQ="
            }
        ]
    ) {
        addedEvidence
        warnings
    }
}

```