#!/bin/bash
# Manual update script for functional tests
# Generated: 2025-08-01T14:26:07.936123
# NOTE: Requires JIRA_EMAIL and JIRA_API_TOKEN environment variables

if [ -z "$JIRA_EMAIL" ] || [ -z "$JIRA_API_TOKEN" ]; then
    echo "Error: JIRA_EMAIL and JIRA_API_TOKEN environment variables must be set"
    exit 1
fi

JIRA_BASE_URL="https://jira.mlbinfra.com"

echo "=== UPDATING FUNCTIONAL TESTS ==="

echo "Updating FRAMED-1632..."
curl -X PUT \
  -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -d '{"fields": {"labels": ["android", "critical", "functional_test", "high", "ios", "manual", "navigation", "smoke", "team_page"], "priority": {"name": "Critical"}}}' \
  "$JIRA_BASE_URL/rest/api/2/issue/FRAMED-1632"
echo

echo "Updating FRAMED-1633..."
curl -X PUT \
  -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -d '{"fields": {"labels": ["android", "functional_test", "ios", "manual", "medium", "navigation", "team_page"], "priority": {"name": "Medium"}}}' \
  "$JIRA_BASE_URL/rest/api/2/issue/FRAMED-1633"
echo

echo "Updating FRAMED-1634..."
curl -X PUT \
  -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -d '{"fields": {"labels": ["android", "critical", "functional_test", "game_state", "high", "ios", "live_state", "manual", "requires_live_game", "team_page"], "priority": {"name": "Critical"}}}' \
  "$JIRA_BASE_URL/rest/api/2/issue/FRAMED-1634"
echo

echo "Updating FRAMED-1635..."
curl -X PUT \
  -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -d '{"fields": {"labels": ["android", "critical", "date_bar", "functional_test", "high", "ios", "manual", "navigation", "team_page"], "priority": {"name": "Critical"}}}' \
  "$JIRA_BASE_URL/rest/api/2/issue/FRAMED-1635"
echo

echo "Updating FRAMED-1636..."
curl -X PUT \
  -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -d '{"fields": {"labels": ["all_star", "android", "functional_test", "ios", "jewel_event", "manual", "medium", "team_page"], "priority": {"name": "Medium"}}}' \
  "$JIRA_BASE_URL/rest/api/2/issue/FRAMED-1636"
echo

echo "Updating FRAMED-1637..."
curl -X PUT \
  -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -d '{"fields": {"labels": ["android", "content_display", "critical", "functional_test", "high", "ios", "manual", "navigation", "team_page"], "priority": {"name": "Critical"}}}' \
  "$JIRA_BASE_URL/rest/api/2/issue/FRAMED-1637"
echo

echo "Updating FRAMED-1638..."
curl -X PUT \
  -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -d '{"fields": {"labels": ["android", "content_display", "critical", "functional_test", "high", "ios", "manual", "team_page"], "priority": {"name": "Critical"}}}' \
  "$JIRA_BASE_URL/rest/api/2/issue/FRAMED-1638"
echo

echo "Updating FRAMED-1639..."
curl -X PUT \
  -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -d '{"fields": {"labels": ["android", "content_display", "functional_test", "ios", "manual", "medium", "team_page"], "priority": {"name": "Medium"}}}' \
  "$JIRA_BASE_URL/rest/api/2/issue/FRAMED-1639"
echo

echo "Updating FRAMED-1640..."
curl -X PUT \
  -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -d '{"fields": {"labels": ["android", "critical", "functional_test", "high", "ios", "localization", "manual", "team_page"], "priority": {"name": "Critical"}}}' \
  "$JIRA_BASE_URL/rest/api/2/issue/FRAMED-1640"
echo

echo "Updating FRAMED-1641..."
curl -X PUT \
  -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -d '{"fields": {"labels": ["android", "functional_test", "ios", "localization", "manual", "medium", "team_page"], "priority": {"name": "Medium"}}}' \
  "$JIRA_BASE_URL/rest/api/2/issue/FRAMED-1641"
echo

echo "Updating FRAMED-1642..."
curl -X PUT \
  -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -d '{"fields": {"labels": ["android", "critical", "functional_test", "high", "ios", "manual", "navigation", "team_page"], "priority": {"name": "Critical"}}}' \
  "$JIRA_BASE_URL/rest/api/2/issue/FRAMED-1642"
echo

