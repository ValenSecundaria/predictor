"""
Team Normalizer Module for World Cup data.

This module handles team name normalization, standardization, and code generation.
It maps various historical and alternate team names to canonical names and FIFA codes.

Location: backend/app/data/cleaning/team_normalizer.py
"""

from dataclasses import dataclass
from typing import Dict, Optional, List, Tuple
import re


@dataclass
class TeamInfo:
    """Represents normalized team information."""
    name: str          # Canonical name
    code: str          # FIFA 3-letter code
    historical_name: Optional[str] = None  # Original name if different


# =============================================================================
# Team Mappings Database
# =============================================================================

# Master mapping of team names to their codes and canonical names
# Key: lowercase normalized name, Value: (canonical_name, code)
#
# IMPORTANT MATCHING RULES:
# - Teams representing the SAME NATION (continuity) use the SAME CODE
# - Teams representing DIFFERENT STATES use DIFFERENT CODES
#
TEAM_DATABASE: Dict[str, Tuple[str, str]] = {
    # =========================================================================
    # AFRICA (CAF)
    # =========================================================================
    "algeria": ("Algeria", "ALG"),
    "angola": ("Angola", "ANG"),
    "cameroon": ("Cameroon", "CMR"),
    
    # DR Congo continuity: Zaire (1971-1997) → DR Congo
    # SAME NATION - SAME CODE
    "dr congo": ("DR Congo", "COD"),
    "democratic republic of congo": ("DR Congo", "COD"),
    "zaire": ("DR Congo", "COD"),  # Historical name, same nation → same code
    
    "egypt": ("Egypt", "EGY"),
    "ghana": ("Ghana", "GHA"),
    
    # Côte d'Ivoire: Multiple names for same country
    # SAME NATION - SAME CODE
    "ivory coast": ("Côte d'Ivoire", "CIV"),
    "côte d'ivoire": ("Côte d'Ivoire", "CIV"),
    "cote d'ivoire": ("Côte d'Ivoire", "CIV"),
    
    "morocco": ("Morocco", "MAR"),
    "nigeria": ("Nigeria", "NGA"),
    "senegal": ("Senegal", "SEN"),
    "south africa": ("South Africa", "RSA"),
    "togo": ("Togo", "TOG"),
    "tunisia": ("Tunisia", "TUN"),
    
    # =========================================================================
    # ASIA (AFC)
    # =========================================================================
    "australia": ("Australia", "AUS"),
    "china": ("China PR", "CHN"),
    "china pr": ("China PR", "CHN"),
    "india": ("India", "IND"),
    "indonesia": ("Indonesia", "IDN"),
    "dutch east indies": ("Indonesia", "IDN"),  # Historical → Indonesia (same nation)
    
    # Iran continuity: Different official names
    # SAME NATION - SAME CODE
    "iran": ("Iran", "IRN"),
    "ir iran": ("Iran", "IRN"),
    
    "iraq": ("Iraq", "IRQ"),
    "israel": ("Israel", "ISR"),
    "japan": ("Japan", "JPN"),
    "north korea": ("Korea DPR", "PRK"),
    "korea dpr": ("Korea DPR", "PRK"),
    "south korea": ("Korea Republic", "KOR"),
    "korea republic": ("Korea Republic", "KOR"),
    "korea": ("Korea Republic", "KOR"),
    "kuwait": ("Kuwait", "KUW"),
    "qatar": ("Qatar", "QAT"),
    "saudi arabia": ("Saudi Arabia", "KSA"),
    "united arab emirates": ("UAE", "UAE"),
    "uae": ("UAE", "UAE"),
    
    # =========================================================================
    # EUROPE (UEFA)
    # =========================================================================
    "albania": ("Albania", "ALB"),
    "austria": ("Austria", "AUT"),
    "belgium": ("Belgium", "BEL"),
    "bosnia-herzegovina": ("Bosnia-Herzegovina", "BIH"),
    "bosnia and herzegovina": ("Bosnia-Herzegovina", "BIH"),
    "bulgaria": ("Bulgaria", "BUL"),
    "croatia": ("Croatia", "CRO"),
    
    # Czech Republic: NEW state after Czechoslovakia split
    # DIFFERENT STATE - DIFFERENT CODE
    "czech republic": ("Czech Republic", "CZE"),
    "czechoslovakia": ("Czechoslovakia", "TCH"),  # Historical, separate from CZE/SVK
    
    "denmark": ("Denmark", "DEN"),
    "england": ("England", "ENG"),
    "france": ("France", "FRA"),
    
    # Germany continuity: West Germany (1949-1990) → Germany (1990+)
    # Federal Republic of Germany continued as unified Germany
    # SAME NATION - SAME CODE
    "germany": ("Germany", "GER"),
    "west germany": ("Germany", "GER"),  # Same nation, reunified
    
    # East Germany: SEPARATE state (GDR 1949-1990)
    # DIFFERENT STATE - DIFFERENT CODE
    "east germany": ("East Germany", "GDR"),  # Different state, NOT unified with GER
    
    "greece": ("Greece", "GRE"),
    "hungary": ("Hungary", "HUN"),
    "iceland": ("Iceland", "ISL"),
    "ireland": ("Republic of Ireland", "IRL"),
    "republic of ireland": ("Republic of Ireland", "IRL"),
    "italy": ("Italy", "ITA"),
    
    # Netherlands: Holland is informal name
    # SAME NATION - SAME CODE
    "netherlands": ("Netherlands", "NED"),
    "holland": ("Netherlands", "NED"),  # Informal name, same nation
    
    "northern ireland": ("Northern Ireland", "NIR"),
    "norway": ("Norway", "NOR"),
    "poland": ("Poland", "POL"),
    "portugal": ("Portugal", "POR"),
    "romania": ("Romania", "ROU"),
    
    # Russia: Post-Soviet independent state
    # DIFFERENT STATE - DIFFERENT CODE
    "russia": ("Russia", "RUS"),
    
    "scotland": ("Scotland", "SCO"),
    
    # Serbia: Post-Yugoslavia independent state
    # DIFFERENT STATE - DIFFERENT CODE
    "serbia": ("Serbia", "SRB"),
    
    # Serbia and Montenegro: Temporary union (1992-2006)
    # DIFFERENT STATE - DIFFERENT CODE (from both Serbia and Yugoslavia)
    "serbia and montenegro": ("Serbia and Montenegro", "SCG"),
    
    # Slovakia: NEW state after Czechoslovakia split
    # DIFFERENT STATE - DIFFERENT CODE
    "slovakia": ("Slovakia", "SVK"),
    
    "slovenia": ("Slovenia", "SVN"),
    
    # Soviet Union: Multi-national state
    # DIFFERENT STATE - DIFFERENT CODE (from Russia)
    "soviet union": ("Soviet Union", "URS"),
    "ussr": ("Soviet Union", "URS"),
    
    "spain": ("Spain", "ESP"),
    "sweden": ("Sweden", "SWE"),
    "switzerland": ("Switzerland", "SUI"),
    "turkey": ("Turkey", "TUR"),
    "ukraine": ("Ukraine", "UKR"),
    "wales": ("Wales", "WAL"),
    
    # Yugoslavia: Multi-national state
    # DIFFERENT STATE - DIFFERENT CODE (from Serbia, Croatia, etc.)
    "yugoslavia": ("Yugoslavia", "YUG"),
    
    # =========================================================================
    # NORTH/CENTRAL AMERICA & CARIBBEAN (CONCACAF)
    # =========================================================================
    "canada": ("Canada", "CAN"),
    "costa rica": ("Costa Rica", "CRC"),
    "cuba": ("Cuba", "CUB"),
    "el salvador": ("El Salvador", "SLV"),
    "haiti": ("Haiti", "HAI"),
    "honduras": ("Honduras", "HON"),
    "jamaica": ("Jamaica", "JAM"),
    "mexico": ("Mexico", "MEX"),
    "panama": ("Panama", "PAN"),
    "trinidad and tobago": ("Trinidad and Tobago", "TRI"),
    "united states": ("United States", "USA"),
    "usa": ("United States", "USA"),
    "us": ("United States", "USA"),
    
    # =========================================================================
    # SOUTH AMERICA (CONMEBOL)
    # =========================================================================
    "argentina": ("Argentina", "ARG"),
    "bolivia": ("Bolivia", "BOL"),
    "brazil": ("Brazil", "BRA"),
    "chile": ("Chile", "CHI"),
    "colombia": ("Colombia", "COL"),
    "ecuador": ("Ecuador", "ECU"),
    "paraguay": ("Paraguay", "PAR"),
    "peru": ("Peru", "PER"),
    "uruguay": ("Uruguay", "URU"),
    "venezuela": ("Venezuela", "VEN"),
    
    # =========================================================================
    # OCEANIA (OFC)
    # =========================================================================
    "new zealand": ("New Zealand", "NZL"),
}

