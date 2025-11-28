from typing import List, Dict, Any
from app.core.entities import ApiMatch
from collections import defaultdict

def calculate_goal_stats(team_code: str, matches: List[ApiMatch]) -> Dict[str, Any]:
    """
    Calcula estadísticas de goles a favor y en contra, global y por competición.

    Args:
        team_code: Código del equipo.
        matches: Lista completa de partidos.

    Returns:
        Un diccionario con las estadísticas de goles.
    """
    
    # Estructura de datos para acumular
    stats = {
        "global": {
            "goals_for": 0,
            "goals_against": 0,
            "matches_played": 0,
            "avg_goals_for": 0.0,
            "avg_goals_against": 0.0,
            "goal_difference": 0
        },
        "by_competition": {}
    }

    competition_stats = defaultdict(lambda: {
        "goals_for": 0,
        "goals_against": 0,
        "matches_played": 0
    })

    for match in matches:
        # Verificar si el equipo participó en el partido
        if match.team_a_code == team_code:
            gf = match.score_a
            ga = match.score_b
        elif match.team_b_code == team_code:
            gf = match.score_b
            ga = match.score_a
        else:
            continue # El equipo no jugó este partido

        # Acumular global
        stats["global"]["goals_for"] += gf
        stats["global"]["goals_against"] += ga
        stats["global"]["matches_played"] += 1

        # Acumular por competición
        comp_key = f"{match.competition} {match.year}"
        competition_stats[comp_key]["goals_for"] += gf
        competition_stats[comp_key]["goals_against"] += ga
        competition_stats[comp_key]["matches_played"] += 1

    # Calcular promedios globales
    if stats["global"]["matches_played"] > 0:
        stats["global"]["avg_goals_for"] = round(stats["global"]["goals_for"] / stats["global"]["matches_played"], 2)
        stats["global"]["avg_goals_against"] = round(stats["global"]["goals_against"] / stats["global"]["matches_played"], 2)
        stats["global"]["goal_difference"] = stats["global"]["goals_for"] - stats["global"]["goals_against"]

    # Procesar y calcular promedios por competición
    for comp, data in competition_stats.items():
        avg_gf = 0.0
        avg_ga = 0.0
        diff = 0
        if data["matches_played"] > 0:
            avg_gf = round(data["goals_for"] / data["matches_played"], 2)
            avg_ga = round(data["goals_against"] / data["matches_played"], 2)
            diff = data["goals_for"] - data["goals_against"]
        
        stats["by_competition"][comp] = {
            "goals_for": data["goals_for"],
            "goals_against": data["goals_against"],
            "matches_played": data["matches_played"],
            "avg_goals_for": avg_gf,
            "avg_goals_against": avg_ga,
            "goal_difference": diff
        }

    return stats
