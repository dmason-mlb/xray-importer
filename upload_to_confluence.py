import requests
import json
import os

# Confluence API configuration
CONFLUENCE_BASE_URL = "https://baseball.atlassian.net/wiki"
PAGE_ID = "4932862074"

def read_markdown_file():
    """Read the markdown content from the file"""
    with open('xray_test_steps_review.md', 'r') as f:
        return f.read()

def convert_markdown_to_confluence(markdown_content):
    """Convert markdown to Confluence wiki markup"""
    # Replace markdown headers with Confluence headers
    content = markdown_content
    content = content.replace('### ', 'h3. ')
    content = content.replace('## ', 'h2. ')
    content = content.replace('# ', 'h1. ')
    
    # Replace markdown bold with Confluence bold
    content = content.replace('**', '*')
    
    # Replace markdown links [text](url) with Confluence links [text|url]
    import re
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    content = re.sub(link_pattern, r'[\1|\2]', content)
    
    # Replace checkbox markdown with Confluence task lists
    content = content.replace('- [ ] ', '[] ')
    content = content.replace('- [x] ', '[x] ')
    
    # Replace horizontal rules
    content = content.replace('---', '----')
    
    # Handle bullet points (already in correct format)
    
    return content

def get_auth_token():
    """Get authentication token from environment or prompt user"""
    # First check environment variable
    token = os.environ.get('CONFLUENCE_TOKEN')
    if token:
        return token
    
    # Otherwise prompt user
    print("Please provide your Confluence API token:")
    print("You can generate one at: https://id.atlassian.com/manage-profile/security/api-tokens")
    return input("API Token: ").strip()

def get_user_email():
    """Get user email from environment or prompt user"""
    email = os.environ.get('CONFLUENCE_EMAIL')
    if email:
        return email
    
    return input("Confluence Email: ").strip()

def update_confluence_page(page_id, title, content, email, token):
    """Update Confluence page with new content"""
    # Get current page version
    url = f"{CONFLUENCE_BASE_URL}/rest/api/content/{page_id}?expand=version"
    
    auth = (email, token)
    
    response = requests.get(url, auth=auth)
    if response.status_code != 200:
        print(f"Error getting page: {response.status_code}")
        print(response.text)
        return False
    
    page_data = response.json()
    current_version = page_data['version']['number']
    
    # Update page
    update_url = f"{CONFLUENCE_BASE_URL}/rest/api/content/{page_id}"
    
    update_data = {
        "id": page_id,
        "type": "page",
        "title": title,
        "space": {"key": page_data['space']['key']},
        "body": {
            "storage": {
                "value": content,
                "representation": "wiki"
            }
        },
        "version": {
            "number": current_version + 1,
            "message": "Updated XRAY test steps review document"
        }
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    response = requests.put(
        update_url, 
        data=json.dumps(update_data), 
        headers=headers,
        auth=auth
    )
    
    if response.status_code == 200:
        print(f"Successfully updated Confluence page: {PAGE_ID}")
        print(f"View at: {CONFLUENCE_BASE_URL}/pages/viewpage.action?pageId={PAGE_ID}")
        return True
    else:
        print(f"Error updating page: {response.status_code}")
        print(response.text)
        return False

def main():
    """Main function to upload content to Confluence"""
    print("Reading markdown file...")
    markdown_content = read_markdown_file()
    
    print("Converting to Confluence wiki markup...")
    confluence_content = convert_markdown_to_confluence(markdown_content)
    
    print("\nConfluence Authentication Required")
    print("-" * 40)
    email = get_user_email()
    token = get_auth_token()
    
    print("\nUploading to Confluence...")
    title = "XRAY Test Steps Review Document"
    
    success = update_confluence_page(PAGE_ID, title, confluence_content, email, token)
    
    if success:
        print("\n✅ Upload completed successfully!")
    else:
        print("\n❌ Upload failed. Please check your credentials and try again.")

if __name__ == "__main__":
    main()