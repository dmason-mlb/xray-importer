# Enhanced Test Steps - Batch 5 (Tests 41-50)

## Test 41: MLBMOB-1217 - Game: Start cast session then play content

### Enhanced Test Step:
- **Action:**
  1. **Precondition**: Entitled user with MLB.tv subscription, cast device available
  2. Connect to Chromecast device first (no content playing)
  3. Verify cast session established with "Ready to Cast" state
  4. Navigate to a live or archived game
  5. Select "Watch" option
  6. Choose to play on the connected cast device

- **Expected Result:**
  1. Cast connection should show device name and ready state
  2. Game selection should trigger:
     - Entitlement check for the game
     - JWT token generation for authenticated content
     - Game metadata preparation
  3. Content should begin playing on TV within 5 seconds
  4. Cast controls should display:
     - Game title and teams
     - Current inning/time
     - Play/pause controls
     - Live indicator (if applicable)
  5. Mobile device should show synchronized controls
  6. No buffering or authentication delays
  7. Analytics should track cast game start

---

## Test 42: MLBMOB-1216 - Game: Start stream on mobile then cast it

### Enhanced Test Step:
- **Action:**
  1. **Precondition**: Entitled user, no active cast session
  2. Navigate to a game (live or archived)
  3. Start playing the game on mobile device
  4. Verify game is playing with stats overlay available
  5. Tap cast icon while game is playing
  6. Select available Chromecast device
  7. Monitor the casting transition

- **Expected Result:**
  1. Game should play on mobile with full features
  2. Cast icon should be visible in player controls
  3. Selecting cast device should:
     - Pause mobile playback
     - Show "Casting to [device]" message
     - Transfer playback to TV
  4. Current playback position should be maintained
  5. Game-specific data transferred:
     - JWT authentication token
     - Game PK and metadata
     - Current inning/timestamp
     - Audio track selection
  6. TV playback should resume within 5 seconds
  7. Mobile should display cast controls

---

## Test 43: MLBMOB-1215 - Playback with Ads Disabled

### Enhanced Test Step:
- **Action:**
  1. **Precondition**: Login with VIDEO_ADS_DISABLED account (e.g., adsDisabled@gmail.com)
  2. Navigate to any video content (game, highlight, etc.)
  3. Start video playback
  4. Monitor network requests for CDN URLs
  5. Watch for any ad breaks or DAI insertions
  6. Note: Audio EPG player always uses fastly/media-cdn URL

- **Expected Result:**
  1. User profile should have VIDEO_ADS_DISABLED flag
  2. Video playback should:
     - Use direct CDN URL (fastly/media-cdn)
     - NOT use DAI (Dynamic Ad Insertion) URLs
     - Skip all commercial breaks
     - Play content uninterrupted
  3. In player logs/network:
     - `isDAIEnabled` should be false
     - `adExperience.isEnabled` should be false
  4. No Google IMA SDK initialization
  5. No ad tracking events fired
  6. Seamless playback experience
  7. Audio streams always bypass DAI

---

## Test 44: MLBMOB-1200 - More than 3 tap stories

### Enhanced Test Step:
- **Action:**
  1. Navigate to a surface/section with tap stories
  2. Verify the content module loads
  3. Count the number of tap stories displayed
  4. Check if "See More" or pagination exists
  5. Interact with stories beyond the third one

- **Expected Result:**
  1. Tap stories module should load successfully
  2. Display behavior based on UI style:
     - Stack style: Up to 6 stories visible
     - Carousel: Scrollable with all stories
     - Hero: 1 featured story
     - Duo: 2 stories side by side
     - Trio: 3 stories in a row
  3. If more than display limit exists:
     - Pagination or scroll indicators shown
     - Additional stories accessible via interaction
  4. Each story should have:
     - Thumbnail image
     - Headline text
     - Tap target for navigation
  5. Analytics track story impressions

---

## Test 45: MLBMOB-1197 - Less than 4 articles

### Enhanced Test Step:
- **Action:**
  1. Navigate to a content section with limited articles
  2. Find a module/surface with fewer than 4 articles
  3. Observe the layout and presentation
  4. Check for any empty state handling

