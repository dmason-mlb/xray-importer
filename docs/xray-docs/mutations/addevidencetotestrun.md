# addEvidenceToTestRun

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/addevidencetotestrun.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    addEvidenceToTestRun(
        id: "5acc7ab0a3fe1b6fcdc3c737",
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

The mutation below adds an evidence to the Test Run.

```

mutation {
    addEvidenceToTestRun(
        id: "5acc7ab0a3fe1b6fcdc3c737",
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