echo "Updating FRAMED-1643..."
curl -X PUT \
  -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -d '{"fields": {"labels": ["android", "critical", "functional_test", "high", "ios", "manual", "navigation", "product_links", "team_page"], "priority": {"name": "Critical"}}}' \
  "$JIRA_BASE_URL/rest/api/2/issue/FRAMED-1643"
echo

echo "Updating FRAMED-1644..."
curl -X PUT \
  -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -d '{"fields": {"labels": ["android", "critical", "functional_test", "high", "ios", "manual", "performance", "smoke", "team_page"], "priority": {"name": "Critical"}}}' \
  "$JIRA_BASE_URL/rest/api/2/issue/FRAMED-1644"
echo

echo "Updating FRAMED-1645..."
curl -X PUT \
  -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -d '{"fields": {"labels": ["android", "functional_test", "ios", "manual", "medium", "navigation", "performance", "team_page"], "priority": {"name": "Medium"}}}' \
  "$JIRA_BASE_URL/rest/api/2/issue/FRAMED-1645"
echo

echo "Updating FRAMED-1646..."
curl -X PUT \
  -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -d '{"fields": {"labels": ["android", "critical", "functional_test", "high", "ios", "manual", "regression", "team_page"], "priority": {"name": "Critical"}}}' \
  "$JIRA_BASE_URL/rest/api/2/issue/FRAMED-1646"
echo

echo "Updating FRAMED-1647..."
curl -X PUT \
  -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -d '{"fields": {"labels": ["android", "functional_test", "ios", "manual", "medium", "regression", "team_page"], "priority": {"name": "Medium"}}}' \
  "$JIRA_BASE_URL/rest/api/2/issue/FRAMED-1647"
echo

echo "Updating FRAMED-1648..."
curl -X PUT \
  -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -d '{"fields": {"labels": ["accessibility", "android", "critical", "functional_test", "high", "ios", "manual", "talkback", "team_page", "voiceover"], "priority": {"name": "Critical"}}}' \
  "$JIRA_BASE_URL/rest/api/2/issue/FRAMED-1648"
echo

echo "Updating FRAMED-1649..."
curl -X PUT \
  -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -d '{"fields": {"labels": ["accessibility", "android", "functional_test", "ios", "manual", "medium", "team_page"], "priority": {"name": "Medium"}}}' \
  "$JIRA_BASE_URL/rest/api/2/issue/FRAMED-1649"
echo

echo "Updating FRAMED-1650..."
curl -X PUT \
  -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -d '{"fields": {"labels": ["android", "critical", "cross_platform", "functional_test", "high", "ios", "manual", "team_page"], "priority": {"name": "Critical"}}}' \
  "$JIRA_BASE_URL/rest/api/2/issue/FRAMED-1650"
echo

echo "Updating FRAMED-1651..."
curl -X PUT \
  -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -d '{"fields": {"labels": ["android", "critical", "functional_test", "high", "ios", "ipad", "manual", "matchup_display", "team_page"], "priority": {"name": "Critical"}}}' \
  "$JIRA_BASE_URL/rest/api/2/issue/FRAMED-1651"
echo

echo "Updating FRAMED-1652..."
curl -X PUT \
  -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -d '{"fields": {"labels": ["analytics", "android", "functional_test", "ios", "manual", "medium", "team_page"], "priority": {"name": "Medium"}}}' \
  "$JIRA_BASE_URL/rest/api/2/issue/FRAMED-1652"
echo

echo "Updating FRAMED-1653..."
curl -X PUT \
  -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -d '{"fields": {"labels": ["android", "critical", "functional_test", "high", "ios", "jewel_event", "manual", "opening_day", "team_page"], "priority": {"name": "Critical"}}}' \
  "$JIRA_BASE_URL/rest/api/2/issue/FRAMED-1653"
echo

echo "Updating FRAMED-1654..."
curl -X PUT \
  -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -d '{"fields": {"labels": ["all_star", "android", "critical", "functional_test", "high", "ios", "jewel_event", "manual", "team_page"], "priority": {"name": "Critical"}}}' \
  "$JIRA_BASE_URL/rest/api/2/issue/FRAMED-1654"
echo

echo "Updating FRAMED-1655..."
curl -X PUT \
  -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -d '{"fields": {"labels": ["android", "critical", "functional_test", "high", "ios", "jewel_event", "manual", "postseason", "team_page"], "priority": {"name": "Critical"}}}' \
  "$JIRA_BASE_URL/rest/api/2/issue/FRAMED-1655"
