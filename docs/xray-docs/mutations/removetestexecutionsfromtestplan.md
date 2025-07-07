# removeTestExecutionsFromTestPlan

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/removetestexecutionsfromtestplan.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    removeTestExecutionsFromTestPlan(issueId: "12345", testExecIssueIds: ["54321", "67890"])
}

```

## Example

The mutation below will remove the Test executions with issue id "54321" and "67890" from the Test Plan "12345".

```

mutation {
    removeTestExecutionsFromTestPlan(issueId: "12345", testExecIssueIds: ["54321", "67890"])
}

```