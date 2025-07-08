# Enhanced Test Steps - Batch 2 (Tests 11-20)

## Test 11: MLBMOB-1981 - Box Score Validation

### Enhanced Test Step:
- **Action:**
  1. **Precondition**: Live game in progress or recently completed game available
  2. Launch MLB app and navigate to Scores/Scoreboard
  3. Select a game to open Gameday view
  4. Navigate to the Box Score tab
  5. Verify both teams' tabs are available
  6. Switch between team tabs
  7. Scroll through batting and pitching statistics

- **Expected Result:**
  1. Box Score should load within 2 seconds
  2. Team tabs should display correctly (ViewPager2 on Android, Segmented Control on iOS)
  3. For each team, verify display of:
     - **Batting Stats**: AB, R, H, RBI, BB, SO, AVG
     - **Pitching Stats**: IP, H, R, ER, BB, SO, ERA
     - **Player Names**: Full names with positions
  4. Active players should show current game stats
  5. Totals row should accurately sum all statistics
  6. Data should match official MLB statistics
  7. UI should update if game is live (every 30 seconds)

---

## Test 12: MLBMOB-1979 - Matchup View Data Updating

### Enhanced Test Step:
- **Action:**
  1. **Precondition**: Live game in progress with active at-bat
  2. Open Gameday for a live game
  3. Navigate to the Matchup/At-Bat view
  4. Observe current batter vs pitcher display
  5. Wait for the at-bat to complete
  6. Monitor the view during the next batter

- **Expected Result:**
  1. Matchup view should display:
     - Current batter photo, name, and season stats
     - Current pitcher photo, name, and game stats
     - Pitch count and ball/strike display
  2. When at-bat changes:
     - View should update within 5 seconds
     - Animation should transition smoothly
     - New batter info should load completely
  3. Historical matchup data (if available) should show
  4. Pitch-by-pitch data should update in real-time
  5. On iOS: GamedayMiniMatchupView should render correctly
  6. On Android: Compose UI should recompose with new data

---

## Test 13: MLBMOB-1841 - tvOS MASN Ad Hoc Test

### Enhanced Test Step:
- **Action:**
  1. **Precondition**: Use MASN test accounts on tvOS device
     - masn@gmail.com (no location override)
     - masnims@gmail.com (In Market)
     - masnoom@gmail.com (Out of Market)
  2. Launch MLB app on tvOS RC 2025.9.0.20504
  3. Login with each test account sequentially
  4. Navigate to a MASN broadcast game
  5. Attempt to play the video content
  6. Test MVPD authentication flow if prompted

- **Expected Result:**
  1. **No location override account**:
     - Should detect user location automatically
     - Apply appropriate blackout rules
  2. **In Market account (masnims)**:
     - Should allow MASN content playback
     - No blackout restrictions
     - Full game access with MASN branding
  3. **Out of Market account (masnoom)**:
     - Should show blackout message
     - Offer alternative viewing options
     - Direct to MVPD authentication if available
  4. RSN container should load properly
  5. Category mappings should display correctly
  6. Sponsor images should load if configured

---

## Test 14: MLBMOB-1790 - Live Game Launch

### Enhanced Test Step:
- **Action:**
  1. **Precondition**: MLB.tv subscription active, live game available
  2. Navigate to Scoreboard/Scores section
  3. Identify a game currently in progress (live indicator)
  4. Tap on the game card
  5. Select "Watch Live" option
  6. Monitor video player launch

- **Expected Result:**
  1. Game card should show live status indicator
  2. Tapping should present game options within 1 second
  3. "Watch Live" should trigger:
     - iOS: VideoLauncher.launchVideo() with live parameters
     - Android: liveGameClick() -> launchMlbTv()
  4. Player should load within 5 seconds
  5. Video should start at live point (unless spoilers hidden)
  6. Player controls should show:
     - Live indicator
     - Jump to live button
     - Stats overlay option
  7. Analytics should track live game launch event

---

## Test 15: MLBMOB-1789 - Archive Launch

