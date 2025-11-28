from typing import List, Dict, Any
from app.core.entities import ApiMatch
from app.analytics.features.history import calculate_head_to_head
from app.analytics.features.momentum import calculate_momentum
from app.analytics.features.goal_stats import calculate_goal_stats
from app.analytics.features.streaks import calculate_streak_stats

def predict_match(team_a_code: str, team_b_code: str, matches: List[ApiMatch]) -> Dict[str, Any]:
    """
    Predice el resultado de un partido entre dos equipos basándose en múltiples factores ponderados.
    
    Factores:
    1. Historial directo (Head-to-Head) - 30%
    2. Momentum (Forma reciente) - 25%
    3. Poder de gol (Goles a favor vs en contra) - 25%
    4. Rachas (Streak actual) - 10%
    5. Factor "Localía" (Simulado/General) - 10%
    """
    
    # 1. Historial Directo
    h2h = calculate_head_to_head(team_a_code, team_b_code, matches)
    h2h_score_a = 0.5
    h2h_score_b = 0.5
    
    if h2h['total_matches'] > 0:
        # Ponderar victorias recientes más alto? Por ahora simple win rate
        total = h2h['total_matches']
        # Damos 0.5 puntos por empate
        points_a = h2h['wins_a'] + (h2h['draws'] * 0.5)
        points_b = h2h['wins_b'] + (h2h['draws'] * 0.5)
        h2h_score_a = points_a / total
        h2h_score_b = points_b / total

    # 2. Momentum
    mom_a = calculate_momentum(team_a_code, matches)
    mom_b = calculate_momentum(team_b_code, matches)
    
    # Normalizar momentum (0 a 100 -> 0.0 a 1.0 aprox)
    # Asumimos que el momentum suele estar entre 0 y 3 (puntos por partido)
    # Un momentum de 3.0 es perfecto (todo ganado).
    m_score_a = min(mom_a['current_momentum'] / 3.0, 1.0)
    m_score_b = min(mom_b['current_momentum'] / 3.0, 1.0)

    # 3. Poder de Gol
    goals_a = calculate_goal_stats(team_a_code, matches)
    goals_b = calculate_goal_stats(team_b_code, matches)
    
    # A ataca vs B defiende
    attack_a = goals_a['global']['avg_goals_for']
    defense_b = goals_b['global']['avg_goals_against']
    # B ataca vs A defiende
    attack_b = goals_b['global']['avg_goals_for']
    defense_a = goals_a['global']['avg_goals_against']
    
    # Score simple: ataque * (1 + debilidad defensa rival)
    # Si defensa es 0 (muy buena), no bonifica. Si es alta, bonifica.
    power_a = attack_a * (1 + (defense_b / 2.0)) 
    power_b = attack_b * (1 + (defense_a / 2.0))
    
    total_power = power_a + power_b
    if total_power == 0:
        g_score_a = 0.5
        g_score_b = 0.5
    else:
        g_score_a = power_a / total_power
        g_score_b = power_b / total_power

    # 4. Rachas
    streak_a = calculate_streak_stats(team_a_code, matches)
    streak_b = calculate_streak_stats(team_b_code, matches)
    
    # Valorar racha actual
    def get_streak_val(streak_data):
        if not streak_data['current_streak']['type']: return 0
        count = streak_data['current_streak']['count']
        if streak_data['current_streak']['type'] == 'W': return count
        if streak_data['current_streak']['type'] == 'D': return count * 0.2
        if streak_data['current_streak']['type'] == 'L': return -count
        return 0

    s_val_a = get_streak_val(streak_a)
    s_val_b = get_streak_val(streak_b)
    
    # Sigmoid-ish normalization para streak (-5 a 5 range aprox)
    # Simple: (val + 5) / 10 -> range 0 to 1
    s_score_a = max(0.0, min(1.0, (s_val_a + 5) / 10))
    s_score_b = max(0.0, min(1.0, (s_val_b + 5) / 10))

    # Pesos
    W_H2H = 0.30
    W_MOM = 0.25
    W_GOAL = 0.25
    W_STREAK = 0.20 # Subimos streak para completar 100% (quitamos localia por ahora ya que es neutral)

    final_score_a = (h2h_score_a * W_H2H) + (m_score_a * W_MOM) + (g_score_a * W_GOAL) + (s_score_a * W_STREAK)
    final_score_b = (h2h_score_b * W_H2H) + (m_score_b * W_MOM) + (g_score_b * W_GOAL) + (s_score_b * W_STREAK)

    # Normalizar a porcentajes que sumen 100
    total_score = final_score_a + final_score_b
    if total_score == 0:
        prob_a = 50.0
        prob_b = 50.0
    else:
        prob_a = (final_score_a / total_score) * 100
        prob_b = (final_score_b / total_score) * 100

    return {
        "team_a": team_a_code,
        "team_b": team_b_code,
        "probability_a": round(prob_a, 1),
        "probability_b": round(prob_b, 1),
        "details": {
            "h2h_score_a": round(h2h_score_a, 2),
            "h2h_score_b": round(h2h_score_b, 2),
            "momentum_score_a": round(m_score_a, 2),
            "momentum_score_b": round(m_score_b, 2),
            "goal_power_a": round(g_score_a, 2),
            "goal_power_b": round(g_score_b, 2),
            "streak_score_a": round(s_score_a, 2),
            "streak_score_b": round(s_score_b, 2)
        },
        "factors": {
            "h2h_weight": W_H2H,
            "momentum_weight": W_MOM,
            "goal_weight": W_GOAL,
            "streak_weight": W_STREAK
        }
    }
