import json
from pathlib import Path
from typing import Dict, Any
from app.core.entities import WorldCupData, WorldCupGroupData


def load_worldcup_data_from_json(file_path: str) -> WorldCupData:
    """
    Lee un archivo JSON, lo valida contra el modelo Pydantic y devuelve un objeto.

    Args:
        file_path: Ruta al archivo JSON de datos del mundial.

    Returns:
        Un objeto WorldCupData con todos los datos del torneo.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return WorldCupData.model_validate(data)


def load_worldcup_groups_data_from_json(file_path: str) -> WorldCupGroupData:
    """
    Lee un archivo JSON, lo valida contra el modelo Pydantic y devuelve un objeto.

    Args:
        file_path: Ruta al archivo JSON de datos del mundial.

    Returns:
        Un objeto WorldCupGroupData con todos los datos de los grupos del torneo.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return WorldCupGroupData.model_validate(data)