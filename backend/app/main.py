from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
from typing import List
from app.file_reader import parse_matches_from_txt

# --- Nuevos modelos Pydantic para representar los datos del partido ---

class Goal(BaseModel):
    player: str
    minute: int

class Match(BaseModel):
    team_a: str
    team_b: str
    score_a: int
    score_b: int
    goals: List[Goal]

router = APIRouter(prefix="/api/v1", tags=["analisis"])

@router.get("/analisis", response_model=List[Match])
def obtener_analisis():
    # Usamos el nuevo parser para leer los datos del archivo .txt
    partidos = parse_matches_from_txt("app/partidos.txt")
    return partidos

app = FastAPI(title="Plantilla Predictor - FastAPI")

@app.get("/api/health")
def health(): return {"ok": True}

app.include_router(router)