# Historical teams and their relationships
# This explains the nature of each historical entity
HISTORICAL_TEAMS = {
    # ========================================
    # CONTINUITY CASES (Unified codes)
    # ========================================
    "West Germany → Germany": {
        "explanation": "Federal Republic of Germany (1949-1990) continued as unified Germany (1990+)",
        "code": "GER",
        "status": "SAME_NATION"
    },
    "Zaire → DR Congo": {
        "explanation": "Renamed in 1997, same country",
        "code": "COD",
        "status": "SAME_NATION"
    },
    "Holland → Netherlands": {
        "explanation": "Informal name vs official name, same country",
        "code": "NED",
        "status": "SAME_NATION"
    },
    "Iran / IR Iran": {
        "explanation": "Different official names for same country",
        "code": "IRN",
        "status": "SAME_NATION"
    },
    "Ivory Coast → Côte d'Ivoire": {
        "explanation": "English name vs French official name, same country",
        "code": "CIV",
        "status": "SAME_NATION"
    },
    "Dutch East Indies → Indonesia": {
        "explanation": "Colonial name vs independent nation, same territory",
        "code": "IDN",
        "status": "SAME_NATION"
    },
    
    # ========================================
    # SEPARATION CASES (Different codes)
    # ========================================
    "East Germany (GDR)": {
        "explanation": "Separate state (1949-1990), NOT unified with West Germany/Germany",
        "code": "GDR",
        "status": "DIFFERENT_STATE"
    },
    "Soviet Union (USSR)": {
        "explanation": "Multi-national state (1922-1991), NOT the same as Russia",
        "code": "URS",
        "status": "DIFFERENT_STATE"
    },
    "Yugoslavia": {
        "explanation": "Multi-national state (1918-1992), NOT the same as Serbia/Croatia/etc",
        "code": "YUG",
        "status": "DIFFERENT_STATE"
    },
    "Serbia and Montenegro": {
        "explanation": "Temporary union (1992-2006), separate from both Yugoslavia and Serbia",
        "code": "SCG",
        "status": "DIFFERENT_STATE"
    },
    "Czechoslovakia": {
        "explanation": "Split into Czech Republic and Slovakia in 1993, separate entities",
        "code": "TCH",
        "status": "DIFFERENT_STATE"
    },
}


