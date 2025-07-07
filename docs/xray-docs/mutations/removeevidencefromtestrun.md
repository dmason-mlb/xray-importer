# removeEvidenceFromTestRun

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/removeevidencefromtestrun.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    removeEvidenceFromTestRun(
        id: "5acc7ab0a3fe1b6fcdc3c737",
        evidenceFilenames: ["evidence.txt"]
    ) {
        removedEvidence
        warnings
    }
}

```

## Example

The mutation below removes an evidence from the Test Run.

```

mutation {
    removeEvidenceFromTestRun(
        id: "5acc7ab0a3fe1b6fcdc3c737",
        evidenceFilenames: ["evidence.txt"]
    ) {
        removedEvidence
        warnings
    }
}

```