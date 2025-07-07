# removeTestEnvironmentsFromTestExecution

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/removetestenvironmentsfromtestexecution.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    removeTestEnvironmentsFromTestExecution(
        issueId: "12345",
        testEnvironments: ["android", "ios"]
    )
}

```

## Example

The mutation below will remoive the Test Environments "android" and "ios" from the Test execution "12345".

```

mutation {
    removeTestEnvironmentsFromTestExecution(
        issueId: "12345",
        testEnvironments: ["android", "ios"]
    )
}

```