# =============================================================================
# Normalization Functions
# =============================================================================

def normalize_team_name(name: str) -> str:
    """
    Normalize a team name by removing extra whitespace and handling
    common variations.
    """
    if not name:
        return ""
    
    # Strip and normalize whitespace
    normalized = ' '.join(name.split())
    
    # Handle some common abbreviations and variations
    replacements = [
        (r"\bU\.?S\.?A\.?\b", "USA"),
        (r"\bU\.?S\.?\b", "USA"),
        (r"\bRep\.?\b", "Republic"),
        (r"\bDem\.?\b", "Democratic"),
        (r"\bPR\b", "PR"),  # People's Republic
    ]
    
    for pattern, replacement in replacements:
        normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)
    
    return normalized.strip()


def get_team_info(name: str) -> Optional[TeamInfo]:
    """
    Get normalized team information for a given team name.
    
    Returns TeamInfo with canonical name and code, or None if not found.
    """
    if not name:
        return None
    
    # Normalize the input
    normalized = normalize_team_name(name)
    lookup_key = normalized.lower()
    
    # Direct lookup
    if lookup_key in TEAM_DATABASE:
        canonical, code = TEAM_DATABASE[lookup_key]
        original = name if canonical != name else None
        return TeamInfo(name=canonical, code=code, historical_name=original)
    
    # Try without diacritics for fuzzy matching
    ascii_key = _remove_diacritics(lookup_key)
    for db_key, (canonical, code) in TEAM_DATABASE.items():
        if _remove_diacritics(db_key) == ascii_key:
            return TeamInfo(name=canonical, code=code, historical_name=name)
    
    # Partial matching for edge cases
    for db_key, (canonical, code) in TEAM_DATABASE.items():
        if lookup_key in db_key or db_key in lookup_key:
            return TeamInfo(name=canonical, code=code, historical_name=name)
    
    return None


