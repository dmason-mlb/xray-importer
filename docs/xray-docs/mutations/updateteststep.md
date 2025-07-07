# updateTestStep

**Category:** Mutations
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/updateteststep.doc.html

## GraphQL Schema Definition

```graphql

mutation {
    updateTestStep(
        stepId: "836d30ec-f034-4a03-879e-9c44a1d6d1fe",
        step: {
            result: "Xray Cloud Rest Api works as expected",
            customFields: [{id:"5ddc0e585da9670010e608dc", value:"Lisbon"}]
        }
    ) {
        warnings
    }
}

```

## Example

The mutation below will update the Step with id "836d30ec-f034-4a03-879e-9c44a1d6d1fe".

```

mutation {
    updateTestStep(
        stepId: "836d30ec-f034-4a03-879e-9c44a1d6d1fe",
        step: {
            result: "Xray Cloud Rest Api works as expected",
            customFields: [{id:"5ddc0e585da9670010e608dc", value:"Lisbon"}]
        }
    ) {
        warnings
    }
}

```