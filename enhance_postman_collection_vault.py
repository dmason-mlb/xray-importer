#!/usr/bin/env python3
"""
Enhance the Postman collection with Vault support for secure secret storage
"""

import json

def enhance_collection():
    # Load the generated collection
    with open("xray-postman-collection.json", "r") as f:
        collection = json.load(f)
    
    # Add collection-level pre-request script for all GraphQL requests
    collection["event"] = [
        {
            "listen": "prerequest",
            "script": {
                "type": "text/javascript",
                "exec": [
                    "// Only run for GraphQL requests (skip authentication)",
                    "if (pm.request.url.getPath().includes('/graphql')) {",
                    "    // Attempt to get token from vault",
                    "    pm.vault.get('Xray_Token')",
                    "        .then((token) => {",
                    "            if (token) {",
                    "                // Set the Authorization header",
                    "                pm.request.headers.add({",
                    "                    key: 'Authorization',",
                    "                    value: `Bearer ${token}`",
                    "                });",
                    "                console.log('✅ Using Xray token from vault');",
                    "            } else {",
                    "                // No token found",
                    "                console.error('❌ No Xray token found in vault');",
                    "                pm.execution.setNextRequest(null); // Stop execution",
                    "                ",
                    "                // Show popup with instructions",
                    "                pm.visualizer.set(`",
                    "                    <div style='font-family: Arial, sans-serif; padding: 20px; max-width: 600px; margin: 0 auto;'>",
                    "                        <h2 style='color: #d73502;'>⚠️ Authentication Required</h2>",
                    "                        <p>No authentication token found. Please follow these steps:</p>",
                    "                        <ol>",
                    "                            <li><strong>Run the Authentication Request:</strong>",
                    "                                <ul>",
                    "                                    <li>Go to '0. Authentication' → 'Get JWT Token'</li>",
                    "                                    <li>Make sure your Vault contains:</li>",
                    "                                    <li style='margin-left: 20px;'><code>Xray_Client_Id</code> - Your client ID</li>",
                    "                                    <li style='margin-left: 20px;'><code>Xray_Client_Secret</code> - Your client secret</li>",
                    "                                    <li>Send the request</li>",
                    "                                </ul>",
                    "                            </li>",
                    "                            <li><strong>The token will be automatically saved to Vault</strong></li>",
                    "                            <li><strong>Retry this request</strong></li>",
                    "                        </ol>",
                    "                        <p style='background: #f0f0f0; padding: 10px; border-radius: 5px;'>",
                    "                            <strong>Note:</strong> Tokens expire after 24 hours. Re-authenticate when needed.",
                    "                        </p>",
                    "                    </div>",
                    "                `);",
                    "            }",
                    "        })",
                    "        .catch((error) => {",
                    "            console.error('❌ Vault access error:', error);",
                    "            pm.execution.setNextRequest(null); // Stop execution",
                    "            ",
                    "            // Show popup with vault setup instructions",
                    "            pm.visualizer.set(`",
                    "                <div style='font-family: Arial, sans-serif; padding: 20px; max-width: 600px; margin: 0 auto;'>",
                    "                    <h2 style='color: #d73502;'>🔒 Vault Access Required</h2>",
                    "                    <p>The script cannot access Postman Vault. Please enable vault access:</p>",
                    "                    <ol>",
                    "                        <li><strong>Open Postman Vault:</strong> Click the 🔒 icon in the bottom bar</li>",
                    "                        <li><strong>Go to Settings:</strong> Click the ⚙️ gear icon in the vault</li>",
                    "                        <li><strong>Enable Script Access:</strong> Toggle ON 'Enable support in scripts'</li>",
                    "                        <li><strong>Add Your Credentials:</strong>",
                    "                            <ul>",
                    "                                <li>Add <code>Xray_Client_Id</code> with your client ID</li>",
                    "                                <li>Add <code>Xray_Client_Secret</code> with your client secret</li>",
                    "                            </ul>",
                    "                        </li>",
                    "                        <li><strong>Retry the request</strong></li>",
                    "                    </ol>",
                    "                    <p style='background: #fffacd; padding: 10px; border-radius: 5px;'>",
                    "                        <strong>Security Note:</strong> Vault keeps your secrets encrypted and never exports them.",
                    "                    </p>",
                    "                </div>",
                    "            `);",
                    "        });",
                    "}"
                ]
            }
        },
        {
            "listen": "test",
            "script": {
                "type": "text/javascript",
                "exec": [
                    "// Check for authentication errors in GraphQL responses",
                    "if (pm.request.url.getPath().includes('/graphql')) {",
                    "    if (pm.response.code === 401 || pm.response.code === 403) {",
                    "        console.error('❌ Authentication failed');",
                    "        ",
                    "        // Show authentication required popup",
                    "        pm.visualizer.set(`",
                    "            <div style='font-family: Arial, sans-serif; padding: 20px; max-width: 600px; margin: 0 auto;'>",
                    "                <h2 style='color: #d73502;'>🔐 Authentication Failed</h2>",
                    "                <p>Your request was not authenticated. This usually means:</p>",
                    "                <ul>",
                    "                    <li>Your token has expired (tokens last 24 hours)</li>",
                    "                    <li>You haven't authenticated yet</li>",
                    "                    <li>Your credentials are incorrect</li>",
                    "                </ul>",
                    "                <h3>To fix this:</h3>",
                    "                <ol>",
                    "                    <li>Go to '0. Authentication' → 'Get JWT Token'</li>",
                    "                    <li>Ensure your Vault contains valid credentials</li>",
                    "                    <li>Send the authentication request</li>",
                    "                    <li>Retry this request</li>",
                    "                </ol>",
                    "            </div>",
                    "        `);",
                    "    }",
                    "}"
                ]
            }
        }
    ]
    
    # Find the authentication request and update it to use Vault
    for folder in collection["item"]:
        if folder["name"] == "0. Authentication":
            for item in folder["item"]:
                if item["name"] == "Get JWT Token":
                    # Update the request body to use vault variables
                    item["request"]["body"]["raw"] = "{\n  \"client_id\": \"{{vault:Xray_Client_Id}}\",\n  \"client_secret\": \"{{vault:Xray_Client_Secret}}\"\n}"
                    
                    # Add pre-request script to check vault access
                    if "event" not in item:
                        item["event"] = []
                    
                    item["event"].append({
                        "listen": "prerequest",
                        "script": {
                            "type": "text/javascript",
                            "exec": [
                                "// Check if we can access vault for credentials",
                                "Promise.all([",
                                "    pm.vault.get('Xray_Client_Id'),",
                                "    pm.vault.get('Xray_Client_Secret')",
                                "]).then(([clientId, clientSecret]) => {",
                                "    if (!clientId || !clientSecret) {",
                                "        console.error('❌ Missing credentials in vault');",
                                "        pm.execution.setNextRequest(null);",
                                "        ",
                                "        pm.visualizer.set(`",
                                "            <div style='font-family: Arial, sans-serif; padding: 20px; max-width: 600px; margin: 0 auto;'>",
                                "                <h2 style='color: #d73502;'>🔑 Missing Credentials</h2>",
                                "                <p>Please add your Xray API credentials to Postman Vault:</p>",
                                "                <ol>",
                                "                    <li>Click the 🔒 Vault icon in the bottom bar</li>",
                                "                    <li>Add these two secrets:",
                                "                        <ul>",
                                "                            <li><code>Xray_Client_Id</code> - Your API client ID</li>",
                                "                            <li><code>Xray_Client_Secret</code> - Your API client secret</li>",
                                "                        </ul>",
                                "                    </li>",
                                "                    <li>Save and close the vault</li>",
                                "                    <li>Retry this request</li>",
                                "                </ol>",
                                "                <p style='background: #e8f4f8; padding: 10px; border-radius: 5px;'>",
                                "                    You can get these credentials from your Xray Global Settings → API Keys",
                                "                </p>",
                                "            </div>",
                                "        `);",
                                "    } else {",
                                "        console.log('✅ Credentials found in vault');",
                                "    }",
                                "}).catch((error) => {",
                                "    console.error('❌ Cannot access vault:', error);",
                                "    pm.execution.setNextRequest(null);",
                                "    ",
                                "    pm.visualizer.set(`",
                                "        <div style='font-family: Arial, sans-serif; padding: 20px; max-width: 600px; margin: 0 auto;'>",
                                "            <h2 style='color: #d73502;'>🔒 Enable Vault Access</h2>",
                                "            <p>Scripts need permission to access Postman Vault:</p>",
                                "            <ol>",
                                "                <li>Click the 🔒 Vault icon in the bottom bar</li>",
                                "                <li>Click the ⚙️ Settings icon</li>",
                                "                <li>Toggle ON <strong>'Enable support in scripts'</strong></li>",
                                "                <li>Close settings and retry this request</li>",
                                "            </ol>",
                                "        </div>",
                                "    `);",
                                "});"
                            ]
                        }
                    })
                    
                    # Update test script to save token to vault
                    item["event"].append({
                        "listen": "test",
                        "script": {
                            "type": "text/javascript",
                            "exec": [
                                "// Save token to vault from authentication response",
                                "if (pm.response.code === 200) {",
                                "    try {",
                                "        // Get the response text (JWT token is returned as a quoted string)",
                                "        let responseText = pm.response.text();",
                                "        ",
                                "        // Remove quotes from the token if present",
                                "        let token = responseText.replace(/^\"|\"$/g, '');",
                                "        ",
                                "        // Validate that we have a token",
                                "        if (token && token.length > 0) {",
                                "            // Store the token in vault",
                                "            pm.vault.set('Xray_Token', token)",
                                "                .then(() => {",
                                "                    console.log('✅ Xray token successfully stored in vault');",
                                "                    ",
                                "                    // Calculate expiration time",
                                "                    const expirationTime = new Date();",
                                "                    expirationTime.setHours(expirationTime.getHours() + 24);",
                                "                    ",
                                "                    // Store expiration in collection variable (non-sensitive)",
                                "                    pm.collectionVariables.set('xray_token_expires', expirationTime.toISOString());",
                                "                    ",
                                "                    console.log('Token expires at:', expirationTime.toISOString());",
                                "                    ",
                                "                    pm.test('Authentication successful', function () {",
                                "                        pm.response.to.have.status(200);",
                                "                    });",
                                "                    ",
                                "                    // Show success message",
                                "                    pm.visualizer.set(`",
                                "                        <div style='font-family: Arial, sans-serif; padding: 20px; max-width: 600px; margin: 0 auto;'>",
                                "                            <h2 style='color: #28a745;'>✅ Authentication Successful</h2>",
                                "                            <p>Your token has been securely stored in Postman Vault.</p>",
                                "                            <p><strong>Token expires:</strong> ${expirationTime.toLocaleString()}</p>",
                                "                            <p style='background: #e8f8e8; padding: 10px; border-radius: 5px;'>",
                                "                                You can now run any GraphQL query or mutation!",
                                "                            </p>",
                                "                        </div>",
                                "                    `);",
                                "                })",
                                "                .catch((error) => {",
                                "                    console.error('❌ Failed to save token to vault:', error);",
                                "                    pm.test('Failed to save token to vault', function () {",
                                "                        pm.expect(error).to.be.null;",
                                "                    });",
                                "                });",
                                "        } else {",
                                "            console.error('❌ No token found in response');",
                                "            pm.test('Token extraction failed', function () {",
                                "                pm.expect(token).to.not.be.undefined;",
                                "            });",
                                "        }",
                                "    } catch (error) {",
                                "        console.error('❌ Error processing authentication response:', error);",
                                "    }",
                                "} else {",
                                "    // Authentication failed",
                                "    pm.test('Authentication failed', function () {",
                                "        pm.response.to.have.status(200);",
                                "    });",
                                "    ",
                                "    // Show error details",
                                "    let errorMessage = pm.response.text();",
                                "    pm.visualizer.set(`",
                                "        <div style='font-family: Arial, sans-serif; padding: 20px; max-width: 600px; margin: 0 auto;'>",
                                "            <h2 style='color: #d73502;'>❌ Authentication Failed</h2>",
                                "            <p><strong>Status:</strong> ${pm.response.code} ${pm.response.status}</p>",
                                "            <p><strong>Response:</strong></p>",
                                "            <pre style='background: #f5f5f5; padding: 10px; overflow: auto;'>${errorMessage}</pre>",
                                "            <h3>Common causes:</h3>",
                                "            <ul>",
                                "                <li>Invalid client ID or secret</li>",
                                "                <li>Expired API credentials</li>",
                                "                <li>API key not enabled in Xray</li>",
                                "            </ul>",
                                "        </div>",
                                "    `);",
                                "}"
                            ]
                        }
                    })
    
    # Update collection variables - remove sensitive ones, keep only non-sensitive
    collection["variable"] = [
        {
            "key": "base_url",
            "value": "https://xray.cloud.getxray.app/api/v2",
            "type": "string"
        },
        {
            "key": "project_id",
            "value": "26420",
            "type": "string",
            "description": "Default project ID (MLBMOB) - Update for your project"
        },
        {
            "key": "xray_token_expires",
            "value": "",
            "type": "string",
            "description": "Token expiration time (set automatically)"
        }
    ]
    
    # Remove auth from collection level since we're setting it per request
    if "auth" in collection:
        del collection["auth"]
    
    # Add collection description
    collection["info"]["description"] = """# Xray GraphQL API Collection (Vault-Secured)

This collection uses Postman Vault for secure storage of credentials and tokens.

## Setup Instructions

1. **Enable Vault Script Access**
   - Click the 🔒 Vault icon in Postman's bottom bar
   - Click ⚙️ Settings
   - Toggle ON "Enable support in scripts"

2. **Add Credentials to Vault**
   - In Vault, add these secrets:
     - `Xray_Client_Id` - Your Xray API client ID
     - `Xray_Client_Secret` - Your Xray API client secret
   - Get these from Xray Global Settings → API Keys

3. **Authenticate**
   - Run "0. Authentication" → "Get JWT Token"
   - The token will be saved to vault as `Xray_Token`
   - Tokens expire after 24 hours

## Security Features

- Credentials stored in encrypted Vault
- Tokens never exposed in collection variables
- Vault contents never exported
- Automatic token injection for requests
- Clear error messages with setup instructions

## Troubleshooting

If you see popups about vault access or authentication:
- Follow the instructions in the popup
- Ensure vault script access is enabled
- Check your credentials are correct
- Re-authenticate if token expired"""
    
    # Save enhanced collection
    with open("xray-postman-collection-vault.json", "w") as f:
        json.dump(collection, f, indent=2)
    
    print("Vault-secured Postman collection saved to xray-postman-collection-vault.json")

if __name__ == "__main__":
    enhance_collection()