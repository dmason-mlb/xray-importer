# Enhanced Test Steps - Batch 3 (Tests 21-30)

## Test 21: MLBMOB-1565 - TV Yearly

### Enhanced Test Step:
- **Action:**
  1. **Precondition**: Use test account without active subscription
  2. Navigate to subscription/paywall screen
  3. Review available subscription options
  4. Select "MLB.TV Yearly" subscription option
  5. Complete purchase flow (use test payment method)
  6. Verify subscription activation
  7. Access premium content

- **Expected Result:**
  1. Yearly subscription option should display:
     - Price (varies by market)
     - Duration: Full season access
     - Auto-renewal information
  2. Purchase flow should complete successfully
  3. Subscription should activate immediately
  4. User entitlements should update to include:
     - All live games (subject to blackouts)
     - Full game archives
     - No commercial breaks
  5. Profile should show active yearly subscription
  6. Renewal date should be set for next March 1st
  7. All MLB.TV content should be accessible

---

## Test 22: MLBMOB-1564 - TV Monthly

### Enhanced Test Step:
- **Action:**
  1. **Precondition**: Test account with no active subscription
  2. Access subscription options from paywall
  3. Select "MLB.TV Monthly" option ($24.99/month)
  4. Review terms including:
     - 7-day free trial (if eligible)
     - Monthly auto-renewal
  5. Complete subscription purchase
  6. Verify immediate access

- **Expected Result:**
  1. Monthly subscription should show:
     - $24.99/month pricing
     - Free trial availability (first-time users)
     - Monthly renewal terms
  2. After purchase:
     - Immediate access to all MLB.TV content
     - Next billing date in 30 days (or after trial)
     - Cancellation option available
  3. Entitlements identical to yearly plan
  4. Auto-renewal can be managed in settings
  5. Available March through October only

---

## Test 23: MLBMOB-1563 - Single-Team Users

### Enhanced Test Step:
- **Action:**
  1. **Precondition**: Account with single-team subscription
  2. Navigate to team selection in settings
  3. Verify selected team is shown
  4. Browse to games/content:
     - Selected team's games
     - Other teams' games
  5. Attempt to play various content

- **Expected Result:**
  1. Single team should be clearly indicated in profile
  2. Full access to selected team's games:
     - Live games (subject to blackouts)
     - Archives
     - Spring training
  3. Other teams' content should show:
     - Paywall/upgrade prompt
     - Option to upgrade to full MLB.TV
  4. Analytics should track as single-team user
  5. Team-specific notifications available
  6. Condensed games for selected team accessible

---

## Test 24: MLBMOB-1562 - Free Users

### Enhanced Test Step:
- **Action:**
  1. **Precondition**: Logged out or free account (no subscription)
  2. Browse app sections:
     - Scores/standings
     - News
     - Video highlights
     - Live games
  3. Attempt to access premium content
  4. Check for FGOTD availability

- **Expected Result:**
  1. Free access should include:
     - Live scores and game tracking
     - Game highlights and recaps
     - News articles
     - Team/player stats
  2. Premium content should show:
     - "Subscription Required" message
     - Clear paywall presentation
     - Subscription options
  3. Blackout restrictions apply to all content
  4. FGOTD requires login but no payment
  5. Limited video quality for free content
  6. Ads may be shown in free content

---

## Test 25: MLBMOB-1560 - Entitled

### Enhanced Test Step:
- **Action:**
  1. **Precondition**: Account with active MLB.TV subscription
  2. Launch app and verify entitled status
  3. Access various content types:
     - Live games
     - Archives
     - Radio broadcasts
  4. Check entitlement indicators
  5. Verify no paywall interruptions

- **Expected Result:**
  1. Profile should show active subscription
  2. No paywall screens should appear
  3. Full access to:
     - All live games (except blackouts)
     - Complete game archives
     - Multi-angle views
     - Stats overlays
  4. Premium features enabled:
     - HD quality streaming
     - No commercial breaks
     - Download for offline (if available)
  5. Entitlement checks should pass silently
  6. Subscription expiry date visible in settings

