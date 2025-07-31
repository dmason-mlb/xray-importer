# Enhanced Test Steps - Batch 6 (Tests 51-60)

## Test 51: MLBMOB-929 - Readme - Important note for iOS

### Enhanced Test Step:
- **Action:**
  1. **Precondition**: Testing passwordless login on iOS device
  2. Ensure MLB app is installed WITHOUT HTTPS proxy (Charles, etc.)
  3. Navigate to login screen
  4. Select "Magic Link" or passwordless option
  5. Enter email address
  6. Submit and check email
  7. Tap the magic link in email

- **Expected Result:**
  1. App installation should be clean (no proxy certificates)
  2. Magic Link option visible if feature enabled
  3. Email submission should succeed
  4. Magic link email arrives within 2 minutes
  5. CRITICAL: Link should open directly in MLB app
  6. If proxy is active:
     - Link may open in Safari instead
     - Authentication will fail
     - User stuck in browser
  7. Successful flow opens app with user logged in
  8. No intermediate browser steps required

---

## Test 52: MLBMOB-928 - Gesture reduction functionality

### Enhanced Test Step:
- **Action:**
  1. Navigate to Settings → Account Settings
  2. Find Accessibility section
  3. Locate "Gesture Reduction" toggle
  4. Enable the setting
  5. Navigate through the app
  6. Pay attention to animations and transitions
  7. Access FieldPass content if available

- **Expected Result:**
  1. Setting found under Accessibility with key `gestureReductionKey`
  2. Toggle should be OFF by default
  3. When enabled:
     - Reduced motion in transitions
     - Simplified animations
     - Less parallax effects
     - Quicker screen changes
  4. FieldPass receives `isGestureReductionEnabled: true`
  5. Navigation feels more static/immediate
  6. Setting persists across app launches
  7. Accessibility improvement for motion-sensitive users

---

## Test 53: MLBMOB-915 - Track events

### Enhanced Test Step:
- **Action:**
  1. Enable debug/analytics logging if available
  2. Perform various app actions:
     - Navigate between tabs
     - Play a video
     - Select a team
     - Login/logout
     - Toggle settings
  3. Monitor console/logs for tracking events
  4. Verify event parameters

- **Expected Result:**
  1. Each action should trigger analytics events
  2. Common events tracked:
     - `TrackedActionEvent` types on iOS
     - Navigation: tab clicks, page views
     - Video: play, pause, quartiles (0%, 25%, 50%, 75%, 100%)
     - User actions: team selection, login success
  3. Event parameters should include:
     - Event name
     - Timestamp
     - Context data
     - User properties
  4. Adobe Analytics integration active
  5. Conviva tracking for video quality
  6. No duplicate events fired

---

## Test 54: MLBMOB-914 - VSM content navigation

### Enhanced Test Step:
- **Action:**
  1. Start playing a video with scoreboard overlay
  2. Access the Video Scorecard Module (VSM)
  3. Navigate through game tiles in the overlay
  4. Select different games while video plays
  5. Test multiview functionality if available
  6. Check focus management on tvOS

- **Expected Result:**
  1. VSM should display as overlay on video player
  2. Shows horizontal collection of game tiles
  3. Each tile displays:
     - Teams and scores
     - Game status (live/final)
     - Inning/time information
  4. Navigation should be smooth:
     - Arrow keys/swipe between tiles
     - Select to switch games
     - Back to dismiss overlay
  5. Multiview loads multiple games if supported
  6. Focus properly managed on tvOS
  7. EPG integration shows correct data

---

## Test 55: MLBMOB-913 - TC05 - Gameday video context

### Enhanced Test Step:
- **Action:**
  1. Navigate to Gameday for any game
  2. Look for video content integration
  3. Check different tabs (Wrap, Videos, etc.)
  4. Play available video content
  5. Verify context-appropriate videos shown
  6. Test video player integration

