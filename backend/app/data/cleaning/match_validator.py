"""
Match Validator Module for World Cup data.

This module provides validation functions to ensure data consistency
and integrity when converting text files to JSON format.

Location: backend/app/data/cleaning/match_validator.py
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import re

from app.data.cleaning.team_normalizer import get_team_info


@dataclass
class ValidationResult:
    """Result of validation operations."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def add_error(self, message: str) -> None:
        """Add an error and mark as invalid."""
        self.errors.append(message)
        self.is_valid = False
    
    def add_warning(self, message: str) -> None:
        """Add a warning (doesn't affect validity)."""
        self.warnings.append(message)
    
    def merge(self, other: 'ValidationResult') -> None:
        """Merge another validation result into this one."""
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        if not other.is_valid:
            self.is_valid = False


# =============================================================================
# Validation Functions
# =============================================================================

def validate_match(match: Dict[str, Any], is_knockout: bool = False) -> ValidationResult:
    """
    Validate a single match object.
    
    Args:
        match: Dictionary containing match data
        is_knockout: Whether this is a knockout stage match
        
    Returns:
        ValidationResult with any errors or warnings
    """
    result = ValidationResult(is_valid=True)
    
    # Required fields
    required_fields = ['team1', 'team2', 'score1', 'score2', 'date']
    for field_name in required_fields:
        if field_name not in match:
            result.add_error(f"Missing required field: {field_name}")
    
    if not result.is_valid:
        return result
    
    # Validate teams
    result.merge(_validate_teams(match))
    
    # Validate scores
    result.merge(_validate_scores(match, is_knockout))
    
    # Validate date
    result.merge(_validate_date(match.get('date', '')))
    
    # Validate time if present
    if 'time' in match and match['time']:
        result.merge(_validate_time(match['time']))
    
    # Validate goals consistency
    result.merge(_validate_goals_consistency(match))
    
    # Validate knockout-specific fields
    if is_knockout or match.get('knockout', False):
        result.merge(_validate_knockout_fields(match))
    
    return result


def _validate_teams(match: Dict[str, Any]) -> ValidationResult:
    """Validate team information."""
    result = ValidationResult(is_valid=True)
    
    team1 = match.get('team1', {})
    team2 = match.get('team2', {})
    
    # Handle both nested and flat formats
    if isinstance(team1, dict):
        team1_name = team1.get('name', '')
        team1_code = team1.get('code', '')
    else:
        team1_name = str(team1)
        team1_code = ''
    
    if isinstance(team2, dict):
        team2_name = team2.get('name', '')
        team2_code = team2.get('code', '')
    else:
        team2_name = str(team2)
        team2_code = ''
    
    # Check if team names are not empty
    if not team1_name:
        result.add_error("Team 1 name is empty")
    if not team2_name:
        result.add_error("Team 2 name is empty")
    
    # Check if teams are different
    if team1_name and team2_name and team1_name == team2_name:
        result.add_error(f"Team 1 and Team 2 are the same: {team1_name}")
    
    # Validate team codes if present
    if team1_code and len(team1_code) != 3:
        result.add_warning(f"Team 1 code '{team1_code}' is not 3 characters")
    if team2_code and len(team2_code) != 3:
        result.add_warning(f"Team 2 code '{team2_code}' is not 3 characters")
    
    # Check if teams are in database
    if team1_name and not get_team_info(team1_name):
        result.add_warning(f"Team '{team1_name}' not found in database")
    if team2_name and not get_team_info(team2_name):
        result.add_warning(f"Team '{team2_name}' not found in database")
    
    return result


def _validate_scores(match: Dict[str, Any], is_knockout: bool = False) -> ValidationResult:
    """Validate score fields."""
    result = ValidationResult(is_valid=True)
    
    score1 = match.get('score1')
    score2 = match.get('score2')
    
    # Check if scores are non-negative integers
    if not isinstance(score1, int) or score1 < 0:
        result.add_error(f"Invalid score1: {score1}")
    if not isinstance(score2, int) or score2 < 0:
        result.add_error(f"Invalid score2: {score2}")
    
    # Check halftime scores if present
    score1i = match.get('score1i')
    score2i = match.get('score2i')
    
    if score1i is not None and score2i is not None:
        if not isinstance(score1i, int) or score1i < 0:
            result.add_error(f"Invalid halftime score1i: {score1i}")
        if not isinstance(score2i, int) or score2i < 0:
            result.add_error(f"Invalid halftime score2i: {score2i}")
        
        # Halftime scores should be <= final scores for regular matches
        if isinstance(score1, int) and isinstance(score1i, int):
            if score1i > score1 and not is_knockout:
                result.add_warning(f"Halftime score1 ({score1i}) > final score1 ({score1})")
        if isinstance(score2, int) and isinstance(score2i, int):
            if score2i > score2 and not is_knockout:
                result.add_warning(f"Halftime score2 ({score2i}) > final score2 ({score2})")
    
    return result


