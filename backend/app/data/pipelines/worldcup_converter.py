"""
World Cup Converter Pipeline.

This module transforms parsed text data into JSON format matching
the schema used by 2014/2018 World Cup data files.

Location: backend/app/data/pipelines/worldcup_converter.py
"""

import json
from dataclasses import asdict
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from app.data.ingestion.text_parser import (
    ParsedTournament, ParsedMatch, ParsedGoal, ParsedGroup,
    parse_worldcup_year, get_available_years
)
from app.data.cleaning.team_normalizer import (
    get_team_info, generate_stadium_key, TeamInfo
)
from app.data.cleaning.match_validator import (
    validate_worldcup_json, validate_groups_json, ValidationResult
)


# =============================================================================
# JSON Schema Conversion
# =============================================================================

def convert_goal_to_json(
    goal: ParsedGoal, 
    is_team1_goal: bool,
    current_score1: int,
    current_score2: int
) -> Dict[str, Any]:
    """
    Convert a ParsedGoal to JSON format matching the 2014/2018 schema.
    
    The JSON format includes running score at time of goal.
    """
    json_goal = {
        "name": goal.scorer,
        "minute": goal.minute,
    }
    
    # Add stoppage time offset if present
    if goal.offset is not None:
        json_goal["offset"] = goal.offset
    
    # Update running score based on who scored
    if goal.is_own_goal:
        # Own goals are recorded in the scoring team's goals list
        # but count for the opponent
        if is_team1_goal:
            # Own goal by team1 means team2 gets a point
            json_goal["score1"] = current_score1
            json_goal["score2"] = current_score2 + 1
        else:
            json_goal["score1"] = current_score1 + 1
            json_goal["score2"] = current_score2
        json_goal["owngoal"] = True
    else:
        if is_team1_goal:
            json_goal["score1"] = current_score1 + 1
            json_goal["score2"] = current_score2
        else:
            json_goal["score1"] = current_score1
            json_goal["score2"] = current_score2 + 1
    
    # Add penalty flag if present
    if goal.is_penalty:
        json_goal["penalty"] = True
    
    return json_goal


def convert_match_to_json(match: ParsedMatch, match_num: int) -> Dict[str, Any]:
    """
    Convert a ParsedMatch to JSON format matching the 2014/2018 schema.
    """
    # Get team info
    team1_info = get_team_info(match.team1)
    team2_info = get_team_info(match.team2)
    
    # Create team objects with fallbacks
    team1_obj = {
        "name": team1_info.name if team1_info else match.team1,
        "code": team1_info.code if team1_info else "???"
    }
    team2_obj = {
        "name": team2_info.name if team2_info else match.team2,
        "code": team2_info.code if team2_info else "???"
    }
    
    # Build the match object
    json_match: Dict[str, Any] = {
        "num": match.match_num or match_num,
        "date": match.date_str,
        "time": match.time_str or "00:00",
        "team1": team1_obj,
        "team2": team2_obj,
        "score1": match.score1,
        "score2": match.score2,
        "score1i": match.score1_ht,
        "score2i": match.score2_ht,
    }
    
    # Convert goals with running score calculation
    goals1_json = []
    goals2_json = []
    
    # Sort all goals by minute for correct running score
    all_goals: List[Tuple[ParsedGoal, bool]] = []  # (goal, is_team1)
    for g in match.goals1:
        all_goals.append((g, True))
    for g in match.goals2:
        all_goals.append((g, False))
    
    # Sort by minute (and offset for stoppage time)
    all_goals.sort(key=lambda x: (x[0].minute, x[0].offset or 0))
    
    # Calculate running scores
    score1 = 0
    score2 = 0
    
    for goal, is_team1 in all_goals:
        json_goal = convert_goal_to_json(goal, is_team1, score1, score2)
        
        # Update running scores
        if goal.is_own_goal:
            if is_team1:
                score2 += 1
            else:
                score1 += 1
        else:
            if is_team1:
                score1 += 1
            else:
                score2 += 1
        
        if is_team1:
            goals1_json.append(json_goal)
        else:
            goals2_json.append(json_goal)
    
    json_match["goals1"] = goals1_json
    json_match["goals2"] = goals2_json
    
    # Add group if present
    if match.group:
        json_match["group"] = match.group
    
    # Add knockout-specific fields
    if match.is_knockout:
        json_match["knockout"] = True
        
        if match.score1_et is not None:
            json_match["score1et"] = match.score1_et
        else:
            json_match["score1et"] = None
            
        if match.score2_et is not None:
            json_match["score2et"] = match.score2_et
        else:
            json_match["score2et"] = None
            
        if match.score1_pen is not None:
            json_match["score1p"] = match.score1_pen
        else:
            json_match["score1p"] = None
            
        if match.score2_pen is not None:
            json_match["score2p"] = match.score2_pen
        else:
            json_match["score2p"] = None
    
    # Add stadium/venue if present
    if match.stadium:
        json_match["stadium"] = {
            "key": generate_stadium_key(match.stadium),
            "name": match.stadium
        }
    
    if match.city:
        json_match["city"] = match.city
    
    return json_match


