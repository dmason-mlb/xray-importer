#!/bin/bash

# Xray GraphQL Documentation Downloader
# This script downloads all remaining documentation pages

BASE_URL="https://us.xray.cloud.getxray.app/doc/graphql/"
TARGET_DIR="/Users/douglas.mason/Documents/GitHub/xray-importer/docs/xray-docs"

echo "Starting download of Xray GraphQL documentation..."
echo "Target directory: $TARGET_DIR"
echo "Base URL: $BASE_URL"
echo ""

# Create subdirectories for assets
mkdir -p "$TARGET_DIR/styles"
mkdir -p "$TARGET_DIR/assets"
mkdir -p "$TARGET_DIR/scripts"

# Function to download a file with error handling
download_file() {
    local url="$1"
    local filename="$2"
    local filepath="$TARGET_DIR/$filename"
    
    echo "Downloading: $filename"
    if curl -f -s -o "$filepath" "$BASE_URL$url"; then
        echo "✅ Success: $filename"
    else
        echo "❌ Failed: $filename"
    fi
    sleep 0.5  # Be respectful to the server
}

# Download remaining Query operations (25 remaining)
echo "=== Downloading Query Operations ==="
QUERY_URLS=(
    "gettests.doc.html"
    "getexpandedtest.doc.html"
    "getexpandedtests.doc.html"
    "getcoverableissue.doc.html"
    "getcoverableissues.doc.html"
    "getdataset.doc.html"
    "getdatasets.doc.html"
    "getprecondition.doc.html"
    "getpreconditions.doc.html"
    "gettestset.doc.html"
    "gettestsets.doc.html"
    "gettestplan.doc.html"
    "gettestplans.doc.html"
    "gettestexecution.doc.html"
    "gettestexecutions.doc.html"
    "gettestrun.doc.html"
    "gettestrunbyid.doc.html"
    "gettestruns.doc.html"
    "gettestrunsbyid.doc.html"
    "getstepstatus.doc.html"
    "getstatus.doc.html"
    "getstatuses.doc.html"
    "getstepstatuses.doc.html"
    "getprojectsettings.doc.html"
    "getissuelinktypes.doc.html"
)

for url in "${QUERY_URLS[@]}"; do
    download_file "$url" "$url"
done

# Download Mutation operations (68 URLs)
echo ""
echo "=== Downloading Mutation Operations ==="
MUTATION_URLS=(
    "createfolder.doc.html"
    "deletefolder.doc.html"
    "renamefolder.doc.html"
    "movefolder.doc.html"
    "addteststofolder.doc.html"
    "addissuestofolder.doc.html"
    "removetestsfromfolder.doc.html"
    "removeissuesfromfolder.doc.html"
    "createtest.doc.html"
    "updatetesttype.doc.html"
    "updateunstructuredtestdefinition.doc.html"
    "updategherkintestdefinition.doc.html"
    "deletetest.doc.html"
    "addteststep.doc.html"
    "updateteststep.doc.html"
    "removeteststep.doc.html"
    "removeallteststeps.doc.html"
    "addpreconditionstotest.doc.html"
    "removepreconditionsfromtest.doc.html"
    "updatetestfolder.doc.html"
    "updatepreconditionfolder.doc.html"
    "addtestsetstotest.doc.html"
    "removetestsetsfromtest.doc.html"
    "addtestplanstotest.doc.html"
    "removetestplansfromtest.doc.html"
    "addtestexecutionstotest.doc.html"
    "removetestexecutionsfromtest.doc.html"
    "createprecondition.doc.html"
    "updateprecondition.doc.html"
    "deleteprecondition.doc.html"
    "addteststoprecondition.doc.html"
    "removetestsfromprecondition.doc.html"
    "createtestset.doc.html"
    "deletetestset.doc.html"
    "addteststotestset.doc.html"
    "removetestsfromtestset.doc.html"
    "createtestplan.doc.html"
    "deletetestplan.doc.html"
    "addteststotestplan.doc.html"
    "removetestsfromtestplan.doc.html"
    "addtestexecutionstotestplan.doc.html"
    "removetestexecutionsfromtestplan.doc.html"
    "createtestexecution.doc.html"
    "deletetestexecution.doc.html"
    "addteststotestexecution.doc.html"
    "removetestsfromtestexecution.doc.html"
    "addtestenvironmentstotestexecution.doc.html"
    "removetestenvironmentsfromtestexecution.doc.html"
    "resettestrun.doc.html"
    "updatetestrunstatus.doc.html"
    "updatetestruncomment.doc.html"
    "updatetestrun.doc.html"
    "adddefectstotestrun.doc.html"
    "removedefectsfromtestrun.doc.html"
    "addevidencetotestrun.doc.html"
    "removeevidencefromtestrun.doc.html"
    "updatetestrunstep.doc.html"
    "addevidencetotestrunstep.doc.html"
    "removeevidencefromtestrunstep.doc.html"
    "adddefectstotestrunstep.doc.html"
    "removedefectsfromtestrunstep.doc.html"
    "updatetestrunstepcomment.doc.html"
    "updatetestrunstepstatus.doc.html"
    "updatetestrunexamplestatus.doc.html"
    "updateiterationstatus.doc.html"
    "settestruntimer.doc.html"
)

for url in "${MUTATION_URLS[@]}"; do
    download_file "$url" "$url"
done

# Download Scalars (5 URLs)
echo ""
echo "=== Downloading Scalars ==="
SCALAR_URLS=(
    "boolean.doc.html"
    "float.doc.html"
    "int.doc.html"
    "json.doc.html"
    "string.doc.html"
)

for url in "${SCALAR_URLS[@]}"; do
    download_file "$url" "$url"
done

# Download Enums (2 URLs)
echo ""
echo "=== Downloading Enums ==="
ENUM_URLS=(
    "directivelocation.spec.html"
    "typekind.spec.html"
)

for url in "${ENUM_URLS[@]}"; do
    download_file "$url" "$url"
done

echo ""
echo "=== Download Complete! ==="
echo "Check the target directory for all downloaded files."
echo "Don't forget to also download the CSS and JS assets if needed."
