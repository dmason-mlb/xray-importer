# Enhanced Test Steps - Batch 1 (Tests 1-10)

## Test 1: MLBMOB-2443 - Main page - impression tracking

### Enhanced Test Step:
- **Action:**
  1. **Precondition**: Ensure test account has a favorite team selected
  2. Launch the MLB app on iOS/Android device
  3. Navigate to the Main/Home page (bottom navigation tab)
  4. Scroll down until the TicketMerchandisingModule is visible on screen
  5. Ensure the module has fully loaded (WebView content is displayed)
  6. Wait 2 seconds for impression tracking to register

- **Expected Result:**
  1. TicketMerchandisingModule WebView should load within 3 seconds
  2. Impression tracking event should fire with the following parameters:
     - Event name: "[actionTag] : Ticket Merchandising Impression"
     - Module type: "Ticket Merchandising"
     - Content labels: [campaignType] + [contentKey]
     - Game PKs: Comma-separated list of associated game IDs
  3. Analytics dashboard should show the impression event
  4. Module should display ticket options relevant to user's favorite team
  5. WebView should be interactive and respond to tap events

---

## Test 2: MLBMOB-2441 - MLB.tv - module stops playing after removal

### Enhanced Test Step:
- **Action:**
  1. **Precondition**: Ensure MLB.tv subscription is active on test account
  2. Launch the MLB app and navigate to a surface containing MLB.tv module
  3. Start playing a video in the MLB.tv module
  4. Verify video is playing with audio
  5. Navigate away from the current screen (e.g., tap different tab)
  6. Return to the previous screen

- **Expected Result:**
  1. Video playback should stop immediately when navigating away
  2. Audio should cease within 1 second of navigation
  3. Player resources should be released (verify in logs)
  4. On iOS: MLBTVCell cleanup() method should be called
  5. On Android: MediaPlayer stop() and release() should be invoked
  6. No background video/audio playback should continue
  7. Memory should be freed (no player instance retained)

---

## Test 3: MLBMOB-2440 - MLB.tv - module should stop playing after removal

### Enhanced Test Step:
- **Action:**
  1. **Precondition**: MLB.tv subscription active, multiple video modules on screen
  2. Launch app and navigate to surface with multiple MLB.tv modules
  3. Start playing video in one MLB.tv module
  4. Scroll the module off-screen (out of viewport)
  5. Continue scrolling until module is completely removed from view hierarchy

- **Expected Result:**
  1. Video playback should pause when module scrolls off-screen
  2. When module is removed from collection view/recycler view:
     - iOS: AutoPlayPool should unregister the item
     - Android: DisposableEffect should trigger cleanup
  3. Player resources should be released
  4. No audio should continue playing
  5. If scrolled back into view, video should not auto-resume
  6. System resources (memory/CPU) should decrease

---

## Test 4: MLBMOB-2435 - MLB.tv - Live Mode FGOTD Support

### Enhanced Test Step:
- **Action:**
  1. **Precondition**: Use non-subscribed test account during FGOTD window
  2. Launch app and navigate to home surface
  3. Locate the Free Game of the Day (FGOTD) in MLB.tv section
  4. Verify FGOTD badge/indicator is displayed
  5. Tap on the FGOTD video tile
  6. Attempt to play the free game

- **Expected Result:**
  1. FGOTD should be clearly marked with badge/indicator
  2. Content restriction check should identify game as FGOTD
  3. If not logged in:
     - iOS: Show login_needed_fgotd error
     - Android: Display FgotdDialog with login/register options
  4. If logged in without subscription:
     - Game should play without paywall
     - Full game access should be granted
  5. Analytics should track FGOTD access attempt
  6. Video player should load with appropriate FGOTD entitlements

---

## Test 5: MLBMOB-2434 - MLB.tv - Live Mode FGOTD Support (Duplicate)

### Enhanced Test Step:
- **Action:**
  1. **Precondition**: MLB.tv subscription expired, FGOTD available
  2. Launch app while logged in with expired subscription
  3. Navigate to home surface
  4. Find and select the FGOTD content
  5. Monitor entitlement checks in network logs