echo

echo "Updating FRAMED-1656..."
curl -X PUT \
  -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -d '{"fields": {"labels": ["android", "critical", "functional_test", "high", "ios", "jewel_event", "manual", "team_page", "world_series"], "priority": {"name": "Critical"}}}' \
  "$JIRA_BASE_URL/rest/api/2/issue/FRAMED-1656"
echo

echo "Updating FRAMED-1657..."
curl -X PUT \
  -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -d '{"fields": {"labels": ["android", "functional_test", "ios", "jewel_event", "manual", "medium", "spring_training", "team_page"], "priority": {"name": "Medium"}}}' \
  "$JIRA_BASE_URL/rest/api/2/issue/FRAMED-1657"
echo

echo "Updating FRAMED-1658..."
curl -X PUT \
  -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -d '{"fields": {"labels": ["android", "functional_test", "international", "ios", "jewel_event", "manual", "medium", "team_page"], "priority": {"name": "Medium"}}}' \
  "$JIRA_BASE_URL/rest/api/2/issue/FRAMED-1658"
echo

echo "Updating FRAMED-1659..."
curl -X PUT \
  -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -d '{"fields": {"labels": ["android", "functional_test", "ios", "jewel_event", "manual", "medium", "team_page"], "priority": {"name": "Medium"}}}' \
  "$JIRA_BASE_URL/rest/api/2/issue/FRAMED-1659"
echo

echo "Updating FRAMED-1660..."
curl -X PUT \
  -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -d '{"fields": {"labels": ["android", "critical", "functional_test", "game_state", "high", "ios", "manual", "preview_state", "team_page"], "priority": {"name": "Critical"}}}' \
  "$JIRA_BASE_URL/rest/api/2/issue/FRAMED-1660"
echo

echo "Updating FRAMED-1661..."
curl -X PUT \
  -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -d '{"fields": {"labels": ["android", "critical", "delayed_state", "functional_test", "game_state", "high", "ios", "manual", "team_page"], "priority": {"name": "Critical"}}}' \
  "$JIRA_BASE_URL/rest/api/2/issue/FRAMED-1661"
echo

echo "Updating FRAMED-1662..."
curl -X PUT \
  -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -d '{"fields": {"labels": ["android", "critical", "functional_test", "game_state", "high", "ios", "manual", "suspended_state", "team_page"], "priority": {"name": "Critical"}}}' \
  "$JIRA_BASE_URL/rest/api/2/issue/FRAMED-1662"
echo

echo "Updating FRAMED-1663..."
curl -X PUT \
  -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -d '{"fields": {"labels": ["android", "functional_test", "game_state", "ios", "live_state", "manual", "medium", "team_page"], "priority": {"name": "Medium"}}}' \
  "$JIRA_BASE_URL/rest/api/2/issue/FRAMED-1663"
echo

echo "Updating FRAMED-1664..."
curl -X PUT \
  -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -d '{"fields": {"labels": ["android", "critical", "final_state", "functional_test", "game_state", "high", "ios", "manual", "team_page"], "priority": {"name": "Critical"}}}' \
  "$JIRA_BASE_URL/rest/api/2/issue/FRAMED-1664"
echo

echo "Updating FRAMED-1665..."
curl -X PUT \
  -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -d '{"fields": {"labels": ["android", "final_state", "functional_test", "game_state", "ios", "low", "manual", "team_page"], "priority": {"name": "Low"}}}' \
  "$JIRA_BASE_URL/rest/api/2/issue/FRAMED-1665"
echo

echo "Updating FRAMED-1666..."
curl -X PUT \
  -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -d '{"fields": {"labels": ["android", "critical", "functional_test", "game_state", "high", "ios", "manual", "state_transition", "team_page"], "priority": {"name": "Critical"}}}' \
  "$JIRA_BASE_URL/rest/api/2/issue/FRAMED-1666"
echo

echo "Updating FRAMED-1631..."
curl -X PUT \
  -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -d '{"fields": {"labels": ["android", "critical", "functional_test", "game_state", "high", "ios", "manual", "team_page"], "priority": {"name": "Critical"}}}' \
  "$JIRA_BASE_URL/rest/api/2/issue/FRAMED-1631"
echo

echo "\n=== UPDATE COMPLETE ==="
