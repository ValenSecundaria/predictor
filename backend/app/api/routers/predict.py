from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from app.core.entities import ApiMatch
from app.analytics.features.history import calculate_head_to_head
from app.analytics.features.goal_stats import calculate_goal_stats
from app.analytics.features.streaks import calculate_streak_stats
from app.analytics.features.home_away import calculate_home_away_stats
from app.analytics.features.momentum import calculate_momentum
from app.analytics.features.graph_analysis import calculate_graph_stats

router = APIRouter(prefix="/api/v1/predict", tags=["predict"])

# Placeholder para los datos, se deben setear al inicio de la app
MATCHES_STORE = []

@router.get("/history/{team_a}/{team_b}")
def get_history(team_a: str, team_b: str):
    """
    Obtiene el historial de enfrentamientos entre dos equipos.
    """
    if not MATCHES_STORE:
        raise HTTPException(status_code=503, detail="Data not loaded yet")
    
    stats = calculate_head_to_head(team_a, team_b, MATCHES_STORE)
    return stats

@router.get("/stats/goals/{team_code}")
def get_goal_stats(team_code: str):
    """
    Obtiene estadísticas de goles a favor y en contra (global y por competición).
    """
    if not MATCHES_STORE:
        raise HTTPException(status_code=503, detail="Data not loaded yet")
    
    stats = calculate_goal_stats(team_code, MATCHES_STORE)
    return stats

@router.get("/stats/streaks/{team_code}")
def get_streak_stats(team_code: str):
    """
    Obtiene estadísticas de rachas y probabilidades de transición.
    """
    if not MATCHES_STORE:
        raise HTTPException(status_code=503, detail="Data not loaded yet")
    
    stats = calculate_streak_stats(team_code, MATCHES_STORE)
    return stats

@router.get("/stats/home-away/{team_code}")
def get_home_away_stats(team_code: str):
    """
    Obtiene estadísticas diferenciadas por condición de local y visitante.
    """
    if not MATCHES_STORE:
        raise HTTPException(status_code=503, detail="Data not loaded yet")
    
    stats = calculate_home_away_stats(team_code, MATCHES_STORE)
    return stats

@router.get("/stats/momentum/{team_code}")
def get_momentum_stats(team_code: str):
    """
    Obtiene el Momentum (EMA) del equipo.
    """
    if not MATCHES_STORE:
        raise HTTPException(status_code=503, detail="Data not loaded yet")
    
    stats = calculate_momentum(team_code, MATCHES_STORE)
    return stats

@router.get("/stats/graph/{team_code}")
def get_graph_stats(team_code: str):
    """
    Obtiene estadísticas de grafo (victorias indirectas).
    """
    if not MATCHES_STORE:
        raise HTTPException(status_code=503, detail="Data not loaded yet")
    
    stats = calculate_graph_stats(team_code, MATCHES_STORE)
    return stats

from app.analytics.features.goal_percentage import calculate_goal_percentage_stats
from app.analytics.features.effectiveness import calculate_effectiveness_stats
from app.analytics.features.possession import calculate_possession_stats

@router.get("/stats/goal-percentage/{team_code}")
def get_goal_percentage_stats(team_code: str):
    """
    Obtiene estadísticas de porcentaje de goles (goles por partido).
    """
    if not MATCHES_STORE:
        raise HTTPException(status_code=503, detail="Data not loaded yet")
    
    stats = calculate_goal_percentage_stats(team_code, MATCHES_STORE)
    return stats

@router.get("/stats/effectiveness/{team_code}")
def get_effectiveness_stats(team_code: str):
    """
    Obtiene estadísticas de efectividad (Goles / Tiros al arco).
    """
    if not MATCHES_STORE:
        raise HTTPException(status_code=503, detail="Data not loaded yet")
    
    stats = calculate_effectiveness_stats(team_code, MATCHES_STORE)
    return stats

@router.get("/stats/possession/{team_code}")
def get_possession_stats(team_code: str):
    """
    Obtiene estadísticas de posesión en 3/4 de cancha.
    """
    if not MATCHES_STORE:
        raise HTTPException(status_code=503, detail="Data not loaded yet")
    
    stats = calculate_possession_stats(team_code, MATCHES_STORE)
    return stats

from app.analytics.match_predictor import predict_match

@router.get("/match-prediction/{team_a}/{team_b}")
def get_match_prediction(team_a: str, team_b: str):
    """
    Predice el resultado entre dos equipos usando un algoritmo ponderado.
    """
    if not MATCHES_STORE:
        raise HTTPException(status_code=503, detail="Data not loaded yet")
    
    prediction = predict_match(team_a, team_b, MATCHES_STORE)
    return prediction
