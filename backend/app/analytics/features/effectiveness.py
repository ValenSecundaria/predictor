from typing import List, Dict, Any
from app.core.entities import ApiMatch

def calculate_effectiveness_stats(team_code: str, matches: List[ApiMatch]) -> Dict[str, Any]:
    """
    Estructura para Efectividad (Goles / Tiros al arco).
    Actualmente retorna 'no disponible' ya que no tenemos datos de tiros al arco.
    
    Args:
        team_code: Código del equipo.
        matches: Lista completa de partidos.
        
    Returns:
        Diccionario indicando que los datos no están disponibles.
    """
    
    # Aquí se implementaría la lógica si tuviéramos 'shots_on_target' en los partidos.
    # Por ahora, verificamos si algún partido tiene esa data (que sabemos que no).
    
    has_shots_data = False
    # for match in matches:
    #     if hasattr(match, 'shots_on_target'): ...
    
    if not has_shots_data:
        return {
            "available": False,
            "message": "Dato no disponible: Se requiere información de 'Tiros al arco' en el dataset."
        }
    
    return {
        "available": True,
        "effectiveness_percentage": 0.0 # Placeholder
    }
