from typing import List, Dict, Any
from app.core.entities import ApiMatch

def calculate_head_to_head(team_a_code: str, team_b_code: str, matches: List[ApiMatch]) -> Dict[str, Any]:
    """
    Calcula el historial de enfrentamientos entre dos equipos.

    Args:
        team_a_code: Código del primer equipo.
        team_b_code: Código del segundo equipo.
        matches: Lista completa de partidos.

    Returns:
        Un diccionario con las estadísticas del enfrentamiento.
    """
    head_to_head_matches = []
    
    stats = {
        "total_matches": 0,
        "wins_a": 0,
        "wins_b": 0,
        "draws": 0,
        "goals_a": 0,
        "goals_b": 0,
        "recent_matches": []
    }

    for match in matches:
        # Verificar si el partido es entre los dos equipos (en cualquier orden)
        is_match_between = (
            (match.team_a_code == team_a_code and match.team_b_code == team_b_code) or
            (match.team_a_code == team_b_code and match.team_b_code == team_a_code)
        )

        if is_match_between:
            head_to_head_matches.append(match)
            stats["total_matches"] += 1

            # Determinar goles y ganador desde la perspectiva de A vs B
            if match.team_a_code == team_a_code:
                score_a = match.score_a
                score_b = match.score_b
            else:
                score_a = match.score_b
                score_b = match.score_a
            
            stats["goals_a"] += score_a
            stats["goals_b"] += score_b

            if score_a > score_b:
                stats["wins_a"] += 1
            elif score_b > score_a:
                stats["wins_b"] += 1
            else:
                stats["draws"] += 1

    head_to_head_matches.sort(key=lambda x: x.year, reverse=True)

    stats["recent_matches"] = head_to_head_matches

    return stats