def _validate_date(date_str: str) -> ValidationResult:
    """Validate date format (YYYY-MM-DD)."""
    result = ValidationResult(is_valid=True)
    
    if not date_str:
        result.add_error("Date is empty")
        return result
    
    # Check format
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        result.add_error(f"Invalid date format: {date_str}. Expected YYYY-MM-DD")
        return result
    
    # Check if it's a valid date
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError as e:
        result.add_error(f"Invalid date: {date_str}. {str(e)}")
    
    return result


def _validate_time(time_str: str) -> ValidationResult:
    """Validate time format (HH:MM)."""
    result = ValidationResult(is_valid=True)
    
    if not time_str:
        return result  # Time is optional
    
    # Check format
    if not re.match(r'^\d{2}:\d{2}$', time_str):
        result.add_warning(f"Time format should be HH:MM: {time_str}")
        return result
    
    # Check if it's a valid time
    try:
        datetime.strptime(time_str, '%H:%M')
    except ValueError:
        result.add_warning(f"Invalid time: {time_str}")
    
    return result


def _validate_goals_consistency(match: Dict[str, Any]) -> ValidationResult:
    """
    Validate that goals count matches the scores.
    
    Note: This is a soft validation (warning only) because:
    - Own goals count for the opposing team
    - Historical data may have incomplete goal information
    """
    result = ValidationResult(is_valid=True)
    
    goals1 = match.get('goals1', [])
    goals2 = match.get('goals2', [])
    score1 = match.get('score1', 0)
    score2 = match.get('score2', 0)
    
    if not goals1 and not goals2:
        # No goal information - this is acceptable
        return result
    
    # Count goals (handling own goals)
    team1_goals = 0
    team2_goals = 0
    
    for goal in goals1:
        if isinstance(goal, dict):
            if goal.get('owngoal', False):
                team2_goals += 1  # Own goal counts for opposing team (recorded in goals1 but from team1)
            else:
                team1_goals += 1
        else:
            team1_goals += 1
    
    for goal in goals2:
        if isinstance(goal, dict):
            if goal.get('owngoal', False):
                team1_goals += 1  # Own goal counts for opposing team
            else:
                team2_goals += 1
        else:
            team2_goals += 1
    
    # Note: goals1 contains goals BY team1, own goals in goals1 are scored by team1 into their own net
    # This means the actual scoring team for goals1 own goals is team1 (scoring against themselves)
    # But the goal counts FOR the opponent's score
    
    # For simplicity, just warn if total goals don't match
    total_goals_from_lists = len(goals1) + len(goals2)
    total_score = score1 + score2
    
    if total_goals_from_lists > 0 and total_goals_from_lists != total_score:
        result.add_warning(
            f"Goals count mismatch: {total_goals_from_lists} goals listed, "
            f"but score is {score1}-{score2} (total: {total_score})"
        )
    
    return result


def _validate_knockout_fields(match: Dict[str, Any]) -> ValidationResult:
    """Validate knockout-stage specific fields."""
    result = ValidationResult(is_valid=True)
    
    score1 = match.get('score1', 0)
    score2 = match.get('score2', 0)
    score1_et = match.get('score1et')
    score2_et = match.get('score2et')
    score1_p = match.get('score1p')
    score2_p = match.get('score2p')
    
    # If match ended in draw after 90 minutes, should have ET or penalties
    # Check for logical consistency
    
    if score1_et is not None and score2_et is not None:
        # If ET scores exist, they should indicate the match went to extra time
        if score1_et == score2_et:
            # Draw after ET - should have penalty scores
            if score1_p is None or score2_p is None:
                result.add_warning(
                    f"Match ended level after ET ({score1_et}-{score2_et}) "
                    "but no penalty scores provided"
                )
    
    if score1_p is not None and score2_p is not None:
        # Penalty shootout - winner should be different
        if score1_p == score2_p:
            result.add_error(
                f"Penalty shootout ended level: {score1_p}-{score2_p}. "
                "This should not happen."
            )
    
    return result


