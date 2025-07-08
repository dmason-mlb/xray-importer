# Enhanced Test Steps - Batch 7 (Tests 61-70)

## Test 61: MLBMOB-822 - TC15 - Settings deeplink

### Enhanced Test Step:
- **Action:**
  1. Close the MLB app completely
  2. Open a browser or notes app
  3. Enter the deep link: `mlbatbat://settings`
  4. Tap the link to launch the app
  5. Observe app launch and navigation
  6. Verify correct screen is displayed

- **Expected Result:**
  1. App should launch from cold state
  2. Deep link handled during launch:
     - iOS: SceneDelegate processes in `willConnectTo`
     - Android: Intent passed from SplashScreen to MainActivity
  3. App should navigate directly to Settings screen
  4. Navigation stack should include:
     - Home/Main screen in background
     - Settings on top
  5. Back navigation should return to home
  6. All settings options should be accessible
  7. Analytics should track deep link usage

---

## Test 62: MLBMOB-821 - TC12 - Splash Screen - No internet connection Warm Launch

### Enhanced Test Step:
- **Action:**
  1. **Precondition**: App previously launched and in background
  2. Turn off all network connections (WiFi, cellular)
  3. Bring app to foreground (warm launch)
  4. Observe splash screen behavior
  5. Monitor loading indicators
  6. Check for error handling

- **Expected Result:**
  1. Warm launch detected (appOpenedState = .background)
  2. Splash screen should appear briefly
  3. Network checks should detect no connectivity:
     - iOS: ABReachability.isConnected() returns false
     - Android: Network-dependent ops fail gracefully
  4. Android behavior:
     - 6-second timer ensures progress
     - Skips ad loading on error
     - Proceeds to MainActivity
  5. iOS behavior:
     - May show offline alert
     - Continues to main screen
  6. No infinite loading or stuck states
  7. Cached data should be available

---

## Test 63: MLBMOB-675 - NL - No duplication of team names? (Duplicate)

### Enhanced Test Step:
- **Action:**
  1. Navigate to Negro Leagues section
  2. Access complete team list
  3. Sort or filter by team name
  4. Check for exact duplicate names
  5. Verify each team's unique identity
  6. Test team selection functionality

- **Expected Result:**
  1. All Negro League teams loaded from JSON data
  2. No two teams should have identical names
  3. Each team must have:
     - Unique team ID
     - Distinct full name
     - Proper abbreviation
  4. Similar names differentiated by:
     - City (e.g., "Chicago Giants" vs "Harrisburg Giants")
     - Time period (if included)
  5. UI should clearly display full team names
  6. No confusion in team picker
  7. Search/filter works correctly

---

## Test 64: MLBMOB-674 - NL - New York Black Yankees do not overlap with New York Cubans (Duplicate)

### Enhanced Test Step:
- **Action:**
  1. Access Negro Leagues team selector
  2. Search or scroll to New York teams
  3. Verify both teams listed separately:
     - New York Black Yankees
     - New York Cubans
  4. Select each team individually
  5. Check team details and history

- **Expected Result:**
  1. Both teams appear as distinct entries
  2. New York Black Yankees:
     - Unique team ID (different from Cubans)
     - Correct historical period
     - Separate team page
  3. New York Cubans:
     - Different team ID
     - Own historical data
     - Distinct team page
  4. No data overlap or confusion
  5. Both properly indexed in search
  6. Team stats/records separate

---

## Test 65: MLBMOB-673 - NL - teams with same name different city (Duplicate)

### Enhanced Test Step:
- **Action:**
  1. Browse complete Negro Leagues team list
  2. Identify all teams sharing base names:
     - All "Giants" teams
     - All "Stars" teams
     - All "Monarchs" teams
  3. Verify city differentiation
  4. Test each team's functionality

- **Expected Result:**
  1. Teams with same base name show city prefix:
     - "Birmingham Giants"
     - "Chicago Giants"  
     - "Harrisburg Giants"
  2. Each variant has:
     - Unique database ID
     - City clearly visible in UI
     - Separate historical data
  3. No ambiguity in selection
  4. Filtering by city works correctly
  5. Team pages load correct data
  6. Analytics track correct team_id

---

