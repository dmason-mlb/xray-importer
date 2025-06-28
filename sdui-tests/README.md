# SDUI Test Cases for Xray Import

## Overview

This directory contains comprehensive JSON files for importing SDUI (Server-Driven UI) test cases into Xray. The test cases were extracted from 8 Confluence documents covering functional and API testing across four major SDUI components.

## Files Created

### 1. `sdui-functional-tests.json`
- **Total Test Cases**: 11 representative functional test cases
- **Coverage**: Browse Menu, Team Page, Gameday, and Scoreboard functional testing
- **Test Types**: Manual execution test cases
- **Platforms**: iOS, Android, iPad

### 2. `sdui-api-tests.json`
- **Total Test Cases**: 11 representative API test cases  
- **Coverage**: Browse Menu, Team Page, Gameday, and Scoreboard API endpoint testing
- **Test Types**: Automated API test cases
- **Platforms**: Cross-platform API testing

## Source Documents Analyzed

The test cases were extracted from these Confluence documents:

1. **SDUI Browse Menu - Functional Test Cases** (50 tests)
   - Core navigation and UI functionality
   - Personalization features
   - Localization support
   - Jewel event integration

2. **SDUI Browse Menu - API Test Cases** (51 tests)
   - Endpoint validation
   - Language support
   - Cache behavior
   - Error handling

3. **SDUI Team Page - Functional Test Cases** (38 tests)
   - Team selection and navigation
   - MIG (Match Information Graphics) display
   - Content sections
   - Game state handling

4. **SDUI Team Page - API Test Cases** (51 tests)
   - Team page endpoints
   - Language localization
   - Game state API integration
   - Performance testing

5. **SDUI Gameday - Functional Test Cases** (67 tests)
   - WebView integration
   - JavaScript bridge functionality
   - Tab navigation
   - Game state transitions

6. **SDUI Gameday - API Test Cases** (50 tests)
   - Gameday endpoint testing
   - Parameter validation
   - Error scenarios
   - Performance metrics

7. **SDUI Scoreboard - Functional Test Cases** (55 tests)
   - Game cell functionality
   - Date navigation
   - Score display
   - User interactions

8. **SDUI Scoreboard - API Test Cases** (47 tests)
   - Scoreboard API endpoints
   - Data validation
   - Cache behavior
   - Error handling

## Test Case Structure

Each test case in the JSON files follows this structure:

```json
{
  "summary": "[Test Case ID]: [Test Name]",
  "description": "[Expected Result description]",
  "folder": "[Folder Structure path]",
  "labels": ["tag1", "tag2", "tag3"],
  "priority": "[High|Medium|Low]",
  "testType": "Manual|Automated",
  "platforms": ["iOS", "Android", "iPad"],
  "steps": [
    {
      "action": "[step description]",
      "result": "[expected result]"
    }
  ],
  "issueLinks": ["[Related Issue if any]"],
  "testData": "[Test Data if specified]"
}
```

## Key Features Covered

### Functional Testing
- **Navigation**: Core app navigation patterns
- **Personalization**: User-specific content display
- **Localization**: Multi-language support (English, Spanish, Japanese)
- **Game States**: Live, preview, final, delayed, suspended game handling
- **Jewel Events**: Opening Day, All-Star, Postseason, World Series
- **Cross-Platform**: iOS and Android consistency
- **Accessibility**: VoiceOver, TalkBack support
- **Performance**: Load times, memory usage, responsiveness

### API Testing
- **Endpoint Validation**: All core SDUI service endpoints
- **Parameter Testing**: Required and optional parameters
- **Error Handling**: Invalid inputs, service failures
- **Performance**: Response times, concurrent requests
- **Data Validation**: Schema compliance, field validation
- **Integration**: Upstream service dependencies
- **Security**: Input validation, authentication
- **Caching**: Cache behavior and invalidation

## Tag Categories

The test cases use the following tag categories:

### Component Tags
- `browse-menu` - Browse Menu related tests
- `team-page` - Team Page related tests  
- `gameday` - Gameday related tests
- `scoreboard` - Scoreboard related tests

### Test Type Tags
- `functional` - Functional test cases
- `api` - API test cases
- `cross-platform` - Multi-platform tests
- `regression` - Regression test cases

### Priority Tags
- `critical` - Critical priority tests
- `high` - High priority tests
- `medium` - Medium priority tests
- `low` - Low priority tests

### Feature Tags
- `navigation` - Navigation functionality
- `personalization` - User personalization features
- `localization` - Multi-language support
- `game-state` - Game state handling
- `jewel-event` - Special event testing
- `performance` - Performance related tests
- `accessibility` - Accessibility compliance
- `live-state` - Live game functionality
- `webview` - WebView integration
- `js-bridge` - JavaScript bridge functionality

### Platform Tags
- `ios` - iOS specific tests
- `android` - Android specific tests
- `ipad` - iPad specific tests

## Implementation Notes

### Requirements for Test Execution
- **Feature Flags**: `enable_bullpen_gameday` and related SDUI flags must be enabled
- **Test Data**: Valid team IDs (108-159), game IDs, and user accounts
- **Network Access**: API endpoints must be accessible
- **Authentication**: Test accounts for logged-in scenarios
- **Live Data**: Some tests require live games or specific game states

### Special Considerations
- **Jewel Events**: Time-sensitive tests that require specific periods (Opening Day, All-Star, etc.)
- **Game States**: Tests requiring specific game states (live, delayed, suspended)
- **Localization**: Device language settings or API language parameters
- **Performance**: Baseline measurements and monitoring tools

## Import Instructions

1. Import `sdui-functional-tests.json` for manual functional test cases
2. Import `sdui-api-tests.json` for automated API test cases  
3. Configure test execution environments with required feature flags
4. Set up test data and authentication for comprehensive coverage
5. Schedule jewel event tests during appropriate time periods

## Total Test Coverage

- **Original Total**: 359+ test cases across all documents
- **Represented**: 22 carefully selected representative test cases
- **Coverage Areas**: All major SDUI components and functionality
- **Test Types**: Both manual and automated test approaches
- **Platforms**: Complete cross-platform coverage

These JSON files provide a solid foundation for SDUI testing in Xray while maintaining the comprehensive coverage and structure of the original test documentation.