# =============================================================================
# Tournament-Level Validation
# =============================================================================

def validate_worldcup_json(data: Dict[str, Any]) -> ValidationResult:
    """
    Validate a complete worldcup.json structure.
    
    Args:
        data: Dictionary containing the full tournament data
        
    Returns:
        ValidationResult with any errors or warnings
    """
    result = ValidationResult(is_valid=True)
    
    # Check required top-level fields
    if 'name' not in data:
        result.add_error("Missing 'name' field")
    if 'rounds' not in data:
        result.add_error("Missing 'rounds' field")
        return result
    
    rounds = data.get('rounds', [])
    if not isinstance(rounds, list):
        result.add_error("'rounds' should be a list")
        return result
    
    # Track match numbers for uniqueness
    seen_match_nums = set()
    total_matches = 0
    
    for round_idx, round_data in enumerate(rounds):
        if not isinstance(round_data, dict):
            result.add_error(f"Round {round_idx} is not a dictionary")
            continue
        
        round_name = round_data.get('name', f'Round {round_idx}')
        matches = round_data.get('matches', [])
        
        if not matches:
            result.add_warning(f"Round '{round_name}' has no matches")
            continue
        
        is_knockout = _is_knockout_round(round_name)
        
        for match_idx, match in enumerate(matches):
            total_matches += 1
            match_num = match.get('num')
            
            # Check match number uniqueness
            if match_num is not None:
                if match_num in seen_match_nums:
                    result.add_warning(
                        f"Duplicate match number {match_num} in {round_name}"
                    )
                seen_match_nums.add(match_num)
            
            # Validate individual match
            match_result = validate_match(match, is_knockout)
            if not match_result.is_valid or match_result.warnings:
                prefix = f"Match {match_num or match_idx + 1} in '{round_name}': "
                for error in match_result.errors:
                    result.add_error(prefix + error)
                for warning in match_result.warnings:
                    result.add_warning(prefix + warning)
    
    if total_matches == 0:
        result.add_warning("No matches found in tournament")
    
    return result


def validate_groups_json(data: Dict[str, Any]) -> ValidationResult:
    """
    Validate a worldcup.groups.json structure.
    
    Args:
        data: Dictionary containing the groups data
        
    Returns:
        ValidationResult with any errors or warnings
    """
    result = ValidationResult(is_valid=True)
    
    # Check required top-level fields
    if 'name' not in data:
        result.add_error("Missing 'name' field")
    if 'groups' not in data:
        result.add_error("Missing 'groups' field")
        return result
    
    groups = data.get('groups', [])
    if not isinstance(groups, list):
        result.add_error("'groups' should be a list")
        return result
    
    seen_teams = set()
    
    for group_idx, group_data in enumerate(groups):
        if not isinstance(group_data, dict):
            result.add_error(f"Group {group_idx} is not a dictionary")
            continue
        
        group_name = group_data.get('name', f'Group {group_idx}')
        teams = group_data.get('teams', [])
        
        if not teams:
            result.add_warning(f"Group '{group_name}' has no teams")
            continue
        
        for team in teams:
            if isinstance(team, dict):
                team_code = team.get('code', '')
                team_name = team.get('name', '')
                
                if team_code in seen_teams:
                    result.add_warning(
                        f"Team {team_code} ({team_name}) appears in multiple groups"
                    )
                seen_teams.add(team_code)
                
                # Validate team info
                if not team_name:
                    result.add_error(f"Team in {group_name} has no name")
                if not team_code or len(team_code) != 3:
                    result.add_warning(
                        f"Team '{team_name}' has invalid code: '{team_code}'"
                    )
    
    return result


def _is_knockout_round(round_name: str) -> bool:
    """Check if a round name indicates a knockout stage."""
    knockout_keywords = [
        'round of', 'quarter', 'semi', 'final', 'third place',
        'third-place', 'knockout'
    ]
    name_lower = round_name.lower()
    return any(keyword in name_lower for keyword in knockout_keywords)