## Test 66: MLBMOB-668 - Reset password on device running MLB App (Duplicate)

### Enhanced Test Step:
- **Action:**
  1. Open MLB app to login screen
  2. Tap "Forgot Password?" link
  3. Choose password reset method:
     - Magic Link (if enabled)
     - Traditional reset
  4. Enter registered email
  5. Submit request
  6. Check email and follow instructions
  7. Set new password and login

- **Expected Result:**
  1. Password reset options clearly visible
  2. Email validation on submission
  3. Confirmation screen shows:
     - Email sent message
     - Check spam folder note
     - Support contact info
  4. Reset email arrives <5 minutes
  5. Link opens password reset form
  6. Password requirements displayed:
     - Minimum length
     - Character requirements
  7. Success message after reset
  8. Can login with new password

---

## Test 67: MLBMOB-667 - Readme - Important note for iOS (Duplicate)

### Enhanced Test Step:
- **Action:**
  1. **Setup**: Install MLB app on iOS device
  2. Ensure NO proxy tools active (Charles, Fiddler)
  3. Attempt passwordless/Magic Link login
  4. Enter email for Magic Link
  5. Check email and tap link
  6. Verify proper app handling

- **Expected Result:**
  1. Clean installation without proxy certificates
  2. Magic Link email received
  3. Tapping link should:
     - Open MLB app directly
     - NOT open Safari
     - Complete authentication in-app
  4. If proxy is active:
     - Link opens in Safari (WRONG)
     - Authentication fails
     - User cannot complete login
  5. Successful flow logs user in
  6. No browser redirection
  7. Seamless app experience

---

## Test 68: MLBMOB-666 - Gesture reduction functionality (Duplicate)

### Enhanced Test Step:
- **Action:**
  1. Go to Settings → Account Settings
  2. Navigate to Accessibility section
  3. Find "Reduce Motion" or "Gesture Reduction"
  4. Toggle the setting ON
  5. Navigate back to main app
  6. Observe animation changes throughout app
  7. Test FieldPass content specifically

- **Expected Result:**
  1. Setting located in Accessibility section
  2. Default state: OFF
  3. When enabled (`gestureReductionKey = true`):
     - Crossfade transitions instead of slides
     - Reduced parallax effects
     - Simpler animations
     - Faster screen changes
  4. FieldPass components respect setting
  5. Changes apply immediately
  6. Setting persists after app restart
  7. Improves accessibility for users sensitive to motion

---

## Test 69: MLBMOB-653 - Track events (Duplicate)

### Enhanced Test Step:
- **Action:**
  1. Enable analytics debug mode (if available)
  2. Perform comprehensive app actions:
     - App launch
     - Tab navigation
     - Video playback (start, quartiles, complete)
     - Authentication events
     - Team/player selection
     - Settings changes
  3. Monitor event tracking
  4. Verify event accuracy

- **Expected Result:**
  1. All user actions generate analytics events
  2. Event categories tracked:
     - Navigation: Page views, tab switches
     - Video: Play, pause, progress (0%, 25%, 50%, 75%, 100%)
     - User: Login, logout, registration
     - Engagement: Favorites, shares, notifications
  3. Each event includes:
     - Event name and type
     - Timestamp
     - User context
     - Screen/feature context
  4. No missing or duplicate events
  5. Adobe Analytics receives all events
  6. Conviva tracks video quality metrics

---

## Test 70: MLBMOB-652 - VSM content navigation (Duplicate)

### Enhanced Test Step:
- **Action:**
  1. Start video playback (game or highlight)
  2. Access Video Scorecard Module overlay
  3. Navigate through available game tiles
  4. Test different navigation methods:
     - Touch/swipe on mobile
     - Remote control on tvOS
  5. Select different games
  6. Test multiview if available

- **Expected Result:**
  1. VSM overlay appears over video content
  2. Displays horizontal scrolling game tiles
  3. Each tile shows:
     - Team names and logos
     - Current score
     - Game status/inning
     - Live indicator if applicable
  4. Navigation is smooth and responsive
  5. Selecting a tile:
     - Switches to that game
     - Updates video player
     - Maintains overlay briefly
  6. Multiview loads multiple games side-by-side
  7. Focus management works properly on tvOS