from typing import List, Dict
from app.core.entities import ApiMatch, TeamStats

def calculate_team_stats(matches: List[ApiMatch], team_code: str) -> TeamStats:
    """
    Calcula las estadísticas de victorias, derrotas y empates para un equipo específico.

    Args:
        matches: La lista completa de partidos.
        team_code: El código del equipo para el cual calcular las estadísticas.

    Returns:
        Un objeto TeamStats con las estadísticas calculadas.
    """
    wins = 0
    losses = 0
    draws = 0
    goals_for = 0
    goals_against = 0
    
    team_matches = [m for m in matches if m.team_a_code == team_code or m.team_b_code == team_code]
    
    if not team_matches:
        return TeamStats(wins=0, losses=0, draws=0, total_matches=0, win_percentage=0, loss_percentage=0, draw_percentage=0, goals_for=0, goals_against=0)

    for match in team_matches:
        is_team_a = match.team_a_code == team_code
        
        if match.score_a == match.score_b:
            draws += 1
        elif (is_team_a and match.score_a > match.score_b) or (not is_team_a and match.score_b > match.score_a):
            wins += 1
        else:
            losses += 1
            
        if is_team_a:
            goals_for += match.score_a
            goals_against += match.score_b
        else:
            goals_for += match.score_b
            goals_against += match.score_a
            
    total_matches = len(team_matches)
    win_percentage = (wins / total_matches) * 100 if total_matches > 0 else 0
    loss_percentage = (losses / total_matches) * 100 if total_matches > 0 else 0
    draw_percentage = (draws / total_matches) * 100 if total_matches > 0 else 0

    return TeamStats(
        wins=wins,
        losses=losses,
        draws=draws,
        total_matches=total_matches,
        win_percentage=win_percentage,
        loss_percentage=loss_percentage,
        draw_percentage=draw_percentage,
        goals_for=goals_for,
        goals_against=goals_against
    )