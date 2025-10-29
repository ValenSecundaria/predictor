import re
from typing import List, Dict, Any, Optional

class Goal(Dict):
    player: str
    minute: int

class Match(Dict):
    team_a: str
    team_b: str
    score_a: int
    score_b: int
    goals: List[Goal]

def parse_matches_from_txt(file_path: str) -> List[Match]:
    """
    Lee un archivo de texto y extrae la información de los partidos.
    Asume que los partidos están separados por al menos una línea en blanco.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    matches_data = content.strip().split('\n\n')
    parsed_matches: List[Match] = []

    for match_block in matches_data:
        lines = match_block.strip().split('\n')
        if not lines:
            continue

        # Parsear la línea del resultado: "EquipoA X - Y EquipoB"
        result_line = lines[0]
        result_match = re.match(r'(.+?)\s+(\d+)\s*-\s*(\d+)\s+(.+)', result_line)
        if not result_match:
            continue

        team_a, score_a, score_b, team_b = result_match.groups()

        # Parsear los goles
        goals: List[Goal] = []
        for goal_line in lines[1:]:
            goal_match = re.match(r'(.+?)\s+(\d+)\'', goal_line)
            if goal_match:
                player, minute = goal_match.groups()
                goals.append({"player": player.strip(), "minute": int(minute)})

        parsed_matches.append({
            "team_a": team_a.strip(), "score_a": int(score_a),
            "team_b": team_b.strip(), "score_b": int(score_b),
            "goals": goals
        })
    return parsed_matches
