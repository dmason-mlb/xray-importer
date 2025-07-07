# addTestEnvironmentsToTestExecution

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/addtestenvironmentstotestexecution.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    addTestEnvironmentsToTestExecution(
        issueId: "12345",
        testEnvironments: ["android", "ios"]
    ) {
        associatedTestEnvironments
        createdTestEnvironments
        warning
    }
}

```

## Example

The mutation below will add the test Environments "android" and "ios" to the Test execution "12345".

```

mutation {
    addTestEnvironmentsToTestExecution(
        issueId: "12345",
        testEnvironments: ["android", "ios"]
    ) {
        associatedTestEnvironments
        createdTestEnvironments
        warning
    }
}

```