# DatasetRow

**Category:** Objects
**Source:** https://us.xray.cloud.getxray.app/doc/graphql/datasetrow.doc.html

*menu* Types OBJECT
 # DatasetRow
 DatasetRow type
Represents a single row in the Dataset, containing combinatorial data.

## linkGraphQL Schema definition
 `1type DatasetRow {23#   The order of the row in the Dataset.4order: Int 56#   The values of the row, stored String array.7Values: [String] 89}`
## linkRequired by
 - DatasetDataset type
Represents a single Dataset entity with its metadata, parameters, and associated dataset rows.