#!/bin/bash

# Script to remove exposed XRAY credentials from git history
# This script provides two methods: BFG (recommended) and git filter-branch

echo "=========================================="
echo "XRAY Credentials Security Remediation Script"
echo "=========================================="
echo ""
echo "WARNING: This will rewrite git history!"
echo "Make sure you have:"
echo "1. Committed all pending changes"
echo "2. Notified your team about the history rewrite"
echo "3. A backup of your repository"
echo ""
read -p "Do you want to continue? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

# Create a file with the secrets to remove
cat > secrets.txt << 'EOF'
6F50E2F905F54387AE31CFD9C912BFB0
7182cbb2529baf5cb0f71854f5b0e71692683c92ee6c8e5ce6fbbdde478dfc14
EOF

echo ""
echo "Choose your method:"
echo "1. BFG Repo-Cleaner (faster, recommended if you have Java)"
echo "2. git filter-branch (slower, but works everywhere)"
read -p "Enter choice (1 or 2): " method

if [ "$method" = "1" ]; then
    echo ""
    echo "Using BFG Repo-Cleaner method..."
    echo ""
    echo "If you don't have BFG installed, download it from:"
    echo "https://rtyley.github.io/bfg-repo-cleaner/"
    echo ""
    echo "Run these commands:"
    echo ""
    echo "# Download BFG if needed:"
    echo "wget https://repo1.maven.org/maven2/com/madgag/bfg/1.14.0/bfg-1.14.0.jar"
    echo ""
    echo "# Run BFG to remove secrets:"
    echo "java -jar bfg-1.14.0.jar --replace-text secrets.txt"
    echo ""
    echo "# Clean up the repository:"
    echo "git reflog expire --expire=now --all && git gc --prune=now --aggressive"
    echo ""
    echo "# Force push to remote (BE CAREFUL!):"
    echo "git push origin --force --all"
    echo "git push origin --force --tags"
    
elif [ "$method" = "2" ]; then
    echo ""
    echo "Using git filter-branch method..."
    echo "This will take a while..."
    echo ""
    
    # Remove credentials from all files
    git filter-branch --force --index-filter \
        'git ls-files -z | xargs -0 sed -i.bak \
        -e "s/6F50E2F905F54387AE31CFD9C912BFB0/XRAY_CLIENT_ID_REMOVED/g" \
        -e "s/7182cbb2529baf5cb0f71854f5b0e71692683c92ee6c8e5ce6fbbdde478dfc14/XRAY_CLIENT_SECRET_REMOVED/g" \
        && git add -A' \
        --prune-empty --tag-name-filter cat -- --all
    
    echo ""
    echo "Cleaning up..."
    git for-each-ref --format="delete %(refname)" refs/original | git update-ref --stdin
    git reflog expire --expire=now --all
    git gc --prune=now --aggressive
    
    echo ""
    echo "Done! Now force push to remote:"
    echo "git push origin --force --all"
    echo "git push origin --force --tags"
else
    echo "Invalid choice. Exiting."
    rm secrets.txt
    exit 1
fi

echo ""
echo "=========================================="
echo "IMPORTANT POST-CLEANUP STEPS:"
echo "=========================================="
echo "1. Immediately rotate/regenerate your XRAY credentials"
echo "2. Update the new credentials in your .env file"
echo "3. Notify all team members to re-clone the repository"
echo "4. Delete and re-fork any forks of this repository"
echo "5. Contact GitHub support to remove cached views if this is a public repo"
echo ""
echo "Remember: The old credentials may still exist in:"
echo "- Local clones that haven't been updated"
echo "- Forks of the repository"
echo "- GitHub's cache (for public repos)"
echo "- CI/CD logs or artifacts"
echo ""

# Clean up
rm -f secrets.txt