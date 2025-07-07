# removeTestExecutionsFromTest

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/removetestexecutionsfromtest.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    removeTestExecutionsFromTest(issueId: "12345", testExecIssueIds: ["54321", "67890"])
}

```

## Example

The mutation below will remove the Test Executions with issue id "54321" and "67890" from the Test "12345".

```

mutation {
    removeTestExecutionsFromTest(issueId: "12345", testExecIssueIds: ["54321", "67890"])
}

```