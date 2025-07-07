# updateTestType

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/updatetesttype.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    updateTestType(issueId: "12345", testType: {name: "Manual"} ) {
        issueId
        testType {
            name
            kind
        }
    }
}

```

## Example

The mutation below will update the Test Type of the Test with id "12345".

```

mutation {
    updateTestType(issueId: "12345", testType: {name: "Manual"} ) {
        issueId
        testType {
            name
            kind
        }
    }
}

```

The mutation below will update the Test Type of the version 3 of the Test with id "12345".

```

mutation {
    updateTestType(issueId: "12345", versionId: 3, testType: {name: "Manual"} ) {
        issueId
        testType {
            name
            kind
        }
    }
}

```