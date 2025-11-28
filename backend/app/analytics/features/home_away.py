from typing import List, Dict, Any
from app.core.entities import ApiMatch

def calculate_home_away_stats(team_code: str, matches: List[ApiMatch]) -> Dict[str, Any]:
    """
    Calcula estadísticas diferenciadas por condición de local (Team A) y visitante (Team B).

    Args:
        team_code: Código del equipo.
        matches: Lista completa de partidos.

    Returns:
        Un diccionario con las estadísticas de local y visitante.
    """
    
    stats = {
        "home": {
            "matches_played": 0,
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "goals_for": 0,
            "goals_against": 0,
            "win_percentage": 0.0,
            "avg_goals_for": 0.0,
            "avg_goals_against": 0.0
        },
        "away": {
            "matches_played": 0,
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "goals_for": 0,
            "goals_against": 0,
            "win_percentage": 0.0,
            "avg_goals_for": 0.0,
            "avg_goals_against": 0.0
        }
    }

    for match in matches:
        # Verificar si el equipo jugó y en qué condición
        if match.team_a_code == team_code:
            condition = "home"
            gf = match.score_a
            ga = match.score_b
        elif match.team_b_code == team_code:
            condition = "away"
            gf = match.score_b
            ga = match.score_a
        else:
            continue # El equipo no jugó este partido

        stats[condition]["matches_played"] += 1
        stats[condition]["goals_for"] += gf
        stats[condition]["goals_against"] += ga

        if gf > ga:
            stats[condition]["wins"] += 1
        elif gf < ga:
            stats[condition]["losses"] += 1
        else:
            stats[condition]["draws"] += 1

    # Calcular porcentajes y promedios
    for condition in ["home", "away"]:
        mp = stats[condition]["matches_played"]
        if mp > 0:
            stats[condition]["win_percentage"] = round((stats[condition]["wins"] / mp) * 100, 1)
            stats[condition]["avg_goals_for"] = round(stats[condition]["goals_for"] / mp, 2)
            stats[condition]["avg_goals_against"] = round(stats[condition]["goals_against"] / mp, 2)

    return stats
