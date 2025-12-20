"""
Text Parser Module for World Cup historical data files.

This module reads and parses cup.txt and cup_finals.txt files from historical
World Cup datasets (1930-2010, 2022) and extracts structured match data.

Location: backend/app/data/ingestion/text_parser.py
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime


# =============================================================================
# Data Classes for Parsed Results
# =============================================================================

@dataclass
class ParsedGoal:
    """Represents a goal extracted from text."""
    scorer: str
    minute: int
    offset: Optional[int] = None  # For stoppage time (90+X)
    is_penalty: bool = False
    is_own_goal: bool = False


@dataclass
class ParsedMatch:
    """Represents a match extracted from text."""
    match_num: Optional[int] = None
    date_str: str = ""
    time_str: Optional[str] = None
    team1: str = ""
    team2: str = ""
    score1: int = 0
    score2: int = 0
    score1_ht: Optional[int] = None  # Half-time score
    score2_ht: Optional[int] = None
    score1_et: Optional[int] = None  # Extra time total
    score2_et: Optional[int] = None
    score1_pen: Optional[int] = None  # Penalty shootout
    score2_pen: Optional[int] = None
    is_aet: bool = False  # After extra time
    goals1: List[ParsedGoal] = field(default_factory=list)
    goals2: List[ParsedGoal] = field(default_factory=list)
    stadium: Optional[str] = None
    city: Optional[str] = None
    group: Optional[str] = None
    round_name: Optional[str] = None
    is_knockout: bool = False


@dataclass
class ParsedGroup:
    """Represents a group extracted from text."""
    name: str
    teams: List[str] = field(default_factory=list)


@dataclass
class ParsedTournament:
    """Represents a complete tournament extracted from text."""
    name: str
    year: int
    location: Optional[str] = None
    groups: List[ParsedGroup] = field(default_factory=list)
    matches: List[ParsedMatch] = field(default_factory=list)


# =============================================================================
# Regular Expression Patterns
# =============================================================================

# Tournament header: "= World Cup 1994" or "= World Cup 1994       # in United States"
RE_TOURNAMENT_HEADER = re.compile(
    r'^=\s*World\s+Cup\s+(\d{4})\s*(?:#\s*(?:in\s+)?(.+))?$',
    re.IGNORECASE
)

# Group definition: "Group A  |  Brazil   Germany   Spain   Italy"
RE_GROUP_DEF = re.compile(
    r'^Group\s+([A-H1-4F])\s*\|\s*(.+)$',
    re.IGNORECASE
)

# Match line patterns - multiple formats across different World Cups
# Format 1 (1994): "(3)  18 June    United States    1-1     Switzerland   @ Pontiac Silverdome, Pontiac"
# Format 2 (2022): "(1) Sun Nov/20 19:00      Qatar   0-2 (0-2)   Ecuador    @ Al Bayt Stadium, Al Khor"
# Format 3 (1930): "(1)  13 July     France     4-1 (3-0)  Mexico    @ Estadio Pocitos, Montevideo"

RE_MATCH_LINE = re.compile(
    r'^\s*\((\d+)\)\s+'  # Match number
    r'(?:(\w+)\s+)?'  # Optional day of week
    r'(\d{1,2})\s*(?:/|\.|\s+)?'  # Day
    r'(\w+)(?:/(\d{1,2}))?\s*'  # Month (and optional day after /)
    r'(?:(\d{1,2}:\d{2})\s+)?'  # Optional time
    r'(.+?)\s+'  # Team 1
    r'(\d+)\s*-\s*(\d+)'  # Score
    r'(?:\s*((?:pen\.|a\.e\.t\.|[\d\-\(\)\s]+)+))?\s*'  # Optional penalty/aet/ht score
    r'(.+?)'  # Team 2
    r'(?:\s*@\s*(.+))?$'  # Optional venue
)

# Simpler match line pattern for edge cases
RE_MATCH_SIMPLE = re.compile(
    r'^\s*\((\d+)\)\s+'  # Match number
    r'(\d{1,2})\s+(\w+)\s+'  # Day Month
    r'(.+?)\s+'  # Team 1
    r'(\d+)\s*-\s*(\d+)'  # Score
    r'(.*)$'  # Rest of line
)

# Score with halftime: "4-1 (3-0)" or "1-1 a.e.t. (1-0)" or "3-2 pen. 0-0 a.e.t. (0-0)"
RE_SCORE_DETAILS = re.compile(
    r'(\d+)\s*-\s*(\d+)\s*'  # Main score
    r'(?:(pen\.?)\s+)?'  # Optional penalty indicator
    r'(?:(\d+)\s*-\s*(\d+)\s*)?'  # Optional regulation/ET score
    r'(?:(a\.e\.t\.?)\s*)?'  # Optional AET indicator
    r'(?:\((\d+)\s*-\s*(\d+)\))?'  # Optional halftime score
)

# Goals line pattern: "[Scorer1 MM' Scorer2 NN'; Scorer3 PP']" or "[Team1Goals; Team2Goals]"
RE_GOALS_LINE = re.compile(r'^\s*\[(.+)\]\s*$')

# Individual goal pattern: "Neymar 29'" or "Messi 90+3'" or "Ronaldo 65'(pen.)" or "Parra 15' (o.g.)"
RE_GOAL = re.compile(
    r"([A-Za-zÀ-ÿ\s\.\-']+?)\s+"  # Scorer name
    r"(\d+)"  # Minute
    r"(?:\+(\d+))?"  # Optional stoppage time
    r"['\u2019]"  # Minute marker (apostrophe)
    r"(?:\s*\((pen\.?|o\.g\.?)\))?"  # Optional penalty or own goal
)

# Round headers
RE_ROUND_HEADER = re.compile(
    r'^(Round\s+of\s+\d+|Quarter-finals?|Semi-finals?|'
    r'Third[- ]place\s+match|Match\s+for\s+third\s+place|Final|'
    r'Final\s+Round|First\s+round|Matchday\s+\d+)\s*'
    r'(?:\|.*)?$',
    re.IGNORECASE
)

# Group header in match section: "Group A" or "Group 1"
RE_GROUP_HEADER = re.compile(r'^Group\s+([A-H1-4F])\s*$', re.IGNORECASE)


# =============================================================================
# Parser Functions
# =============================================================================

def parse_tournament_header(line: str) -> Optional[Tuple[int, Optional[str]]]:
    """Parse tournament header line to extract year and location."""
    match = RE_TOURNAMENT_HEADER.match(line.strip())
    if match:
        year = int(match.group(1))
        location = match.group(2).strip() if match.group(2) else None
        return year, location
    return None


def parse_group_definition(line: str) -> Optional[ParsedGroup]:
    """Parse group definition line to extract group name and teams."""
    match = RE_GROUP_DEF.match(line.strip())
    if match:
        group_name = f"Group {match.group(1).upper()}"
        teams_str = match.group(2)
        # Split teams by multiple spaces
        teams = [t.strip() for t in re.split(r'\s{2,}', teams_str) if t.strip()]
        return ParsedGroup(name=group_name, teams=teams)
    return None


def parse_goals(goals_text: str) -> Tuple[List[ParsedGoal], List[ParsedGoal]]:
    """
    Parse goals text that may be in format:
    - "[Team1Goals; Team2Goals]"
    - "[Team1Goals]" (when team2 has no goals, shown as "-")
    """
    goals1: List[ParsedGoal] = []
    goals2: List[ParsedGoal] = []
    
    if not goals_text:
        return goals1, goals2
    
    # Remove brackets if present
    text = goals_text.strip()
    if text.startswith('['):
        text = text[1:]
    if text.endswith(']'):
        text = text[:-1]
    
    # Split by semicolon for team1 vs team2 goals
    parts = text.split(';')
    
    team1_text = parts[0].strip() if len(parts) > 0 else ""
    team2_text = parts[1].strip() if len(parts) > 1 else ""
    
    # Parse each team's goals
    goals1 = _parse_team_goals(team1_text)
    goals2 = _parse_team_goals(team2_text)
    
    return goals1, goals2


def _parse_team_goals(text: str) -> List[ParsedGoal]:
    """Parse goals for a single team."""
    goals: List[ParsedGoal] = []
    
    if not text or text == '-':
        return goals
    
    # Find all goal matches
    for match in RE_GOAL.finditer(text):
        scorer = match.group(1).strip()
        minute = int(match.group(2))
        offset = int(match.group(3)) if match.group(3) else None
        modifier = match.group(4).lower() if match.group(4) else ""
        
        is_penalty = 'pen' in modifier
        is_own_goal = 'o.g' in modifier
        
        goals.append(ParsedGoal(
            scorer=scorer,
            minute=minute,
            offset=offset,
            is_penalty=is_penalty,
            is_own_goal=is_own_goal
        ))
    
    return goals


def parse_score_details(score_text: str) -> Dict[str, Any]:
    """
    Parse complex score strings like:
    - "3-2 pen. 0-0 a.e.t. (0-0)"
    - "1-1 a.e.t. (1-0)"
    - "4-1 (3-0)"
    - "2-1"
    """
    result = {
        'score1': 0,
        'score2': 0,
        'score1_ht': None,
        'score2_ht': None,
        'score1_et': None,
        'score2_et': None,
        'score1_pen': None,
        'score2_pen': None,
        'is_aet': False,
    }
    
    text = score_text.strip()
    
    # Check for penalty shootout: "3-2 pen." at the start
    pen_match = re.match(r'^(\d+)\s*-\s*(\d+)\s*pen\.?', text)
    if pen_match:
        result['score1_pen'] = int(pen_match.group(1))
        result['score2_pen'] = int(pen_match.group(2))
        text = text[pen_match.end():].strip()
    
    # Check for a.e.t.
    if 'a.e.t' in text.lower():
        result['is_aet'] = True
    
    # Find all score patterns (X-Y)
    scores = re.findall(r'(\d+)\s*-\s*(\d+)', text)
    
    if scores:
        # First score is either final or regulation time score
        if result['score1_pen'] is not None:
            # If we have penalties, first remaining score is ET regulation
            result['score1_et'] = int(scores[0][0])
            result['score2_et'] = int(scores[0][1])
            # Final score is penalties
            result['score1'] = result['score1_pen']
            result['score2'] = result['score2_pen']
        elif result['is_aet']:
            # AET without penalties: first score is final after ET
            result['score1'] = int(scores[0][0])
            result['score2'] = int(scores[0][1])
            result['score1_et'] = result['score1']
            result['score2_et'] = result['score2']
        else:
            # Regular match
            result['score1'] = int(scores[0][0])
            result['score2'] = int(scores[0][1])
        
        # Last score in parentheses is halftime
        # Look for (X-Y) pattern
        ht_match = re.search(r'\((\d+)\s*-\s*(\d+)\)\s*$', text)
        if ht_match:
            result['score1_ht'] = int(ht_match.group(1))
            result['score2_ht'] = int(ht_match.group(2))
    
    return result


def parse_match_line(line: str, current_group: Optional[str] = None, 
                     current_round: Optional[str] = None,
                     year: int = 2022) -> Optional[ParsedMatch]:
    """
    Parse a single match line and return ParsedMatch object.
    
    Handles multiple formats across World Cup years.
    """
    line = line.strip()
    if not line or not line.startswith('('):
        return None
    
    # Try to extract match number first
    num_match = re.match(r'\((\d+)\)\s+', line)
    if not num_match:
        return None
    
    match_num = int(num_match.group(1))
    rest = line[num_match.end():]
    
    # Parse the date portion
    date_str, time_str, rest = _parse_date_portion(rest, year)
    
    # Parse teams and score
    team1, score_text, team2, venue = _parse_teams_and_score(rest)
    
    if not team1 or not team2:
        return None
    
    # Parse score details
    score_info = parse_score_details(score_text)
    
    # Parse venue
    stadium, city = _parse_venue(venue) if venue else (None, None)
    
    # Determine if knockout
    is_knockout = current_round is not None and current_round.lower() not in [
        'matchday', 'group', 'first round'
    ] and 'group' not in (current_round or '').lower()
    
    return ParsedMatch(
        match_num=match_num,
        date_str=date_str,
        time_str=time_str,
        team1=team1.strip(),
        team2=team2.strip(),
        score1=score_info['score1'],
        score2=score_info['score2'],
        score1_ht=score_info['score1_ht'],
        score2_ht=score_info['score2_ht'],
        score1_et=score_info['score1_et'],
        score2_et=score_info['score2_et'],
        score1_pen=score_info['score1_pen'],
        score2_pen=score_info['score2_pen'],
        is_aet=score_info['is_aet'],
        stadium=stadium,
        city=city,
        group=current_group if not is_knockout else None,
        round_name=current_round,
        is_knockout=is_knockout
    )


def _parse_date_portion(text: str, year: int) -> Tuple[str, Optional[str], str]:
    """Extract date and time from the beginning of a match line."""
    # Pattern: "Sun Nov/20 19:00" or "18 June" or "Fri Jun/9"
    
    # Try format with day name and time: "Sun Nov/20 19:00"
    match = re.match(
        r'^(\w{3})\s+(\w+)/(\d{1,2})\s+(\d{1,2}:\d{2})\s+',
        text
    )
    if match:
        day_name, month, day, time = match.groups()
        month_num = _month_to_num(month)
        date_str = f"{year}-{month_num:02d}-{int(day):02d}"
        return date_str, time, text[match.end():]
    
    # Try format with day name, no time: "Fri Jun/9"
    match = re.match(
        r'^(\w{3})\s+(\w+)/(\d{1,2})\s+',
        text
    )
    if match:
        day_name, month, day = match.groups()
        month_num = _month_to_num(month)
        date_str = f"{year}-{month_num:02d}-{int(day):02d}"
        return date_str, None, text[match.end():]
    
    # Try format: "18 June" or "18 July"
    match = re.match(r'^(\d{1,2})\s+(\w+)\s+', text)
    if match:
        day, month = match.groups()
        month_num = _month_to_num(month)
        date_str = f"{year}-{month_num:02d}-{int(day):02d}"
        return date_str, None, text[match.end():]
    
    return "", None, text


def _month_to_num(month: str) -> int:
    """Convert month name to number."""
    months = {
        'jan': 1, 'january': 1,
        'feb': 2, 'february': 2,
        'mar': 3, 'march': 3,
        'apr': 4, 'april': 4,
        'may': 5,
        'jun': 6, 'june': 6,
        'jul': 7, 'july': 7,
        'aug': 8, 'august': 8,
        'sep': 9, 'september': 9,
        'oct': 10, 'october': 10,
        'nov': 11, 'november': 11,
        'dec': 12, 'december': 12,
    }
    return months.get(month.lower()[:3], 1)


def _parse_teams_and_score(text: str) -> Tuple[str, str, str, Optional[str]]:
    """Parse team names, score, and venue from match text."""
    # Look for venue marker
    venue = None
    if '@' in text:
        parts = text.split('@', 1)
        text = parts[0].strip()
        venue = parts[1].strip()
    
    # Find the score pattern - must have digits with dash: X-Y
    # Also handle complex scores like "3-2 pen. 0-0 a.e.t. (0-0)"
    score_pattern = re.compile(
        r'(\d+)\s*-\s*(\d+)'
        r'(?:\s*pen\.?)?'
        r'(?:\s*\d+\s*-\s*\d+)?'
        r'(?:\s*a\.e\.t\.?)?'
        r'(?:\s*\(\d+\s*-\s*\d+(?:,\s*\d+\s*-\s*\d+)?\))?'
    )
    
    score_match = score_pattern.search(text)
    if not score_match:
        return "", "", "", venue
    
    team1 = text[:score_match.start()].strip()
    score_text = score_match.group(0)
    team2 = text[score_match.end():].strip()
    
    return team1, score_text, team2, venue


def _parse_venue(venue: str) -> Tuple[Optional[str], Optional[str]]:
    """Parse venue string into stadium and city."""
    if not venue:
        return None, None
    
    # Format: "Stadium Name, City"
    if ',' in venue:
        parts = venue.rsplit(',', 1)
        stadium = parts[0].strip()
        city = parts[1].strip()
        return stadium, city
    
    return venue.strip(), None


def parse_cup_file(file_path: Path) -> ParsedTournament:
    """
    Parse a cup.txt file and return a ParsedTournament object.
    
    This handles the group stage matches.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    tournament = ParsedTournament(name="", year=0)
    current_group: Optional[str] = None
    current_round: Optional[str] = None
    pending_goals_line: Optional[str] = None
    last_match: Optional[ParsedMatch] = None
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        
        # Skip empty lines and comments
        if not line_stripped or line_stripped.startswith('##'):
            continue
        
        # Parse tournament header
        header_result = parse_tournament_header(line_stripped)
        if header_result:
            tournament.year, tournament.location = header_result
            tournament.name = f"World Cup {tournament.year}"
            continue
        
        # Parse group definitions
        group_def = parse_group_definition(line_stripped)
        if group_def:
            tournament.groups.append(group_def)
            continue
        
        # Check for group header in matches section
        group_match = RE_GROUP_HEADER.match(line_stripped)
        if group_match:
            current_group = f"Group {group_match.group(1).upper()}"
            current_round = None
            continue
        
        # Check for round header
        round_match = RE_ROUND_HEADER.match(line_stripped)
        if round_match:
            current_round = round_match.group(1)
            if 'group' not in current_round.lower() and 'matchday' not in current_round.lower():
                current_group = None  # Clear group for knockout
            continue
        
        # Check for goals line (starts with '[')
        if line_stripped.startswith('['):
            goals_match = RE_GOALS_LINE.match(line_stripped)
            if goals_match and last_match:
                goals1, goals2 = parse_goals(goals_match.group(1))
                last_match.goals1 = goals1
                last_match.goals2 = goals2
            continue
        
        # Try to parse as a match line
        if line_stripped.startswith('('):
            match = parse_match_line(
                line_stripped, 
                current_group, 
                current_round,
                tournament.year
            )
            if match:
                tournament.matches.append(match)
                last_match = match
    
    return tournament