def get_team_code(name: str) -> Optional[str]:
    """Get the FIFA code for a team name."""
    info = get_team_info(name)
    return info.code if info else None


def get_canonical_name(name: str) -> Optional[str]:
    """Get the canonical name for a team."""
    info = get_team_info(name)
    return info.name if info else None


def is_historical_team(name: str) -> bool:
    """Check if a team is a historical (no longer existing) team."""
    info = get_team_info(name)
    if info:
        return info.name in HISTORICAL_TEAMS
    return False


def _remove_diacritics(text: str) -> str:
    """Remove diacritics/accents from text for fuzzy matching."""
    import unicodedata
    # Normalize to decomposed form, then remove combining characters
    nfkd_form = unicodedata.normalize('NFKD', text)
    return ''.join(c for c in nfkd_form if not unicodedata.combining(c))


# =============================================================================
# Batch Processing
# =============================================================================

def normalize_team_list(teams: List[str]) -> List[TeamInfo]:
    """
    Normalize a list of team names.
    
    Returns list of TeamInfo objects, with None entries for unrecognized teams.
    """
    results = []
    for team in teams:
        info = get_team_info(team)
        if info:
            results.append(info)
        else:
            # Create a placeholder with original name
            results.append(TeamInfo(name=team, code="???", historical_name=None))
    return results


def find_unknown_teams(teams: List[str]) -> List[str]:
    """Find teams that are not in the database."""
    unknown = []
    for team in teams:
        if get_team_info(team) is None:
            unknown.append(team)
    return unknown


def generate_team_code(name: str) -> str:
    """
    Generate a 3-letter code for an unknown team.
    
    This is a fallback for teams not in the database.
    """
    # Remove common words and take first 3 consonants
    cleaned = re.sub(r'\b(the|of|and|republic)\b', '', name.lower())
    cleaned = ''.join(c for c in cleaned if c.isalpha())
    
    # Take first 3 characters as uppercase
    if len(cleaned) >= 3:
        return cleaned[:3].upper()
    return (cleaned + "XX")[:3].upper()


# =============================================================================
# Stadium/City Normalization
# =============================================================================

def generate_stadium_key(stadium_name: str) -> str:
    """
    Generate a URL-friendly key for a stadium name.
    
    Examples:
        "Arena Corinthians" -> "corinthians"
        "Estádio do Maracanã" -> "maracana"
    """
    if not stadium_name:
        return ""
    
    # Remove common prefixes
    prefixes = [
        r'^Arena\s+',
        r'^Estádio\s+',
        r'^Estadio\s+',
        r'^Stadium\s+',
        r'^Allianz\s+',
        r'^do\s+',
        r'^de\s+',
        r'^la\s+',
    ]
    
    key = stadium_name
    for prefix in prefixes:
        key = re.sub(prefix, '', key, flags=re.IGNORECASE)
    
    # Remove diacritics
    key = _remove_diacritics(key.lower())
    
    # Keep only alphanumeric characters
    key = re.sub(r'[^a-z0-9]', '', key)
    
    return key or "stadium"
