#!/usr/bin/env python3
"""
Create generic preconditions that can be reused across multiple tests
"""

import json
from pathlib import Path

# Define generic preconditions that cover multiple specific cases
GENERIC_PRECONDITIONS = [
    {
        "summary": "API Test Environment Ready",
        "description": """Generic precondition for API tests:
1. Test environment is properly configured
2. All required API endpoints are accessible
3. Valid test data is available
4. Authentication tokens are configured (if required)
5. Network connectivity is stable""",
        "covers": [
            "API endpoint accessible",
            "Valid test data configured",
            "Test environment configured",
            "Security testing environment",
            "Load testing environment available",
            "Public endpoint available",
            "Upstream services available"
        ]
    },
    {
        "summary": "Game State Test Data Available",
        "description": """Generic precondition for game state testing:
1. Various game states are available in test data
2. Live, completed, postponed, and scheduled games exist
3. Special game states (rain delay, suspended, etc.) can be simulated
4. Game state transitions can be tested""",
        "covers": [
            "Game in delayed state",
            "Game suspended",
            "Postponed game available",
            "Completed game available",
            "Scheduled game available",
            "Game in warmup state",
            "Game state data available",
            "Game state transitions available",
            "Multiple games available"
        ]
    },
    {
        "summary": "Jewel Event Test Environment",
        "description": """Generic precondition for jewel event testing:
1. Jewel event test data is configured
2. Various event types can be simulated (Opening Day, All-Star, Postseason, etc.)
3. Event metadata is properly configured
4. Multiple events can be active simultaneously""",
        "covers": [
            "Opening Day active",
            "All-Star Game active",
            "Spring Training active",
            "Team qualified for playoffs",
            "Team in World Series",
            "International Series active",
            "Multiple events active",
            "Jewel event metadata available"
        ]
    },
    {
        "summary": "Localization Test Environment",
        "description": """Generic precondition for localization testing:
1. Multiple languages are configured (English, Spanish, Japanese)
2. Localized content is available for all supported languages
3. Language switching is properly configured
4. Timezone data for various regions is available""",
        "covers": [
            "English language supported",
            "Spanish language supported",
            "Japanese language supported",
            "Localization supported",
            "Various timezone data available"
        ]
    },
    {
        "summary": "Mobile App Test Environment",
        "description": """Generic precondition for mobile app testing:
1. iOS and Android test apps are available
2. iPad-specific features are testable
3. Device orientation can be changed
4. Analytics tracking is enabled
5. Performance baselines are established""",
        "covers": [
            "iOS app available",
            "Android app available",
            "iPad app available",
            "Device orientation unlocked",
            "Analytics tracking enabled",
            "Performance baseline established"
        ]
    }
]

def get_precondition_mapping():
    """Create mapping of all specific preconditions to generic ones"""
    mapping = {}
    
    # Add existing JIRA preconditions
    existing_mappings = {
        "Valid team ID available": "FRAMED-1355",
        "User on Team Page": "FRAMED-1356",
        "Selected team has a live game": "FRAMED-1357",
        "Live game in progress": "FRAMED-1357",
        "HRD is scheduled": "FRAMED-1358",
        "Device language set to Spanish": "FRAMED-1359",
        "Device language set to Japanese": "FRAMED-1360",
        "Testing during Opening Day period": "FRAMED-1361",
        "Testing during All-Star period": "FRAMED-1362",
        "Team qualified for postseason": "FRAMED-1363",
        "Team in World Series": "FRAMED-1364",
        "Spring Training period active": "FRAMED-1365",
        "Team playing in International Series": "FRAMED-1366",
        "Multiple jewel events active": "FRAMED-1367",
        "Team has game in warmup state": "FRAMED-1368",
        "Game in rain delay": "FRAMED-1369",
        "Suspended game with scheduled resume": "FRAMED-1370",
        "Live game with active challenge": "FRAMED-1371",
        "Recently postponed game": "FRAMED-1372",
        "Forfeit game (rare)": "FRAMED-1373",
        "Team playing doubleheader": "FRAMED-1374",
        "Game in extra innings": "FRAMED-1375"
    }
    
    mapping.update(existing_mappings)
    
    # Map remaining preconditions to generic ones (to be created)
    for generic in GENERIC_PRECONDITIONS:
        for specific in generic["covers"]:
            if specific not in mapping:
                mapping[specific] = f"GENERIC_{generic['summary'][:20]}"
    
    return mapping

def save_precondition_plan():
    """Save the precondition creation plan"""
    plan = {
        "generic_preconditions_to_create": GENERIC_PRECONDITIONS,
        "total_generic": len(GENERIC_PRECONDITIONS),
        "total_specific_covered": sum(len(g["covers"]) for g in GENERIC_PRECONDITIONS),
        "mapping": get_precondition_mapping()
    }
    
    plan_file = Path(__file__).parent.parent / 'logs' / 'generic_precondition_plan.json'
    with open(plan_file, 'w') as f:
        json.dump(plan, f, indent=2)
    
    print("Generic Precondition Plan:")
    print(f"  - Generic preconditions to create: {len(GENERIC_PRECONDITIONS)}")
    print(f"  - Specific cases covered: {plan['total_specific_covered']}")
    print(f"\nGeneric preconditions:")
    for g in GENERIC_PRECONDITIONS:
        print(f"  - {g['summary']} (covers {len(g['covers'])} cases)")
    
    return plan

if __name__ == "__main__":
    save_precondition_plan()