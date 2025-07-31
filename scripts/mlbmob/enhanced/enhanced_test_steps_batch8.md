# Enhanced Test Steps - Batch 8 (Tests 71-76)

## Test 71: MLBMOB-651 - TC05 - Gameday video context (Duplicate)

### Enhanced Test Step:
- **Action:**
  1. Open any game in Gameday view
  2. Navigate to video-related tabs/sections
  3. Look for contextual video content:
     - Highlights tab
     - Key moments
     - In-game clips
  4. Play various video types
  5. Check video player integration
  6. Verify content updates for live games

- **Expected Result:**
  1. Gameday includes dedicated video sections
  2. Video content specific to current game:
     - Real-time highlights
     - Key plays and moments
     - Pitcher/batter matchups
     - Scoring plays
  3. Videos organized by:
     - Inning (for live/recent games)
     - Play type
     - Player involved
  4. Seamless playback within Gameday
  5. Player controls overlay Gameday UI
  6. Live games show new videos as available
  7. Analytics include gameday_context tag

---

## Test 72: MLBMOB-650 - TC04 - Scores page video context (Duplicate)

### Enhanced Test Step:
- **Action:**
  1. Go to Scores/Scoreboard tab
  2. Look for video indicators on games
  3. Identify different video types:
     - Recap videos
     - Live look-ins
     - Condensed games
  4. Access videos from score cards
  5. Test inline vs full-screen playback
  6. Check video availability by game status

- **Expected Result:**
  1. Score cards show video availability icons
  2. Video options based on game status:
     - Live: Live look-in available
     - Final: Recap and condensed game
     - In Progress: Latest highlights
  3. Quick access without leaving scores
  4. Video preview on hover/long-press
  5. Smooth transition to video player
  6. Return to scores maintains position
  7. Analytics track scores_video_play events

---

## Test 73: MLBMOB-649 - TC03 - Team page video context (Duplicate)

### Enhanced Test Step:
- **Action:**
  1. Navigate to any team's page
  2. Locate video content section
  3. Verify team-filtered content
  4. Browse video categories:
     - Recent games
     - Player highlights
     - Team features
  5. Play videos and check metadata
  6. Test related video suggestions

- **Expected Result:**
  1. Prominent video section on team page
  2. All content filtered for selected team
  3. Video categories include:
     - Game highlights
     - Player interviews
     - Behind the scenes
     - Classic moments
  4. Thumbnail previews load quickly
  5. Video player shows team branding
  6. Related videos stay team-specific
  7. Share functionality includes team context

---

## Test 74: MLBMOB-648 - TC02 - Home tab video context (Duplicate)

### Enhanced Test Step:
- **Action:**
  1. Navigate to Home/Feed tab
  2. Scroll to identify video modules
  3. Check different module types:
     - Featured videos
     - MLB.tv content
     - Trending highlights
  4. Interact with video carousels
  5. Play videos from different sources
  6. Verify personalization

- **Expected Result:**
  1. Multiple video modules in home feed
  2. Module types displayed:
     - Hero video (large featured)
     - Carousel of highlights
     - MLB.tv games (if subscribed)
     - Recommended content
  3. Smooth carousel navigation
  4. Videos personalized by:
     - Favorite teams
     - Watch history
     - Trending content
  5. Quick play with minimal loading
  6. Module-specific layouts optimized
  7. Cross-platform viewing sync

---

## Test 75: MLBMOB-645 - TC45 - Spring training tab config (Duplicate)

### Enhanced Test Step:
- **Action:**
  1. During spring training (Feb-March)
  2. Check for spring training section
  3. Navigate to spring content
  4. Verify special configurations:
     - League splits (Grapefruit/Cactus)
     - Squad games
     - Exhibition games
  5. Check standings format
  6. Test game navigation

- **Expected Result:**
  1. Spring training tab/section visible
  2. Games marked with GameType "S"
  3. Special features:
     - Split squad indicators
     - Simplified statistics
     - Exhibition game labels
     - Practice game info
  4. Standings show:
     - Win/loss only
     - League divisions
     - No playoff implications
  5. Remote config controls visibility
  6. Transitions to regular season smoothly
  7. Spring-specific news and content

---

## Test 76: MLBMOB-644 - TC34 - Next Game is displayed (Duplicate)

### Enhanced Test Step:
- **Action:**
  1. Go to team page or schedule view
  2. Find "Next Game" section/widget
  3. Verify all game details shown
  4. Test interactive elements:
     - Add to calendar
     - Buy tickets
     - Set reminder
     - Share game
  5. Check countdown functionality
  6. Navigate to game details

- **Expected Result:**
  1. Next game prominently displayed
  2. Complete game information:
     - Teams and records
     - Date/time (user's timezone)
     - Venue and location
     - TV/Radio broadcasts
     - Probable pitchers
  3. Countdown timer for games <24hrs
  4. Interactive options work:
     - Calendar adds event
     - Tickets link to purchase
     - Reminder sets notification
     - Share creates proper link
  5. Updates when current game ends
  6. Handles edge cases:
     - Doubleheaders
     - Postponements
     - Off days