# Xray GraphQL API Postman Collection (Vault-Secured)

This is a security-enhanced version of the Xray GraphQL API Postman collection that uses Postman Vault for secure credential storage.

## 🔒 Security Features

- **Encrypted Credential Storage**: All sensitive data stored in Postman Vault
- **No Exposed Secrets**: Credentials and tokens never appear in collection variables
- **Export-Safe**: Vault contents are never included when exporting/sharing
- **Automatic Token Management**: Tokens are injected at request time from vault
- **User-Friendly Error Handling**: Clear popup instructions for setup issues

## 📋 Prerequisites

- Postman v10.17 or later (Vault support required)
- Xray API credentials (Client ID and Secret)

## 🚀 Setup Instructions

### 1. Enable Vault Script Access

**This is required for the collection to work!**

1. Click the 🔒 **Vault** icon in Postman's bottom bar
2. Click the ⚙️ **Settings** icon in the vault window
3. Toggle **ON** the "Enable support in scripts" option
4. Close the settings

### 2. Add Your Credentials to Vault

1. In the Vault window, click **Add new**
2. Add these two secrets:
   - **Key**: `Xray_Client_Id`  
     **Value**: Your Xray API client ID
   - **Key**: `Xray_Client_Secret`  
     **Value**: Your Xray API client secret
3. Save and close the vault

> 💡 Get these credentials from Xray Global Settings → API Keys

### 3. Import the Collection

1. Click **Import** in Postman
2. Select `xray-postman-collection-vault.json`
3. Click **Import**

### 4. Authenticate

1. Navigate to **0. Authentication** → **Get JWT Token**
2. Send the request
3. You should see a green success message
4. The token is now securely stored in vault as `Xray_Token`

## 📁 Collection Structure

The collection is organized into categories:

```
Xray GraphQL API/
├── 0. Authentication/
│   └── Get JWT Token (uses vault:Xray_Client_Id & vault:Xray_Client_Secret)
├── 1. Queries - Tests/
├── 1. Queries - Folders/
├── 1. Queries - Test Executions/
├── 1. Queries - Test Plans/
├── 1. Queries - Test Sets/
├── 1. Queries - Test Runs/
├── 2. Mutations - Tests/
├── 2. Mutations - Folders/
├── 2. Mutations - Test Steps/
└── ... (more categories)
```

## 🎯 Usage

### Running Queries/Mutations

1. **First Time**: Run the authentication request
2. **Select a Request**: Browse the folders and choose an operation
3. **Edit Variables**: Modify the GraphQL variables as needed
4. **Send**: The token is automatically injected from vault

### Example: Get a Test

1. Go to **1. Queries - Tests** → **getTest**
2. In the Variables section, update:
   ```json
   {
     "issueId": "YOUR-TEST-ID"
   }
   ```
3. Click **Send**

## 🚨 Error Handling

The collection includes helpful error popups for common issues:

### "🔒 Vault Access Required"
- You need to enable vault script access (see Setup step 1)

### "🔑 Missing Credentials"
- Add your Client ID and Secret to vault (see Setup step 2)

### "⚠️ Authentication Required"
- Run the authentication request first
- Your token may have expired (24 hours)

### "🔐 Authentication Failed"
- Check your credentials are correct
- Ensure your API key is active in Xray

## 🔄 Token Management

- **Automatic Storage**: Tokens are saved to vault after authentication
- **Automatic Injection**: Tokens are added to requests automatically
- **Expiration**: Tokens expire after 24 hours
- **Re-authentication**: Just run the auth request again when needed

## 📊 GraphQL Variables

All requests use Postman's GraphQL mode:
- **Query**: The GraphQL query/mutation (pre-filled)
- **Variables**: JSON object with your input values

You can use Postman variables in the Variables section:
```json
{
  "projectId": "{{project_id}}",
  "path": "/{{folder_name}}"
}
```

## 🛡️ Security Best Practices

1. **Never share your vault contents**
2. **Don't add secrets to collection/environment variables**
3. **Export collections without vault data**
4. **Rotate your API credentials regularly**
5. **Use separate credentials for different environments**

## 🐛 Troubleshooting

### Scripts Can't Access Vault
1. Ensure Postman is v10.17 or later
2. Enable "Support in scripts" in vault settings
3. Restart Postman if needed

### Authentication Keeps Failing
1. Verify credentials in vault are correct
2. Check API key is enabled in Xray
3. Look at the response for specific error messages

### Token Not Found
1. Run the authentication request
2. Check the console for error messages
3. Verify the token was saved (you'll see a success popup)

## 📝 Notes

- The collection uses popup visualizers for better error messages
- All sensitive data is kept in vault only
- Collection variables only store non-sensitive data like URLs
- Each request has appropriate error handling

## 🔄 Updating the Collection

To regenerate with the latest schema:
1. Set environment variables: `XRAY_CLIENT` and `XRAY_SECRET`
2. Run: `python3 graphql_introspection.py`
3. Run: `python3 generate_postman_collection.py`
4. Run: `python3 enhance_postman_collection_vault.py`

---

**Security Note**: This collection follows Postman's security best practices by using Vault for all sensitive data. Your credentials and tokens are encrypted and never included in exports.