def parse_cup_finals_file(file_path: Path) -> ParsedTournament:
    """
    Parse a cup_finals.txt file and return a ParsedTournament object.
    
    This handles the knockout stage matches (Round of 16, Quarter-finals, etc.)
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    tournament = ParsedTournament(name="", year=0)
    current_round: Optional[str] = None
    last_match: Optional[ParsedMatch] = None
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        
        # Skip empty lines and comments
        if not line_stripped or line_stripped.startswith('#'):
            continue
        
        # Parse tournament header
        header_result = parse_tournament_header(line_stripped)
        if header_result:
            tournament.year, tournament.location = header_result
            tournament.name = f"World Cup {tournament.year}"
            continue
        
        # Check for round header
        round_match = RE_ROUND_HEADER.match(line_stripped)
        if round_match:
            current_round = round_match.group(1)
            continue
        
        # Check for goals line (starts with '[')
        if line_stripped.startswith('['):
            goals_match = RE_GOALS_LINE.match(line_stripped)
            if goals_match and last_match:
                goals1, goals2 = parse_goals(goals_match.group(1))
                last_match.goals1 = goals1
                last_match.goals2 = goals2
            continue
        
        # Try to parse as a match line
        if line_stripped.startswith('('):
            match = parse_match_line(
                line_stripped, 
                None,  # No group for knockout
                current_round,
                tournament.year
            )
            if match:
                match.is_knockout = True
                tournament.matches.append(match)
                last_match = match
    
    return tournament


def parse_worldcup_year(datasets_dir: Path, year: int) -> ParsedTournament:
    """
    Parse all text files for a given World Cup year.
    
    Combines cup.txt and cup_finals.txt if both exist.
    """
    year_dir = datasets_dir / str(year)
    cup_file = year_dir / "cup.txt"
    finals_file = year_dir / "cup_finals.txt"
    
    # Start with group stage
    if cup_file.exists():
        tournament = parse_cup_file(cup_file)
    else:
        raise FileNotFoundError(f"No cup.txt found for {year}")
    
    # Add knockout stage if exists
    if finals_file.exists():
        finals_tournament = parse_cup_finals_file(finals_file)
        # Merge knockout matches
        tournament.matches.extend(finals_tournament.matches)
    
    return tournament


# =============================================================================
# Utility Functions
# =============================================================================

def get_available_years(datasets_dir: Path) -> List[int]:
    """Get list of years that have cup.txt files."""
    years = []
    for subdir in datasets_dir.iterdir():
        if subdir.is_dir() and subdir.name.isdigit():
            year = int(subdir.name)
            cup_file = subdir / "cup.txt"
            if cup_file.exists():
                years.append(year)
    return sorted(years)