- **Expected Result:**
  1. Gameday should have dedicated video sections
  2. Video content contextual to the game:
     - Game highlights
     - Key plays
     - Player interviews
     - Manager comments
  3. Videos should play inline or full-screen
  4. Player controls integrated with Gameday UI
  5. Analytics track video plays with game context
  6. Smooth transitions between video and stats
  7. Live game shows updating video content

---

## Test 56: MLBMOB-912 - TC04 - Scores page video context

### Enhanced Test Step:
- **Action:**
  1. Navigate to Scores/Scoreboard section
  2. Identify video indicators on game cards
  3. Access video content from score cards
  4. Play highlight reels or recaps
  5. Check video preview functionality
  6. Test quick video access

- **Expected Result:**
  1. Score cards should indicate video availability
  2. Video types available:
     - Game recaps
     - Condensed games
     - Key highlights
     - Live look-ins (if applicable)
  3. Videos accessible with single tap
  4. Preview on hover/focus (if supported)
  5. Quick play without leaving scores
  6. Context includes game metadata
  7. Analytics track source as "scores_page"

---

## Test 57: MLBMOB-911 - TC03 - Team page video context

### Enhanced Test Step:
- **Action:**
  1. Navigate to any team's page
  2. Locate video content sections
  3. Check for team-specific videos
  4. Play various video types
  5. Verify filtering by selected team
  6. Test video carousel/grid navigation

- **Expected Result:**
  1. Team page includes dedicated video section
  2. All videos filtered for selected team:
     - Team highlights
     - Player features
     - Press conferences
     - Historical content
  3. Video organization:
     - Most recent first
     - Categories available
     - Search/filter options
  4. Smooth video playback
  5. Team branding in player
  6. Related videos suggested
  7. Analytics include team_id parameter

---

## Test 58: MLBMOB-910 - TC02 - Home tab video context

### Enhanced Test Step:
- **Action:**
  1. Navigate to Home/Feed tab
  2. Scroll through content modules
  3. Identify video modules (MLB.tv, highlights)
  4. Interact with video carousels
  5. Play videos from different modules
  6. Check personalization based on favorites

- **Expected Result:**
  1. Home feed includes multiple video modules
  2. Video content types:
     - Featured videos
     - Trending highlights  
     - Personalized recommendations
     - MLB.tv content (if subscribed)
  3. Smooth carousel scrolling
  4. Video previews/thumbnails load quickly
  5. Personalization based on:
     - Favorite teams
     - Viewing history
     - Subscription status
  6. Inline or full-screen playback
  7. Module-specific analytics tracking

---

## Test 59: MLBMOB-907 - TC45 - Spring training tab config

### Enhanced Test Step:
- **Action:**
  1. During spring training period (or use date override)
  2. Check for spring training tab/section
  3. Navigate to spring training content
  4. Verify special configuration
  5. Check game type indicators
  6. Review standings format

- **Expected Result:**
  1. Spring training identified by GameType "S"
  2. Special tab/section during spring period:
     - Separate from regular season
     - Grapefruit/Cactus League split
     - Different standings format
  3. Configuration differences:
     - Simplified stats
     - Split squad games handled
     - Exhibition game indicators
  4. Remote config controls visibility
  5. Appropriate date ranges enforced
  6. Special spring training news/content
  7. Analytics track as spring_training context

---

## Test 60: MLBMOB-906 - TC34 - Next Game is displayed

### Enhanced Test Step:
- **Action:**
  1. Navigate to team page or schedule
  2. Locate "Next Game" or "Upcoming" section
  3. Verify game details displayed
  4. Check countdown timer (if shown)
  5. Test interaction options:
     - Set reminder
     - Buy tickets
     - Share game
  6. Verify deep linking works

- **Expected Result:**
  1. Next game prominently displayed with:
     - Teams and matchup
     - Date and time (localized)
     - Venue information
     - TV/radio broadcast info
  2. Countdown timer if <24 hours
  3. Interactive elements:
     - Reminder button (calendar integration)
     - Ticket purchase (if available)
     - Share functionality
  4. Deep link format: `mlbatbat://game?gamepk=[id]`
  5. Updates automatically when game ends
  6. Handles doubleheaders correctly
  7. Off-season shows spring training games