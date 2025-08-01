#!/usr/bin/env python3
"""
Process discovery results and prepare for test upload
"""

import json
from pathlib import Path
from datetime import datetime

# Discovery results from JIRA
existing_preconditions = {
    "App is on Team Page": "FRAMED-1356",
    "User has the app installed and opened": "FRAMED-1355",
    "Selected team has a live game": "FRAMED-1357",
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
    "Game in extra innings": "FRAMED-1375",
    "MLB App Setup": "FRAMED-1376",
    "Team Page Navigation": "FRAMED-1377"
}

# Map our JSON preconditions to existing ones
precondition_mapping = {
    # API test preconditions
    "Valid team ID available": "FRAMED-1355",  # Maps to "User has the app installed and opened"
    "User on Team Page": "FRAMED-1356",
    "Valid MIG data present": "FRAMED-1357",  # Maps to "Selected team has a live game"
    "Live game in progress": "FRAMED-1357",
    "API endpoints accessible": "FRAMED-1355",
    "Valid test data configured": "FRAMED-1355",
    "Different game states available": None,  # Need to create
    "App in required state": "FRAMED-1355",
    "Game in postponed state": "FRAMED-1372",
    "Special event active": None,  # Need to create - generic special event
    "Video content available": None,  # Need to create
    "Device orientation unlocked": None,  # Need to create
    "Analytics tracking enabled": None,  # Need to create
    "Empty state conditions configured": None,  # Need to create
    "Paginated content available": None,  # Need to create
    "Offline state testable": None,  # Need to create
    "Spanish language content available": "FRAMED-1359",
    "Japanese language content available": "FRAMED-1360",
    "Security test endpoint available": None,  # Need to create
    "Test environment configured": "FRAMED-1355"
}

def extract_all_preconditions():
    """Extract unique preconditions from both JSON files"""
    preconditions_needed = set()
    
    # Process API tests
    api_file = Path(__file__).parent.parent / 'test-data' / 'api_tests_xray.json'
    with open(api_file, 'r') as f:
        api_data = json.load(f)
    
    for test in api_data['testSuite']['testCases']:
        if 'preconditions' in test and test['preconditions']:
            preconditions_needed.add(test['preconditions'])
    
    print(f"Found {len(preconditions_needed)} unique preconditions in API tests")
    
    # Check functional tests for any in descriptions
    functional_file = Path(__file__).parent.parent / 'test-data' / 'functional_tests_xray.json'
    with open(functional_file, 'r') as f:
        functional_data = json.load(f)
    
    # Functional tests don't have explicit preconditions field
    # But they might need the basic setup ones
    
    return list(preconditions_needed)

def create_precondition_plan():
    """Create a plan for which preconditions need to be created"""
    all_preconditions = extract_all_preconditions()
    
    to_create = []
    to_reuse = []
    
    for precondition in all_preconditions:
        if precondition in precondition_mapping:
            mapped_key = precondition_mapping[precondition]
            if mapped_key:
                to_reuse.append({
                    "text": precondition,
                    "jira_key": mapped_key
                })
            else:
                to_create.append(precondition)
        else:
            # Not in mapping, need to create
            to_create.append(precondition)
    
    plan = {
        "timestamp": datetime.now().isoformat(),
        "to_create": to_create,
        "to_reuse": to_reuse,
        "existing_count": len(existing_preconditions),
        "create_count": len(to_create),
        "reuse_count": len(to_reuse)
    }
    
    # Save plan
    plan_file = Path(__file__).parent.parent / 'logs' / 'precondition_plan.json'
    with open(plan_file, 'w') as f:
        json.dump(plan, f, indent=2)
    
    print("\nPrecondition Plan:")
    print(f"  - Existing in JIRA: {len(existing_preconditions)}")
    print(f"  - Will reuse: {len(to_reuse)}")
    print(f"  - Need to create: {len(to_create)}")
    
    if to_create:
        print("\nPreconditions to create:")
        for pc in to_create:
            print(f"  - {pc}")
    
    return plan

if __name__ == "__main__":
    create_precondition_plan()