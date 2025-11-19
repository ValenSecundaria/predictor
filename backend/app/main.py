from fastapi import FastAPI, APIRouter, HTTPException
from typing import List
from pathlib import Path

# 1. Importar los nuevos módulos y los modelos de la API
from app.core.entities import ApiMatch, TeamGroupInfo
from app.data.ingestion.json_reader import load_worldcup_data_from_json, load_worldcup_groups_data_from_json
from app.data.cleaning.match_cleaner import flatten_and_transform_matches, filter_matches_by_team

router = APIRouter(prefix="/api/v1", tags=["analisis"])

# --- Solución: Definir rutas a los archivos de datos de forma robusta ---
# Obtenemos la ruta al directorio donde se encuentra este archivo (main.py)
BASE_DIR = Path(__file__).resolve().parent
# Construimos las rutas a los archivos JSON basándonos en la ubicación de main.py
WORLDCUP_GROUPS_JSON_PATH = BASE_DIR / "data" / "datasets" / "worldcup.groups.json"
WORLDCUP_JSON_PATH = BASE_DIR / "data" / "datasets" / "worldcup.json"

# --- Solución: Cargar y procesar los datos una sola vez al iniciar la app ---
try:
    # Cargar y procesar datos de equipos
    worldcup_groups_data = load_worldcup_groups_data_from_json(WORLDCUP_GROUPS_JSON_PATH)
    TEAMS_DATA = [team for group in worldcup_groups_data.groups for team in group.teams]

    # Cargar y procesar datos de partidos
    worldcup_data = load_worldcup_data_from_json(WORLDCUP_JSON_PATH)
    MATCHES_DATA = flatten_and_transform_matches(worldcup_data)
except FileNotFoundError as e:
    # Si los archivos no existen al iniciar, la aplicación no puede funcionar.
    # Es mejor que falle rápido y con un mensaje claro.
    raise RuntimeError(f"No se pudo iniciar la aplicación: Archivo de datos no encontrado. {e}")
except Exception as e:
    raise RuntimeError(f"Error crítico al procesar datos durante el inicio: {e}")

@router.get("/teams", response_model=List[TeamGroupInfo])
def obtener_equipos():
    return TEAMS_DATA

@router.get("/analisis", response_model=List[ApiMatch])
def obtener_analisis():
    return MATCHES_DATA

@router.get("/analisis/{team_code}", response_model=List[ApiMatch])
def obtener_partidos_por_equipo(team_code: str):
    partidos_filtrados = filter_matches_by_team(MATCHES_DATA, team_code)
    return partidos_filtrados
		
app = FastAPI(title="Plantilla Predictor - FastAPI")

@app.get("/")
def read_root():
    return {"message": "Bienvenido al API del Predictor Mundial"}

@app.get("/api/health")
def health(): return {"ok": True}

app.include_router(router)