### Enhanced Test Step:
- **Action:**
  1. **Precondition**: MLB.tv subscription, completed games available
  2. Navigate to previous date with completed games
  3. Select a final game
  4. Choose "Watch Archive" or similar option
  5. Observe player behavior and starting point

- **Expected Result:**
  1. Completed games should show "Final" status
  2. Archive option should be available in game menu
  3. Launch should check PlaybackResumptionManager for resume points
  4. If no resume point:
     - Start at beginning of broadcast
     - Show pregame content if available
  5. If resume point exists:
     - Prompt user to resume or start over
     - Resume at exact timestamp
  6. No live polling should occur
  7. Full game controls available (scrubbing, skip)

---

## Test 16: MLBMOB-1761 - Day without Games

### Enhanced Test Step:
- **Action:**
  1. Navigate to Scoreboard/Scores
  2. Use date picker to select a day with no games (e.g., All-Star break day)
  3. Observe the UI presentation
  4. Try navigating to adjacent dates
  5. Check calendar view for game indicators

- **Expected Result:**
  1. Empty state should display immediately
  2. Message should indicate "No games scheduled"
  3. Appropriate illustration/graphic should appear
  4. Date picker should:
     - Show dates with games in different style
     - Auto-suggest nearest date with games
  5. Navigation arrows should skip to next/previous game date
  6. getDatesThatHaveGamesScheduled should be called
  7. No loading spinners after initial check

---

## Test 17: MLBMOB-1622 - Picture-In-Picture

### Enhanced Test Step:
- **Action:**
  1. **Precondition**: Device supports PiP, MLB.tv subscription active
  2. Start playing any video content
  3. Initiate PiP mode:
     - iOS: Tap PiP button or swipe home
     - Android: Home button or PiP button
  4. Interact with PiP window
  5. Return to full screen mode

- **Expected Result:**
  1. PiP should activate within 1 second
  2. Video should continue playing in floating window
  3. PiP window should show:
     - Play/pause control
     - Return to app button
     - Close button
  4. Window should be:
     - Movable to screen corners
     - Resizable (platform dependent)
  5. Audio should continue uninterrupted
  6. Returning to app should restore full player
  7. Analytics should track PiP usage

---

## Test 18: MLBMOB-1609 - All-Star Game

### Enhanced Test Step:
- **Action:**
  1. **Precondition**: During All-Star Game period
  2. Navigate to the All-Star Game in schedule
  3. Observe special UI indicators
  4. Attempt to watch the game
  5. Complete MVPD authentication if required

- **Expected Result:**
  1. Game should display with All-Star badge/branding
  2. GameType should equal "A" in data model
  3. Special authentication flow should trigger:
     - URL: https://commerce.mlb.com/asg
     - Partner: "Fox" by default
  4. Different entitlement rules apply
  5. No blackout restrictions for ASG
  6. Special graphics/overlays in player
  7. Unique analytics tracking for ASG

---

## Test 19: MLBMOB-1567 - Exec Users

### Enhanced Test Step:
- **Action:**
  1. **Precondition**: Login with executive/admin account
  2. Navigate through various app sections
  3. Attempt to access restricted content
  4. Check for debug/admin options
  5. Verify special permissions

- **Expected Result:**
  1. Executive users should have:
     - Access to all content without restrictions
     - No blackout limitations
     - Debug menu access (if implemented)
     - All entitlements enabled
  2. Profile should indicate admin status
  3. No paywalls should appear
  4. Test content should be accessible
  5. Analytics should tag user as executive
  6. Special logging may be enabled

---

## Test 20: MLBMOB-1566 - Anon Users

### Enhanced Test Step:
- **Action:**
  1. **Precondition**: Ensure logged out state
  2. Launch app without signing in
  3. Navigate to various sections:
     - Scores
     - News  
     - Video content
     - Team pages
  4. Attempt to access premium content

- **Expected Result:**
  1. Anonymous users should access:
     - Live scores and game data
     - Free news content
     - Game highlights
     - Team information
  2. Restricted content should show:
     - Login prompt
     - Registration options
     - Feature benefits messaging
  3. Favorite team selection should prompt login
  4. No personalized content displayed
  5. FGOTD should require login
  6. Analytics should track anonymous usage