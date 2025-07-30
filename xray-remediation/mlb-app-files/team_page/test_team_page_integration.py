"""Team Page API Integration, Security, Error Handling, Data Validation and Regression tests."""

import pytest
import allure
import requests
import time
import json
import os
from datetime import datetime
from jsonschema import ValidationError
from lib.validators import (
    validate_bullpen_response,
    validate_mig_section,
    validate_mig_carousel_section,
    validate_screens_reference_sections,
    validate_team_specific_content,
    validate_response_contains_refresh_action,
    validate_response_language
)
from lib.utils import (
    find_refresh_actions, 
    get_game_state, 
    find_game_cards,
    assert_valid_bullpen_response,
    assert_status_code
)


@allure.epic("Bullpen API")
@allure.feature("Team Page Endpoint")
class TestTeamPageIntegration:
    """Integration test cases for Team Page endpoints."""
    
    @pytest.mark.api
    @pytest.mark.team_page
    @pytest.mark.high
    @pytest.mark.cross_platform
    @pytest.mark.integration
    @allure.story("Integration Tests")
    @allure.title("API-INT-001: Upstream Service Integration")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("API-INT-001")
    def test_upstream_service_integration(self, api_client, valid_team_id, timezone_headers):
        """
        Test Case ID: API-INT-001
        Verify integration with upstream services.
        """
        response = api_client.get_team_page(valid_team_id, headers=timezone_headers)
        
        assert_status_code(response, 200, context=f"team_page upstream_integration")