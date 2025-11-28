from typing import List, Dict, Any
from app.core.entities import ApiMatch

def calculate_possession_stats(team_code: str, matches: List[ApiMatch]) -> Dict[str, Any]:
    """
    Estructura para Posesión en 3/4 de cancha.
    Actualmente retorna 'no disponible' ya que no tenemos datos de posesión detallada.
    
    Args:
        team_code: Código del equipo.
        matches: Lista completa de partidos.
        
    Returns:
        Diccionario indicando que los datos no están disponibles.
    """
    
    has_possession_data = False
    
    if not has_possession_data:
        return {
            "available": False,
            "message": "Dato no disponible: Se requiere información de 'Posesión en zona de ataque' en el dataset."
        }
    
    return {
        "available": True,
        "possession_3rd_quarter_avg": 0.0 # Placeholder
    }