- **Expected Result:**
  1. Content should display gracefully with <4 articles
  2. Layout adjustments:
     - No empty placeholders shown
     - Content centers or left-aligns appropriately
     - Maintains visual hierarchy
  3. Based on display style minimum requirements:
     - Hero: Shows if at least 1 article
     - Duo: Shows if at least 2 articles
     - Trio: Shows if at least 3 articles
     - Stack: May show partial row
  4. No error states or broken layouts
  5. "See More" link hidden if insufficient content

---

## Test 46: MLBMOB-1196 - Exploring a Category in More Depth

### Enhanced Test Step:
- **Action:**
  1. Navigate to News or content section
  2. Identify category filters or tabs
  3. Select a specific category (e.g., "Trades", "Injuries")
  4. Browse within the category
  5. Use any refinement options available
  6. Navigate to full category view if available

- **Expected Result:**
  1. Categories should be clearly labeled and selectable
  2. Selecting a category should:
     - Filter content immediately
     - Update URL/navigation state
     - Show category-specific content only
  3. Category view features:
     - Breadcrumb navigation
     - Result count indicator
     - Sort options (date, relevance)
     - Load more functionality
  4. Content should be relevant to selected category
  5. Back navigation preserves category selection
  6. Analytics track category exploration

---

## Test 47: MLBMOB-937 - NL - No duplication of team names?

### Enhanced Test Step:
- **Action:**
  1. Navigate to Negro Leagues section or team selector
  2. Browse through all Negro League teams
  3. Check for any duplicate team names
  4. Compare team names across different cities
  5. Verify unique identification for each team

- **Expected Result:**
  1. Negro League teams loaded from MLBTeams+NegroLeagues.json
  2. Each team should have unique:
     - Team ID (numeric identifier)
     - Full team name
     - Abbreviation
  3. No exact duplicate team names should appear
  4. Teams with similar names differentiated by:
     - City prefix
     - Year active (if shown)
     - League affiliation
  5. Team selection should work correctly
  6. No UI confusion from similar names

---

## Test 48: MLBMOB-936 - NL - New York Black Yankees do not overlap with New York Cubans

### Enhanced Test Step:
- **Action:**
  1. Access Negro Leagues team list
  2. Locate "New York Black Yankees"
  3. Locate "New York Cubans"
  4. Verify both teams display separately
  5. Check team details for each
  6. Test selection of each team independently

- **Expected Result:**
  1. Both teams should appear as distinct entries
  2. New York Black Yankees:
     - Unique team ID
     - Correct historical information
     - Proper logo/branding if available
  3. New York Cubans:
     - Different team ID
     - Separate historical data
     - Distinct visual identity
  4. No data mixing between teams
  5. Selection of one doesn't affect the other
  6. Both teams properly integrated in `negroLeagueTeams` array

---

## Test 49: MLBMOB-935 - NL - teams with same name different city

### Enhanced Test Step:
- **Action:**
  1. Browse Negro Leagues team list
  2. Identify teams with same name but different cities
  3. Examples to check:
     - "Giants" teams from different cities
     - "Stars" teams from different cities
  4. Verify each team's distinct identity
  5. Test functionality with each team

- **Expected Result:**
  1. Teams with same base name differentiated by city:
     - "Chicago Giants" vs "Harrisburg Giants"
     - "Detroit Stars" vs "St. Louis Stars"
  2. Each team should have:
     - Unique team ID in database
     - City prefix clearly visible
     - Separate team pages/content
  3. Team picker shows full name with city
  4. No confusion in team selection
  5. Filtering/search works correctly
  6. Historical data accurate for each team

---

## Test 50: MLBMOB-930 - Reset password on device running MLB App

### Enhanced Test Step:
- **Action:**
  1. Launch MLB app and go to login screen
  2. Tap "Forgot Password?" or "Reset Password" link
  3. Enter email address associated with account
  4. Submit password reset request
  5. Check email for reset instructions
  6. Follow link to reset password
  7. Return to app and login with new password

- **Expected Result:**
  1. Password reset option clearly visible on login screen
  2. Reset flow should offer:
     - Magic Link option (if enabled)
     - Traditional password reset
  3. Email submission should:
     - Validate email format
     - Show confirmation message
     - Send email within 2 minutes
  4. Reset email should contain:
     - Secure reset link
     - Expiration time notice
     - Support contact info
  5. New password requirements shown
  6. Successful reset confirmed in app
  7. Analytics track reset completion