- **Expected Result:**
  1. FGOTD should override subscription requirement
  2. Entitlement service should return positive for FGOTD
  3. No paywall should appear for the free game
  4. Video should play with full controls available
  5. Quality options should be accessible
  6. Game should play to completion without interruption

---

## Test 6: MLBMOB-2232 - It should show favorite team news

### Enhanced Test Step:
- **Action:**
  1. **Precondition**: Set Yankees as favorite team in user profile
  2. Launch app and navigate to News section
  3. Verify team selector shows Yankees as selected
  4. Observe the news feed content
  5. Pull to refresh the news feed

- **Expected Result:**
  1. Team selector header should display Yankees logo/name
  2. News feed should show Yankees-specific articles
  3. API call should include Yankees team ID parameter
  4. Maximum 5 news items should display initially
  5. "See All News" link should navigate to full Yankees news
  6. Articles should be sorted by publish date (newest first)
  7. Each article should show:
     - Headline
     - Thumbnail image
     - Publication date
     - Author (if available)

---

## Test 7: MLBMOB-2231 - Users should be able to open a news item

### Enhanced Test Step:
- **Action:**
  1. Navigate to News section in the app
  2. Locate any news article in the feed
  3. Tap on the news article card/cell
  4. Wait for article to load
  5. Interact with article content (scroll, tap links)

- **Expected Result:**
  1. Article should open within 2 seconds
  2. On iOS: Opens in Safari/SFSafariViewController or WebView
  3. On Android: Opens in Chrome Custom Tabs or WebView
  4. Article URL should be processed through GetNewsArticleUrlUseCase
  5. Full article content should be displayed
  6. Navigation bar should show:
     - Close/back button
     - Article title
     - Share button (platform dependent)
  7. User should be able to return to news list

---

## Test 8: MLBMOB-2230 - It should show latest news as default tab

### Enhanced Test Step:
- **Action:**
  1. Force quit the app to ensure fresh launch
  2. Launch MLB app
  3. Navigate to News section for the first time
  4. Observe the default selected tab
  5. Check the content displayed

- **Expected Result:**
  1. "Latest" or "MLB News" tab should be selected by default
  2. Content should show league-wide MLB news (not team-specific)
  3. GetNewsIndexForMlbUseCase should be called (verify in logs)
  4. News items should include stories from all teams
  5. Tab indicator should highlight the latest/MLB news option
  6. Articles should be sorted by most recent first
  7. Feed should auto-refresh if stale (>30 minutes old)

---

## Test 9: MLBMOB-2229 - Deep-links Tests should open scoreboard screen when using deeplink

### Enhanced Test Step:
- **Action:**
  1. Close the MLB app completely
  2. Open a web browser or notes app
  3. Enter deep link URL: `mlbatbat://scoreboard`
  4. Tap the link to launch the app
  5. Observe app navigation behavior

- **Expected Result:**
  1. App should launch or come to foreground
  2. Should navigate directly to Scoreboard screen
  3. On Android: ScoreboardDestinationProvider should handle routing
  4. On iOS: DeepLinkAdapter should process the URL
  5. Scoreboard should display current day's games
  6. Navigation stack should allow back navigation to home
  7. Analytics should track deep link usage
  8. If app was already open, should navigate from current position

---

## Test 10: MLBMOB-2228 - Deep-links Tests should open watch screen when using deeplink

### Enhanced Test Step:
- **Action:**
  1. Ensure app is in background or closed
  2. Trigger deep link: `mlbatbat://watch`
  3. Can test via:
     - Safari URL bar
     - Email link
     - QR code
     - Push notification action
  4. Monitor app launch and navigation

- **Expected Result:**
  1. App should launch/resume within 2 seconds
  2. Should navigate directly to Watch/MLB.tv screen
  3. On Android: WatchDestinationProvider routes to R.id.navigation_watch
  4. On iOS: Routes to MLB.tv tab/screen
  5. If subscription exists, should show available games
  6. If no subscription, should show subscription options
  7. Deep link should work from both cold and warm launch
  8. Previous screen state should not interfere with navigation