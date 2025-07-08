# Enhanced Test Steps - Batch 4 (Tests 31-40)

## Test 31: MLBMOB-1230 - Mobile: Casting controls

### Enhanced Test Step:
- **Action:**
  1. **Precondition**: Active cast session with media playing
  2. Access the casting controls UI in the app
  3. Test all available controls:
     - Play/Pause toggle
     - Scrubber/seek bar
     - Volume control
     - Quality settings
     - CC toggle
  4. Verify control responsiveness
  5. Check synchronization with TV playback

- **Expected Result:**
  1. Cast controls should display current playback state
  2. Play/pause should toggle within 1 second
  3. Scrubber should show:
     - Current position
     - Total duration
     - Buffered content (if applicable)
  4. Seeking should:
     - Update TV playback immediately
     - Show loading state during seek
     - Resume playback at new position
  5. Volume changes should reflect on TV
  6. Quality/CC changes should apply without interrupting playback
  7. All controls should remain responsive during network fluctuations

---

## Test 32: MLBMOB-1228 - SLIVE: Start stream on mobile then cast it

### Enhanced Test Step:
- **Action:**
  1. **Precondition**: Entitled user with MLB.TV subscription
  2. Navigate to a live game (SLIVE - Subscription Live)
  3. Start playing the stream on mobile device
  4. Verify playback is working with audio/video
  5. Tap the cast icon while stream is playing
  6. Select available Chromecast device
  7. Monitor transition to cast mode

- **Expected Result:**
  1. Mobile playback should start successfully with JWT auth
  2. Cast icon should appear when Chromecast is available
  3. Upon casting:
     - Mobile playback should pause
     - Loading indicator should appear
     - TV should begin playback within 5 seconds
  4. Cast session should include:
     - JWT token in custom data
     - Proper content type: "SLIVE"
     - Live stream parameters
  5. Mobile should show cast controls
  6. Stream quality should adapt to TV capability
  7. No re-authentication required

---

## Test 33: MLBMOB-1227 - FLIVE: Start a stream on mobile then cast it

### Enhanced Test Step:
- **Action:**
  1. **Precondition**: Any user (entitled or free)
  2. Find Free Game of the Day (FLIVE - Free Live)
  3. Start playing on mobile device
  4. Confirm no subscription prompt appears
  5. Initiate casting to available device
  6. Monitor the cast transition

- **Expected Result:**
  1. FLIVE content should play without authentication
  2. No subscription check should occur
  3. Cast transition should:
     - Not require JWT token
     - Set content type as "FLIVE"
     - Complete within 3-5 seconds
  4. Custom data should indicate free content
  5. Full playback controls available
  6. Quality options same as premium content
  7. Analytics should track as free game cast

---

## Test 34: MLBMOB-1226 - VOD/SVOD: While casting Game content switch to VOD/SVOD stream

### Enhanced Test Step:
- **Action:**
  1. **Precondition**: Entitled user, cast session playing game content
  2. Verify game is casting to TV successfully
  3. Navigate to VOD/SVOD content in app
  4. Select a different video (highlight, recap, etc.)
  5. Choose to play on the existing cast session
  6. Monitor content switch behavior

- **Expected Result:**
  1. Current game cast should continue during navigation
  2. Selecting new content should prompt:
     - "Replace current cast?" dialog
     - Or automatic replacement (based on UX)
  3. Content switch should:
     - Stop current stream cleanly
     - Load new media with proper metadata
     - SVOD: Include JWT authentication
     - VOD: No auth required
  4. New content should start within 5 seconds
  5. Player state should reset (position, duration)
  6. Appropriate analytics for content switch

---

## Test 35: MLBMOB-1225 - SVOD: Attempt to cast when unentitled

### Enhanced Test Step:
- **Action:**
  1. **Precondition**: Unentitled user (not logged in/free account), cast device available
  2. Navigate to premium SVOD content
  3. Attempt to cast the content
  4. Observe authentication flow
  5. Try different premium content types

