from typing import List, Dict, Any
from app.core.entities import ApiMatch

def calculate_streak_stats(team_code: str, matches: List[ApiMatch]) -> Dict[str, Any]:
    """
    Calcula estadísticas de rachas y probabilidades de transición.

    Args:
        team_code: Código del equipo.
        matches: Lista completa de partidos.

    Returns:
        Un diccionario con las estadísticas de rachas.
    """
    
    # 1. Filtrar y ordenar partidos del equipo cronológicamente
    team_matches = []
    for match in matches:
        if match.team_a_code == team_code or match.team_b_code == team_code:
            team_matches.append(match)
    
    team_matches.sort(key=lambda x: x.year)

    # 2. Determinar resultados (W, D, L)
    results = []
    for match in team_matches:
        if match.team_a_code == team_code:
            gf = match.score_a
            ga = match.score_b
        else:
            gf = match.score_b
            ga = match.score_a
        
        if gf > ga:
            results.append('W')
        elif gf < ga:
            results.append('L')
        else:
            results.append('D')

    # 3. Calcular rachas
    current_streak = {"type": None, "count": 0}
    longest_streaks = {"W": 0, "D": 0, "L": 0, "Unbeaten": 0} # Unbeaten = W or D
    
    if results:
        # Current streak
        current_streak["type"] = results[-1]
        count = 0
        for res in reversed(results):
            if res == current_streak["type"]:
                count += 1
            else:
                break
        current_streak["count"] = count

        # Longest streaks
        temp_streaks = {"W": 0, "D": 0, "L": 0, "Unbeaten": 0}
        
        for res in results:
            # W, D, L
            for key in ["W", "D", "L"]:
                if res == key:
                    temp_streaks[key] += 1
                else:
                    longest_streaks[key] = max(longest_streaks[key], temp_streaks[key])
                    temp_streaks[key] = 0
            
            # Unbeaten
            if res in ["W", "D"]:
                temp_streaks["Unbeaten"] += 1
            else:
                longest_streaks["Unbeaten"] = max(longest_streaks["Unbeaten"], temp_streaks["Unbeaten"])
                temp_streaks["Unbeaten"] = 0
        
        # Final check for streaks ending at the last match
        for key in ["W", "D", "L", "Unbeaten"]:
            longest_streaks[key] = max(longest_streaks[key], temp_streaks[key])

    # 4. Probabilidades de transición (Markov)
    # P(Next=X | Prev=Y)
    transitions = {
        "W": {"W": 0, "D": 0, "L": 0, "total": 0},
        "D": {"W": 0, "D": 0, "L": 0, "total": 0},
        "L": {"W": 0, "D": 0, "L": 0, "total": 0}
    }

    for i in range(len(results) - 1):
        prev = results[i]
        next_res = results[i+1]
        transitions[prev][next_res] += 1
        transitions[prev]["total"] += 1

    probabilities = {}
    for prev_res in ["W", "D", "L"]:
        total = transitions[prev_res]["total"]
        if total > 0:
            probabilities[prev_res] = {
                "W": round(transitions[prev_res]["W"] / total, 2),
                "D": round(transitions[prev_res]["D"] / total, 2),
                "L": round(transitions[prev_res]["L"] / total, 2),
                "sample_size": total
            }
        else:
            probabilities[prev_res] = {
                "W": 0, "D": 0, "L": 0, "sample_size": 0
            }

    return {
        "current_streak": current_streak,
        "longest_streaks": longest_streaks,
        "transitions": probabilities,
        "total_matches": len(results)
    }
