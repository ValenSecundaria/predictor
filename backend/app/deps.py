from typing import List
from pathlib import Path
from functools import lru_cache

from app.core.entities import ApiMatch, TeamGroupInfo
from app.data.ingestion.json_reader import load_worldcup_data_from_json, load_worldcup_groups_data_from_json
from app.data.cleaning.match_cleaner import flatten_and_transform_matches

BASE_DIR = Path(__file__).resolve().parents[2] # Sube dos niveles: app/api -> app -> backend
DATASETS_DIR = BASE_DIR / "data" / "datasets"
YEARS = ["2014", "2018"]

@lru_cache(maxsize=None)
def get_all_matches() -> List[ApiMatch]:
    """Carga, procesa y cachea todos los partidos de todos los años."""
    all_matches = []
    for year in YEARS:
        worldcup_json_path = DATASETS_DIR / year / "worldcup.json"
        worldcup_data = load_worldcup_data_from_json(worldcup_json_path)
        all_matches.extend(flatten_and_transform_matches(worldcup_data))
    return all_matches

@lru_cache(maxsize=None)
def get_all_teams() -> List[TeamGroupInfo]:
    """Carga, procesa y cachea todos los equipos de todos los años."""
    all_teams_dict = {}
    for year in YEARS:
        worldcup_groups_json_path = DATASETS_DIR / year / "worldcup.groups.json"
        worldcup_groups_data = load_worldcup_groups_data_from_json(worldcup_groups_json_path)
        for group in worldcup_groups_data.groups:
            for team in group.teams:
                all_teams_dict[team.code] = team
    
    return sorted(list(all_teams_dict.values()), key=lambda x: x.name)