def group_matches_by_round(matches: List[ParsedMatch]) -> Dict[str, List[ParsedMatch]]:
    """
    Group matches by their round name for organizing into the rounds structure.
    """
    rounds: Dict[str, List[ParsedMatch]] = {}
    
    for match in matches:
        # Determine round name
        if match.is_knockout and match.round_name:
            round_name = match.round_name
        elif match.group:
            # Group matches - organize by matchday based on sequence
            round_name = f"Group Stage"  # Will be refined later
        else:
            round_name = match.round_name or "Unknown"
        
        if round_name not in rounds:
            rounds[round_name] = []
        rounds[round_name].append(match)
    
    return rounds


def organize_group_stage_rounds(
    matches: List[ParsedMatch]
) -> List[Dict[str, Any]]:
    """
    Organize group stage matches into matchday rounds.
    
    Groups matches by date and creates appropriate matchday names.
    """
    # Group by date
    dates: Dict[str, List[ParsedMatch]] = {}
    for match in matches:
        if match.date_str not in dates:
            dates[match.date_str] = []
        dates[match.date_str].append(match)
    
    # Sort dates and create rounds
    rounds = []
    sorted_dates = sorted(dates.keys())
    
    for i, date in enumerate(sorted_dates):
        day_matches = dates[date]
        
        # Sort matches within day by match number
        day_matches.sort(key=lambda m: m.match_num or 0)
        
        round_data = {
            "name": f"Matchday {i + 1}",
            "matches": [
                convert_match_to_json(m, idx + 1) 
                for idx, m in enumerate(day_matches)
            ]
        }
        rounds.append(round_data)
    
    return rounds


def organize_knockout_rounds(
    matches: List[ParsedMatch]
) -> List[Dict[str, Any]]:
    """
    Organize knockout stage matches into proper rounds.
    """
    # Define round order
    round_order = [
        "Round of 16",
        "Quarter-finals",
        "Semi-finals",
        "Third-place match",
        "Match for third place",
        "Third place match",
        "Final"
    ]
    
    # Group by round name
    rounds_dict: Dict[str, List[ParsedMatch]] = {}
    for match in matches:
        round_name = match.round_name or "Unknown"
        # Normalize round names
        round_name = _normalize_round_name(round_name)
        if round_name not in rounds_dict:
            rounds_dict[round_name] = []
        rounds_dict[round_name].append(match)
    
    # Create ordered rounds
    rounds = []
    seen_rounds = set()
    
    # First add rounds in defined order
    for round_name in round_order:
        normalized = _normalize_round_name(round_name)
        if normalized in rounds_dict and normalized not in seen_rounds:
            matches_in_round = rounds_dict[normalized]
            matches_in_round.sort(key=lambda m: m.match_num or 0)
            
            round_data = {
                "name": round_name,
                "matches": [
                    convert_match_to_json(m, idx + 1)
                    for idx, m in enumerate(matches_in_round)
                ]
            }
            rounds.append(round_data)
            seen_rounds.add(normalized)
    
    # Add any remaining rounds
    for round_name, matches_in_round in rounds_dict.items():
        if round_name not in seen_rounds:
            matches_in_round.sort(key=lambda m: m.match_num or 0)
            round_data = {
                "name": round_name,
                "matches": [
                    convert_match_to_json(m, idx + 1)
                    for idx, m in enumerate(matches_in_round)
                ]
            }
            rounds.append(round_data)
    
    return rounds


def _normalize_round_name(name: str) -> str:
    """Normalize round name for comparison."""
    name_lower = name.lower().strip()
    
    if 'round of 16' in name_lower or 'round of sixteen' in name_lower:
        return "Round of 16"
    if 'quarter' in name_lower:
        return "Quarter-finals"
    if 'semi' in name_lower:
        return "Semi-finals"
    if 'third' in name_lower:
        return "Match for third place"
    if name_lower == 'final':
        return "Final"
    
    return name


