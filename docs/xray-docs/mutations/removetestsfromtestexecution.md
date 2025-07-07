# removeTestsFromTestExecution

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/removetestsfromtestexecution.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    removeTestsFromTestExecution(issueId: "12345", testIssueIds: ["54321", "67890"])
}

```

## Example

The mutation below will remove the Tests with issue id "54321" and "67890" from the Test Execution "12345".

```

mutation {
    removeTestsFromTestExecution(issueId: "12345", testIssueIds: ["54321", "67890"])
}

```