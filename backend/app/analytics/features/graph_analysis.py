from typing import List, Dict, Any
from app.core.entities import ApiMatch

def calculate_graph_stats(team_code: str, matches: List[ApiMatch]) -> Dict[str, Any]:
    """
    Calcula estadísticas de grafo, específicamente "Dominancia Indirecta" (Transitividad).
    Si A ganó a B, y B ganó a C, entonces A tiene dominancia indirecta sobre C.

    Args:
        team_code: Código del equipo (Team A).
        matches: Lista completa de partidos.

    Returns:
        Un diccionario con las relaciones indirectas encontradas.
    """
    
    # 1. Construir grafo de victorias (Winner -> Loser)
    # Estructura: { "WinnerCode": ["LoserCode1", "LoserCode2", ...] }
    wins_graph = {}
    teams_map = {} # Code -> Name

    for match in matches:
        # Guardar nombres
        teams_map[match.team_a_code] = match.team_a
        teams_map[match.team_b_code] = match.team_b

        winner = None
        loser = None

        if match.score_a > match.score_b:
            winner = match.team_a_code
            loser = match.team_b_code
        elif match.score_b > match.score_a:
            winner = match.team_b_code
            loser = match.team_a_code
        
        if winner and loser:
            if winner not in wins_graph:
                wins_graph[winner] = []
            wins_graph[winner].append(loser)

    # 2. Encontrar victorias directas del equipo analizado
    direct_victims = wins_graph.get(team_code, [])
    
    # 3. Encontrar victorias indirectas (2do grado)
    indirect_relations = []
    
    # Evitar duplicados y ciclos triviales
    seen_indirect_victims = set()

    for victim_code in direct_victims:
        # Rivales a los que 'victim_code' ganó
        second_order_victims = wins_graph.get(victim_code, [])
        
        for indirect_victim_code in second_order_victims:
            # No contar si el rival indirecto es el mismo equipo analizado (ciclo A->B->A)
            # Y no contar si ya es una víctima directa (A->B y A->C, pero B->C. A ya le ganó a C directamente)
            # Aunque "Dominancia Indirecta" sigue siendo válida incluso si hubo directa, 
            # para "descubrimiento" es más interesante si NO jugaron o si perdió.
            # Por simplicidad, listamos todas las transitividades válidas.
            
            if indirect_victim_code != team_code:
                relation_id = f"{victim_code}-{indirect_victim_code}"
                if relation_id not in seen_indirect_victims:
                    indirect_relations.append({
                        "intermediate_team": teams_map.get(victim_code, victim_code),
                        "indirect_victim": teams_map.get(indirect_victim_code, indirect_victim_code),
                        "intermediate_code": victim_code,
                        "indirect_victim_code": indirect_victim_code
                    })
                    seen_indirect_victims.add(relation_id)

    return {
        "indirect_wins": indirect_relations,
        "total_indirect_wins": len(indirect_relations)
    }