def convert_tournament_to_json(tournament: ParsedTournament) -> Dict[str, Any]:
    """
    Convert a complete ParsedTournament to the worldcup.json format.
    """
    rounds = []
    
    # Separate group stage and knockout matches
    group_matches = [m for m in tournament.matches if not m.is_knockout]
    knockout_matches = [m for m in tournament.matches if m.is_knockout]
    
    # Organize group stage
    if group_matches:
        # Group by date and create matchdays
        dates: Dict[str, List[ParsedMatch]] = {}
        for match in group_matches:
            date = match.date_str or "unknown"
            if date not in dates:
                dates[date] = []
            dates[date].append(match)
        
        # Sort dates
        sorted_dates = sorted(dates.keys())
        
        for i, date in enumerate(sorted_dates):
            day_matches = sorted(dates[date], key=lambda m: m.match_num or 0)
            round_data = {
                "name": f"Matchday {i + 1}",
                "matches": [
                    convert_match_to_json(m, m.match_num or idx + 1)
                    for idx, m in enumerate(day_matches)
                ]
            }
            rounds.append(round_data)
    
    # Organize knockout stage
    if knockout_matches:
        knockout_rounds = organize_knockout_rounds(knockout_matches)
        rounds.extend(knockout_rounds)
    
    return {
        "name": tournament.name,
        "rounds": rounds
    }


def convert_groups_to_json(tournament: ParsedTournament) -> Dict[str, Any]:
    """
    Generate the worldcup.groups.json format from parsed tournament data.
    """
    groups_json = []
    
    for group in tournament.groups:
        teams_json = []
        for team_name in group.teams:
            team_info = get_team_info(team_name)
            if team_info:
                teams_json.append({
                    "name": team_info.name,
                    "code": team_info.code
                })
            else:
                teams_json.append({
                    "name": team_name,
                    "code": "???"
                })
        
        groups_json.append({
            "name": group.name,
            "teams": teams_json
        })
    
    return {
        "name": tournament.name,
        "groups": groups_json
    }


# =============================================================================
# Main Conversion Pipeline
# =============================================================================

def convert_worldcup_year(
    datasets_dir: Path,
    year: int,
    output_dir: Optional[Path] = None,
    validate: bool = True
) -> Tuple[Dict[str, Any], Dict[str, Any], ValidationResult]:
    """
    Convert a World Cup year from text to JSON format.
    
    Args:
        datasets_dir: Path to the datasets directory
        year: World Cup year to convert
        output_dir: Optional output directory (defaults to same as source)
        validate: Whether to run validation
        
    Returns:
        Tuple of (worldcup_json, groups_json, validation_result)
    """
    # Parse the text files
    tournament = parse_worldcup_year(datasets_dir, year)
    
    # Convert to JSON
    worldcup_json = convert_tournament_to_json(tournament)
    groups_json = convert_groups_to_json(tournament)
    
    # Validate if requested
    validation_result = ValidationResult(is_valid=True)
    if validate:
        validation_result.merge(validate_worldcup_json(worldcup_json))
        validation_result.merge(validate_groups_json(groups_json))
    
    return worldcup_json, groups_json, validation_result


def save_worldcup_json(
    data: Dict[str, Any],
    output_path: Path,
    pretty: bool = True
) -> None:
    """Save JSON data to file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        if pretty:
            json.dump(data, f, indent=2, ensure_ascii=False)
        else:
            json.dump(data, f, ensure_ascii=False)


def convert_and_save_year(
    datasets_dir: Path,
    year: int,
    dry_run: bool = False
) -> ValidationResult:
    """
    Convert a World Cup year and save the output files.
    
    Args:
        datasets_dir: Path to the datasets directory
        year: World Cup year to convert
        dry_run: If True, don't save files, just validate
        
    Returns:
        ValidationResult with any errors or warnings
    """
    year_dir = datasets_dir / str(year)
    
    # Convert
    worldcup_json, groups_json, validation = convert_worldcup_year(
        datasets_dir, year
    )
    
    if not dry_run:
        # Save worldcup.json
        worldcup_path = year_dir / "worldcup.json"
        save_worldcup_json(worldcup_json, worldcup_path)
        
        # Save worldcup.groups.json
        groups_path = year_dir / "worldcup.groups.json"
        save_worldcup_json(groups_json, groups_path)
    
    return validation


def convert_all_years(
    datasets_dir: Path,
    years: Optional[List[int]] = None,
    exclude_existing: bool = True,
    dry_run: bool = False
) -> Dict[int, ValidationResult]:
    """
    Convert multiple World Cup years.
    
    Args:
        datasets_dir: Path to the datasets directory
        years: Specific years to convert (if None, convert all available)
        exclude_existing: Skip years that already have JSON files (2014, 2018)
        dry_run: If True, don't save files, just validate
        
    Returns:
        Dictionary mapping year to ValidationResult
    """
    results: Dict[int, ValidationResult] = {}
    
    # Get years to process
    if years is None:
        years = get_available_years(datasets_dir)
    
    # Exclude existing if requested
    if exclude_existing:
        existing_years = {2014, 2018}  # These already have JSON
        years = [y for y in years if y not in existing_years]
    
    for year in years:
        try:
            result = convert_and_save_year(datasets_dir, year, dry_run)
            results[year] = result
        except Exception as e:
            result = ValidationResult(is_valid=False)
            result.add_error(f"Conversion failed: {str(e)}")
            results[year] = result
    
    return results
