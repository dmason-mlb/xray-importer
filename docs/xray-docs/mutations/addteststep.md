# addTestStep

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/addteststep.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    addTestStep(
        issueId: "12345",
        step: {
            action: "Use Xray Cloud Rest Api to add a new Step to the Test",
            result: "Step was added to the Test",
            customFields: [{id:"5ddc0e585da9670010e608dc", value:"Tokyo"}]
        }
    ) {
        id
        action
        data
        result
    }
}

```

## Example

The mutation below will add a new Step to the test with id "12345".

```

mutation {
    addTestStep(
        issueId: "12345",
        step: {
            action: "Use Xray Cloud Rest Api to add a new Step to the Test",
            result: "Step was added to the Test",
            customFields: [{id:"5ddc0e585da9670010e608dc", value:"Tokyo"}]
        }
    ) {
        id
        action
        data
        result
    }
}

```

The mutation below will add a new Step to the version 3 of the Test with id "12345".

```

mutation {
    addTestStep(
        issueId: "12345",
        versionId: 3,
        step: {
            action: "Use Xray Cloud Rest Api to add a new Step to the Test",
            result: "Step was added to the Test",
            customFields: [{id:"5ddc0e585da9670010e608dc", value:"Tokyo"}]
        }
    ) {
        id
        action
        data
        result
    }
}

```