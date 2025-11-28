from typing import List, Dict, Any
from app.core.entities import ApiMatch

def calculate_momentum(team_code: str, matches: List[ApiMatch], span: int = 5) -> Dict[str, Any]:
    """
    Calcula el Momentum usando una Media Móvil Exponencial (EMA) de los puntos obtenidos
    en los últimos partidos.

    Args:
        team_code: Código del equipo.
        matches: Lista completa de partidos.
        span: Ventana para el cálculo de EMA (default 5).

    Returns:
        Un diccionario con el score de momentum actual y la historia reciente.
    """
    
    # 1. Filtrar y ordenar partidos del equipo cronológicamente
    team_matches = []
    for match in matches:
        if match.team_a_code == team_code or match.team_b_code == team_code:
            team_matches.append(match)
    
    team_matches.sort(key=lambda x: x.year)

    # 2. Asignar puntos (3, 1, 0)
    points_history = []
    matches_info = []

    for match in team_matches:
        if match.team_a_code == team_code:
            gf = match.score_a
            ga = match.score_b
            opponent = match.team_b
        else:
            gf = match.score_b
            ga = match.score_a
            opponent = match.team_a
        
        if gf > ga:
            points = 3
            result = 'W'
        elif gf < ga:
            points = 0
            result = 'L'
        else:
            points = 1
            result = 'D'
        
        points_history.append(points)
        matches_info.append({
            "opponent": opponent,
            "result": result,
            "points": points,
            "year": match.year,
            "competition": match.competition
        })

    # 3. Calcular EMA
    # Fórmula EMA: Price(t) * k + EMA(y) * (1 – k)
    # k = 2 / (N + 1)
    # N = span
    
    ema_history = []
    if not points_history:
        return {
            "current_momentum": 0,
            "history": []
        }

    k = 2 / (span + 1)
    ema = points_history[0] # Inicializar con el primer valor (SMA de 1 elemento)
    ema_history.append(round(ema, 2))

    for i in range(1, len(points_history)):
        price = points_history[i]
        ema = price * k + ema * (1 - k)
        ema_history.append(round(ema, 2))

    # Combinar info
    history_data = []
    for i in range(len(matches_info)):
        history_data.append({
            **matches_info[i],
            "momentum_score": ema_history[i]
        })

    return {
        "current_momentum": ema_history[-1] if ema_history else 0,
        "history": history_data[-10:] # Retornar solo los últimos 10 para el gráfico
    }
