from typing import List, Dict, Any
from app.core.entities import ApiMatch

def calculate_goal_percentage_stats(team_code: str, matches: List[ApiMatch]) -> Dict[str, Any]:
    """
    Calcula el porcentaje de goles (goles por partido) y estructura para futura expansión.
    
    Args:
        team_code: Código del equipo.
        matches: Lista completa de partidos.
        
    Returns:
        Diccionario con estadísticas de porcentaje de goles.
    """
    
    total_goals = 0
    matches_played = 0
    
    for match in matches:
        if match.team_a_code == team_code:
            total_goals += match.score_a
            matches_played += 1
        elif match.team_b_code == team_code:
            total_goals += match.score_b
            matches_played += 1
            
    goals_per_match = 0.0
    if matches_played > 0:
        goals_per_match = round(total_goals / matches_played, 2)
        
    return {
        "available": True,
        "goals_per_match": goals_per_match,
        "total_goals": total_goals,
        "matches_played": matches_played,
        "message": "Datos calculados en base a historial disponible."
    }