- **Expected Result:**
  1. Cast button should be visible but trigger auth check
  2. Upon cast attempt:
     - Entitlement check should fail
     - Login/subscription prompt should appear
     - No content should start on TV
  3. Error messaging should be clear:
     - "Subscription required for casting"
     - Login/signup options presented
  4. Cast session should not establish
  5. Free content casting should still work
  6. Analytics should track failed cast attempt

---

## Test 36: MLBMOB-1224 - SVOD: Start cast session then play content

### Enhanced Test Step:
- **Action:**
  1. **Precondition**: Entitled user, no active cast session
  2. Tap cast icon to connect to device
  3. Wait for cast session to establish
  4. Navigate to SVOD content
  5. Select content to play on cast device
  6. Monitor playback initiation

- **Expected Result:**
  1. Cast session should connect showing:
     - "Ready to cast" state
     - Connected device name
     - No content playing initially
  2. Selecting SVOD content should:
     - Perform entitlement check
     - Generate JWT token if needed
     - Load media with authentication
  3. Playback should start within 5 seconds
  4. Cast receiver should show MLB branding
  5. Full controls available immediately
  6. Session should remain stable

---

## Test 37: MLBMOB-1223 - SVOD: Start stream on mobile then cast it

### Enhanced Test Step:
- **Action:**
  1. **Precondition**: Entitled user with SVOD access
  2. Navigate to premium video content
  3. Start playback on mobile device
  4. Verify authenticated playback working
  5. Cast to available device mid-playback
  6. Check cast transition

- **Expected Result:**
  1. Mobile SVOD playback requires authentication
  2. JWT token should be valid and fresh
  3. Cast transition should:
     - Transfer current playback position
     - Include JWT in custom data
     - Maintain video quality settings
  4. iOS: `didStartPlayingFeed()` called
  5. Android: `castMlbTvVideo()` executed
  6. No re-authentication needed
  7. Seamless transition under 5 seconds

---

## Test 38: MLBMOB-1222 - VOD: Start cast session then play content

### Enhanced Test Step:
- **Action:**
  1. **Precondition**: Entitled user with cast session active
  2. Ensure cast is connected but idle
  3. Browse to VOD content (highlights/recaps)
  4. Select video to cast
  5. Monitor cast behavior

- **Expected Result:**
  1. Connected cast should show ready state
  2. VOD selection should:
     - Not require authentication
     - Load immediately to cast
     - Show proper metadata (title, thumbnail)
  3. Playback should start within 3 seconds
  4. Controls should include:
     - Full scrubbing capability
     - 10-second skip buttons
     - Quality selection
  5. No JWT token in custom data
  6. `isHighlightContent: true` flag set

---

## Test 39: MLBMOB-1221 - VOD: Start stream on mobile then cast it

### Enhanced Test Step:
- **Action:**
  1. **Precondition**: Entitled user, no active cast
  2. Play VOD content on mobile (game highlight)
  3. Verify smooth playback
  4. Initiate cast while playing
  5. Select target cast device
  6. Observe transition behavior

- **Expected Result:**
  1. VOD plays immediately on mobile (no auth)
  2. Cast icon appears during playback
  3. Cast transition should:
     - Pause mobile playback
     - Transfer current position
     - Start TV playback at same position
  4. Metadata transferred:
     - Video title and description
     - Thumbnail image
     - Duration and position
  5. No authentication delays
  6. Quality adjusts to TV capabilities
  7. Analytics track VOD cast event

---

## Test 40: MLBMOB-1218 - Game: While casting content switch to Game stream

### Enhanced Test Step:
- **Action:**
  1. **Precondition**: Entitled user, VOD/SVOD content casting
  2. Verify non-game content playing on TV
  3. Navigate to live/archived game
  4. Select "Watch" on the game
  5. Choose to cast the game content
  6. Monitor content replacement

- **Expected Result:**
  1. Current cast content should continue initially
  2. Game selection should:
     - Check game entitlements
     - Prepare game stream with auth
     - Prompt for cast replacement
  3. Upon confirmation:
     - Current content stops cleanly
     - Game loads with full metadata
     - Appropriate starting point selected
  4. Game-specific features activate:
     - Live stats (if live game)
     - Commercial skip (if entitled)
     - Multi-angle options
  5. JWT token included for game
  6. Smooth transition under 5 seconds