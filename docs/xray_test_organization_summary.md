# XRAY Test Organization Summary

## Overview
The 1,414 imported test cases can be organized into folders using the **Test Repository Path** custom field in JIRA/XRAY.

## Discovered Custom Field
- **Field ID**: `customfield_22975`
- **Field Name**: Test Repo
- **Purpose**: Organizes tests into hierarchical folder structure in XRAY

## Proposed Folder Structure

Based on analysis of the test titles and CSV section data, tests will be organized into:

### Top Level: `/MLBAPP Test Repository/`

### Main Categories:
1. **Home Surface** (~450 tests)
   - Advertising
   - Analytics
   - Video
   - Surface Configuration
   - Player Features
   - Team Snapshot
   - Stories
   - Mixed Feed
   - Accessibility
   - Headline Stack
   - Content Carousel
   - Gameday Mini Module
   - Standings

2. **News Surface** (~300 tests)
   - Video
   - Stories
   - Carousel (large/medium/small)
   - Headline Stack
   - News Rebuild
   - Analytics
   - Authentication
   - Accessibility
   - Surface Configuration
   - Bilingual Support

3. **Core App** (~664 tests)
   - Authentication
   - Advertising
   - Onboarding
   - Player Features
   - Sanity Tests
   - Accessibility
   - Standings
   - Live Activities
   - Notifications
   - Video
   - Settings
   - Scoreboard
   - Passwordless Login
   - Japanese Language Support

## Organization Logic

Tests are categorized based on:
1. **Section data from CSV**: Primary surface (Home/News/Core)
2. **Title keywords**: Feature areas (e.g., "analytics", "video", "authentication")
3. **Hierarchical structure**: Up to 3-4 levels deep for better organization

## Command to Execute Organization

```bash
# Set environment variables
export JIRA_EMAIL="douglas.mason@mlb.com"
export JIRA_BASE_URL="https://baseball.atlassian.net"
export ATLASSIAN_TOKEN="[YOUR_TOKEN]"

# Run organization script
python3 organize_xray_tests.py \
  --custom-field customfield_22975 \
  import_data/home_surface_prepared.csv \
  import_data/mlbapp_prepared.csv \
  import_data/news_surface_prepared.csv
```

## Benefits

1. **Improved Navigation**: Tests organized by feature area and surface
2. **Better Test Management**: Easy to find related tests
3. **Reporting**: Can generate reports by folder/feature area
4. **Team Organization**: Different teams can focus on their areas
5. **Test Planning**: Easier to identify test coverage gaps

## Next Steps

1. Run the organization script to update all tests
2. Review the folder structure in XRAY Test Repository
3. Adjust folder names/structure as needed
4. Set up test execution plans based on folders
5. Configure permissions/access by folder if needed

## Notes

- The script will update ~1,400 tests with rate limiting (0.5s between updates)
- Estimated time: ~12 minutes to complete
- Tests already with a repository path will be skipped
- All changes are logged for audit purposes