---

## Test 26: MLBMOB-1235 - Casting -> Stop Casting behavior

### Enhanced Test Step:
- **Action:**
  1. **Precondition**: Active cast session with media playing
  2. Verify content is playing on TV/Chromecast
  3. Access cast controls (notification or in-app)
  4. Tap "Stop Casting" button
  5. Observe behavior on both devices

- **Expected Result:**
  1. Cast notification should show current playback
  2. Stop casting should:
     - Immediately halt TV playback
     - Clear cast notification
     - Return to device playback option
  3. On iOS: `stopCastMedia()` should execute:
     - Stop scrubber timer
     - End audio interruption
     - Set state to `.noRoute`
  4. On Android: Session should end cleanly
  5. Playback position should be preserved
  6. Option to resume on device should appear

---

## Test 27: MLBMOB-1234 - Casting -> Select Closed Captioning

### Enhanced Test Step:
- **Action:**
  1. **Precondition**: User casting MLB content to TV
  2. Access player controls during cast
  3. Navigate to CC/subtitle options
  4. Toggle closed captions on/off
  5. Verify CC state on TV screen

- **Expected Result:**
  1. CC button should be visible in cast controls
  2. Current CC state should be indicated
  3. Toggling CC should:
     - Update immediately on TV
     - Persist the preference
     - Sync with device settings
  4. CC data sent to receiver:
     - `closedCaptionKey`: current state
     - `captionsEnabled`: boolean
  5. System accessibility settings should be respected
  6. CC state maintained if switching content

---

## Test 28: MLBMOB-1233 - Mobile: Put device in sleep mode while casting

### Enhanced Test Step:
- **Action:**
  1. **Precondition**: Active cast with video playing on TV
  2. Verify stable cast connection
  3. Put mobile device to sleep:
     - Press power button
     - Let screen timeout
  4. Wait 30 seconds
  5. Wake device and check cast state

- **Expected Result:**
  1. TV playback should continue uninterrupted
  2. Chromecast operates independently
  3. Upon wake:
     - Cast session should still be active
     - Notification controls should be available
     - Playback position should be current
  4. No audio/video interruption on TV
  5. Cast controls should respond immediately
  6. Stream quality should remain stable

---

## Test 29: MLBMOB-1232 - Mobile: Background the app while casting

### Enhanced Test Step:
- **Action:**
  1. **Precondition**: Cast session active, media playing
  2. Swipe up/press home to background app
  3. Use other apps for 1-2 minutes
  4. Check notification shade for cast controls
  5. Return to MLB app

- **Expected Result:**
  1. Backgrounding should not affect cast playback
  2. Cast notification should remain visible
  3. Notification controls should work:
     - Play/pause
     - Stop casting
     - Expand for more options
  4. On return to app:
     - Cast state should be synchronized
     - Current position accurate
     - Controls responsive
  5. iOS: ExpandedControlsActivity launches if needed
  6. No session disconnection or errors

---

## Test 30: MLBMOB-1231 - Mobile: Casting notification controls

### Enhanced Test Step:
- **Action:**
  1. **Precondition**: Active cast session with game playing
  2. Pull down notification shade
  3. Locate cast notification
  4. Test each control:
     - Play/pause toggle
     - Skip forward/back (if available)
     - Stop casting
  5. Expand notification for more options

- **Expected Result:**
  1. Cast notification should appear automatically
  2. Notification should display:
     - Current content title
     - Playback progress
     - Team logos/thumbnails
  3. Controls should be responsive:
     - Play/pause updates within 1 second
     - Skip controls work if enabled
  4. Expanded view should show:
     - Larger controls
     - Volume adjustment
     - Quality settings (if applicable)
  5. Android: ExpandedControlsActivity integration
  6. iOS: Default or custom expanded controls based on config