from fastapi import FastAPI, APIRouter, HTTPException
from typing import List

# 1. Importar los nuevos módulos y los modelos de la API
from app.core.entities import ApiMatch, TeamGroupInfo
from app.data.ingestion.json_reader import load_worldcup_data_from_json, load_worldcup_groups_data_from_json
from app.data.cleaning.match_cleaner import flatten_and_transform_matches, filter_matches_by_team

router = APIRouter(prefix="/api/v1", tags=["analisis"])

@router.get("/teams", response_model=List[TeamGroupInfo])
def obtener_equipos():
    try:
        # 2. Ingesta: Leer los datos crudos del JSON
        worldcup_groups_data = load_worldcup_groups_data_from_json("app/data/datasets/worldcup.groups.json")
        # 3. Procesamiento: Extraer los equipos de los grupos
        teams = [team for group in worldcup_groups_data.groups for team in group.teams]
        return teams
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="No se encontró el archivo de datos del mundial.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar los datos: {str(e)}")

@router.get("/analisis", response_model=List[ApiMatch])
def obtener_analisis():
    try:
        # 2. Ingesta: Leer los datos crudos del JSON
        worldcup_data = load_worldcup_data_from_json("app/data/datasets/worldcup.json")
        # 3. Procesamiento: Transformar los datos al formato de la API
        partidos_procesados = flatten_and_transform_matches(worldcup_data)
        return partidos_procesados
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="No se encontró el archivo de datos del mundial.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar los datos: {str(e)}")

@router.get("/analisis/{team_code}", response_model=List[ApiMatch])
def obtener_partidos_por_equipo(team_code: str):
    try:
        # 1. Ingesta: Leer los datos crudos del JSON
        worldcup_data = load_worldcup_data_from_json("app/data/datasets/worldcup.json")
        # 2. Procesamiento: Transformar los datos al formato de la API
        partidos_procesados = flatten_and_transform_matches(worldcup_data)
        # 3. Filtrado: Seleccionar solo los partidos del equipo especificado
        partidos_filtrados = filter_matches_by_team(partidos_procesados, team_code)
        return partidos_filtrados
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="No se encontró el archivo de datos del mundial.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar los datos: {str(e)}")
		
app = FastAPI(title="Plantilla Predictor - FastAPI")

@app.get("/api/health")
def health(): return {"ok": True}

app.include_router(router)
