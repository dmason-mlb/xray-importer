# updateUnstructuredTestDefinition

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/updateunstructuredtestdefinition.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    updateUnstructuredTestDefinition(issueId: "12345", unstructured: "Generic definition" ) {
        issueId
        unstructured
    }
}

```

## Example

The mutation below will update the unstructured definition of the Test with id "12345".

```

mutation {
    updateUnstructuredTestDefinition(issueId: "12345", unstructured: "Generic definition" ) {
        issueId
        unstructured
    }
}

```

The mutation below will update the unstructured definition of the version 3 of the Test with id "12345".

```

mutation {
    updateUnstructuredTestDefinition(issueId: "12345", versionId: 3, unstructured: "Generic definition" ) {
        issueId
        unstructured
    }
}

```