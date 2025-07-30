"""
AI-Powered Test Step Generator

This module provides functionality to generate proposed test steps for XRAY tests
that don't have steps defined. It uses the test summary, description, and labels
to generate contextually appropriate test steps.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import re

from test_manager import TestSummary, TestStep, XrayTestManager

logger = logging.getLogger(__name__)

@dataclass
class ProposedStep:
    """A proposed test step with confidence score"""
    action: str
    data: str
    result: str
    confidence: float  # 0.0 to 1.0
    reasoning: str  # Why this step was proposed

@dataclass
class StepProposal:
    """Complete proposal for a test"""
    issue_id: str
    test_key: str
    test_summary: str
    proposed_steps: List[ProposedStep]
    overall_confidence: float
    metadata: Dict[str, Any]

class AIStepGenerator:
    """Generate test steps using AI/ML techniques"""
    
    def __init__(self, test_manager: XrayTestManager):
        self.test_manager = test_manager
        self.step_templates = self._load_step_templates()
        self.patterns = self._load_patterns()
    
    def _load_step_templates(self) -> Dict[str, List[Dict]]:
        """Load common test step templates by category"""
        return {
            "login": [
                {"action": "Navigate to login page", "data": "", "result": "Login page is displayed"},
                {"action": "Enter username", "data": "${username}", "result": "Username field is populated"},
                {"action": "Enter password", "data": "${password}", "result": "Password field is populated"},
                {"action": "Click login button", "data": "", "result": "User is logged in successfully"},
                {"action": "Verify successful login", "data": "", "result": "Dashboard or home page is displayed"}
            ],
            "api": [
                {"action": "Send API request", "data": "GET ${endpoint}", "result": "API responds with status 200"},
                {"action": "Verify response structure", "data": "", "result": "Response contains expected fields"},
                {"action": "Validate response data", "data": "", "result": "Response data matches expected values"},
                {"action": "Check response time", "data": "", "result": "Response time is within acceptable limits"}
            ],
            "ui": [
                {"action": "Navigate to ${page}", "data": "", "result": "Page loads successfully"},
                {"action": "Verify page elements", "data": "", "result": "All expected elements are present"},
                {"action": "Interact with ${element}", "data": "${input_data}", "result": "Element responds correctly"},
                {"action": "Validate page behavior", "data": "", "result": "Page functions as expected"}
            ],
            "mobile": [
                {"action": "Launch mobile app", "data": "", "result": "App launches successfully"},
                {"action": "Navigate to ${screen}", "data": "", "result": "Screen is displayed"},
                {"action": "Tap ${element}", "data": "", "result": "Element is activated"},
                {"action": "Verify mobile behavior", "data": "", "result": "App responds correctly"}
            ],
            "navigation": [
                {"action": "Navigate to ${section}", "data": "", "result": "Section loads successfully"},
                {"action": "Verify navigation elements", "data": "", "result": "Navigation menu is displayed"},
                {"action": "Select ${menu_item}", "data": "", "result": "Menu item is selected"},
                {"action": "Verify navigation result", "data": "", "result": "Correct page/section is displayed"}
            ],
            "search": [
                {"action": "Enter search term", "data": "${search_term}", "result": "Search term is entered"},
                {"action": "Execute search", "data": "", "result": "Search is performed"},
                {"action": "Verify search results", "data": "", "result": "Relevant results are displayed"},
                {"action": "Validate result count", "data": "", "result": "Expected number of results shown"}
            ],
            "data_entry": [
                {"action": "Enter required data", "data": "${test_data}", "result": "Data is entered correctly"},
                {"action": "Validate input fields", "data": "", "result": "All fields accept valid input"},
                {"action": "Submit form", "data": "", "result": "Form is submitted successfully"},
                {"action": "Verify data persistence", "data": "", "result": "Data is saved correctly"}
            ],
            "error_handling": [
                {"action": "Enter invalid data", "data": "${invalid_data}", "result": "Validation error is displayed"},
                {"action": "Verify error message", "data": "", "result": "Appropriate error message is shown"},
                {"action": "Correct the error", "data": "${valid_data}", "result": "Error is resolved"},
                {"action": "Proceed with valid data", "data": "", "result": "Process continues successfully"}
            ]
        }
    
    def _load_patterns(self) -> Dict[str, List[str]]:
        """Load keyword patterns for categorizing tests"""
        return {
            "login": ["login", "sign in", "authenticate", "auth", "credential"],
            "api": ["api", "endpoint", "rest", "graphql", "service", "request", "response"],
            "ui": ["ui", "interface", "button", "form", "page", "screen", "display"],
            "mobile": ["mobile", "app", "ios", "android", "device", "touch", "swipe"],
            "navigation": ["navigate", "menu", "browse", "link", "tab", "section"],
            "search": ["search", "filter", "find", "query", "lookup"],
            "data_entry": ["create", "add", "input", "form", "submit", "save"],
            "error_handling": ["error", "invalid", "validation", "exception", "failure"]
        }
    
    def generate_steps_for_test(self, test_summary: TestSummary) -> StepProposal:
        """Generate proposed test steps for a single test"""
        # Get detailed test information
        test_details = self.test_manager.get_test_details(test_summary.issue_id)
        
        # Analyze test content
        analysis = self._analyze_test_content(test_summary, test_details)
        
        # Generate steps based on analysis
        proposed_steps = self._generate_steps_from_analysis(analysis)
        
        # Calculate overall confidence
        overall_confidence = self._calculate_overall_confidence(proposed_steps)
        
        return StepProposal(
            issue_id=test_summary.issue_id,
            test_key=test_summary.key,
            test_summary=test_summary.summary,
            proposed_steps=proposed_steps,
            overall_confidence=overall_confidence,
            metadata=analysis
        )
    
    def _analyze_test_content(self, test_summary: TestSummary, test_details: Dict) -> Dict[str, Any]:
        """Analyze test content to determine appropriate step categories"""
        jira_data = test_details.get("jira", {})
        description = jira_data.get("description", "")
        summary = test_summary.summary.lower()
        desc_lower = description.lower()
        
        # Combine text for analysis
        combined_text = f"{summary} {desc_lower}"
        
        # Identify categories
        categories = []
        category_scores = {}
        
        for category, keywords in self.patterns.items():
            score = 0
            for keyword in keywords:
                if keyword in combined_text:
                    score += combined_text.count(keyword)
            
            if score > 0:
                category_scores[category] = score
                categories.append(category)
        
        # Sort categories by relevance
        categories.sort(key=lambda x: category_scores.get(x, 0), reverse=True)
        
        # Extract key information
        analysis = {
            "categories": categories,
            "category_scores": category_scores,
            "primary_category": categories[0] if categories else "ui",
            "labels": test_summary.labels,
            "priority": test_summary.priority,
            "folder_path": test_summary.folder_path,
            "extracted_entities": self._extract_entities(combined_text),
            "complexity": self._assess_complexity(combined_text)
        }
        
        return analysis
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract entities like pages, elements, data from text"""
        entities = {
            "pages": [],
            "elements": [],
            "actions": [],
            "data": []
        }
        
        # Simple keyword extraction (could be enhanced with NLP)
        page_keywords = ["page", "screen", "view", "dashboard", "home"]
        element_keywords = ["button", "field", "input", "dropdown", "menu", "link"]
        action_keywords = ["click", "tap", "select", "enter", "submit", "verify"]
        
        words = text.lower().split()
        
        for i, word in enumerate(words):
            if word in page_keywords and i > 0:
                entities["pages"].append(words[i-1])
            elif word in element_keywords and i > 0:
                entities["elements"].append(words[i-1])
            elif word in action_keywords:
                entities["actions"].append(word)
        
        return entities
    
    def _assess_complexity(self, text: str) -> str:
        """Assess test complexity based on content"""
        complexity_indicators = {
            "simple": ["basic", "simple", "quick", "single"],
            "medium": ["multiple", "various", "different", "several"],
            "complex": ["complex", "advanced", "integration", "end-to-end", "comprehensive"]
        }
        
        for complexity, indicators in complexity_indicators.items():
            if any(indicator in text.lower() for indicator in indicators):
                return complexity
        
        # Default based on text length
        if len(text) < 100:
            return "simple"
        elif len(text) < 300:
            return "medium"
        else:
            return "complex"
    
    def _generate_steps_from_analysis(self, analysis: Dict[str, Any]) -> List[ProposedStep]:
        """Generate test steps based on analysis"""
        primary_category = analysis["primary_category"]
        complexity = analysis["complexity"]
        entities = analysis["extracted_entities"]
        
        # Get base template
        base_steps = self.step_templates.get(primary_category, self.step_templates["ui"])
        
        # Customize steps based on entities and complexity
        proposed_steps = []
        
        for i, step_template in enumerate(base_steps):
            # Apply entity substitutions
            action = self._apply_substitutions(step_template["action"], entities)
            data = self._apply_substitutions(step_template["data"], entities)
            result = self._apply_substitutions(step_template["result"], entities)
            
            # Calculate confidence based on template match and entity presence
            confidence = self._calculate_step_confidence(step_template, entities, analysis)
            
            # Generate reasoning
            reasoning = self._generate_reasoning(step_template, primary_category, entities)
            
            proposed_step = ProposedStep(
                action=action,
                data=data,
                result=result,
                confidence=confidence,
                reasoning=reasoning
            )
            
            proposed_steps.append(proposed_step)
            
            # Add complexity-based additional steps
            if complexity == "complex" and i == len(base_steps) - 1:
                # Add validation steps for complex tests
                validation_step = ProposedStep(
                    action="Perform additional validation",
                    data="",
                    result="All aspects of functionality are verified",
                    confidence=0.7,
                    reasoning="Added for complex test scenarios"
                )
                proposed_steps.append(validation_step)
        
        return proposed_steps
    
    def _apply_substitutions(self, template: str, entities: Dict[str, List[str]]) -> str:
        """Apply entity substitutions to template strings"""
        result = template
        
        # Replace common placeholders
        replacements = {
            "${page}": entities["pages"][0] if entities["pages"] else "target page",
            "${screen}": entities["pages"][0] if entities["pages"] else "target screen",
            "${element}": entities["elements"][0] if entities["elements"] else "target element",
            "${username}": "test_user",
            "${password}": "test_password",
            "${endpoint}": "/api/test/endpoint",
            "${search_term}": "test query",
            "${test_data}": "test data",
            "${invalid_data}": "invalid input",
            "${valid_data}": "valid input"
        }
        
        for placeholder, replacement in replacements.items():
            result = result.replace(placeholder, replacement)
        
        return result
    
    def _calculate_step_confidence(self, step_template: Dict, entities: Dict, analysis: Dict) -> float:
        """Calculate confidence score for a proposed step"""
        base_confidence = 0.8
        
        # Adjust based on category match
        primary_category = analysis["primary_category"]
        category_score = analysis["category_scores"].get(primary_category, 0)
        
        if category_score > 2:
            base_confidence += 0.1
        elif category_score > 1:
            base_confidence += 0.05
        
        # Adjust based on entity presence
        if entities["pages"] or entities["elements"]:
            base_confidence += 0.05
        
        # Adjust based on complexity
        complexity = analysis["complexity"]
        if complexity == "simple":
            base_confidence += 0.05
        elif complexity == "complex":
            base_confidence -= 0.1
        
        return min(1.0, max(0.1, base_confidence))
    
    def _generate_reasoning(self, step_template: Dict, category: str, entities: Dict) -> str:
        """Generate reasoning for why this step was proposed"""
        reasons = []
        
        if category in step_template.get("action", "").lower():
            reasons.append(f"Step aligns with {category} test pattern")
        
        if entities["pages"]:
            reasons.append("Page entities detected in test description")
        
        if entities["elements"]:
            reasons.append("UI elements identified in test context")
        
        if not reasons:
            reasons.append("Standard test step based on common patterns")
        
        return "; ".join(reasons)
    
    def _calculate_overall_confidence(self, proposed_steps: List[ProposedStep]) -> float:
        """Calculate overall confidence for the entire proposal"""
        if not proposed_steps:
            return 0.0
        
        # Average confidence with weight on higher-confidence steps
        confidences = [step.confidence for step in proposed_steps]
        weighted_avg = sum(confidences) / len(confidences)
        
        # Boost confidence if we have good coverage
        if len(proposed_steps) >= 3:
            weighted_avg += 0.05
        
        return min(1.0, weighted_avg)
    
    def generate_steps_for_multiple_tests(self, test_summaries: List[TestSummary]) -> List[StepProposal]:
        """Generate steps for multiple tests"""
        proposals = []
        
        for test_summary in test_summaries:
            try:
                proposal = self.generate_steps_for_test(test_summary)
                proposals.append(proposal)
                logger.info(f"Generated {len(proposal.proposed_steps)} steps for {test_summary.key}")
                
            except Exception as e:
                logger.error(f"Failed to generate steps for {test_summary.key}: {e}")
        
        return proposals
    
    def export_proposals_to_json(self, proposals: List[StepProposal], output_file: str) -> None:
        """Export step proposals to JSON file"""
        try:
            proposals_data = [asdict(proposal) for proposal in proposals]
            
            export_data = {
                "generated_at": "2025-07-18T00:00:00Z",  # Using current date from env
                "total_proposals": len(proposals_data),
                "proposals": proposals_data
            }
            
            with open(output_file, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"Exported {len(proposals_data)} step proposals to {output_file}")
            
        except Exception as e:
            logger.error(f"Failed to export proposals: {e}")
            raise

# Example usage
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    # Create components
    test_manager = XrayTestManager()
    step_generator = AIStepGenerator(test_manager)
    
    try:
        # Get tests without steps
        tests_without_steps = test_manager.get_tests_without_steps("MLB", limit=3)
        print(f"Found {len(tests_without_steps)} tests without steps")
        
        # Generate step proposals
        proposals = step_generator.generate_steps_for_multiple_tests(tests_without_steps)
        
        # Display proposals
        for proposal in proposals:
            print(f"\n=== {proposal.test_key}: {proposal.test_summary} ===")
            print(f"Confidence: {proposal.overall_confidence:.2f}")
            print(f"Primary Category: {proposal.metadata['primary_category']}")
            
            for i, step in enumerate(proposal.proposed_steps, 1):
                print(f"  Step {i}: {step.action}")
                print(f"    Data: {step.data}")
                print(f"    Result: {step.result}")
                print(f"    Confidence: {step.confidence:.2f}")
                print(f"    Reasoning: {step.reasoning}")
        
        # Export to JSON
        step_generator.export_proposals_to_json(proposals, "step_proposals.json")
        
    except Exception as e:
        print(f"Error: {e}")