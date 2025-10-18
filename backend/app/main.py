from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any, Protocol

class Extractor(Protocol):
    def extraer_datos(self) -> List[Dict[str, Any]]:
        ...

class MockExtractor:
    def extraer_datos(self) -> List[Dict[str, Any]]:
        return [
            {"equipo": "Argentina", "goles": 2},
            {"equipo": "Argentina", "goles": None},
            {"equipo": "Francia", "goles": 1},
            {"equipo": "Argentina", "goles": 3},
            {"equipo": None, "goles": 0},
        ]

class AnaliticaResultado(BaseModel):
    total_registros: int
    registros_validos: int
    goles_por_equipo: Dict[str, int]

def limpieza_basica(registros: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    limpios: List[Dict[str, Any]] = []
    for r in registros:
        equipo = r.get("equipo")
        goles = r.get("goles")
        if equipo is None or goles is None:
            continue
        try:
            goles = int(goles)
        except Exception:
            continue
        limpios.append({"equipo": str(equipo), "goles": goles})
    return limpios

def logica_conteo(limpios: List[Dict[str, Any]]) -> AnaliticaResultado:
    goles_por_equipo: Dict[str, int] = {}
    for r in limpios:
        goles_por_equipo[r["equipo"]] = goles_por_equipo.get(r["equipo"], 0) + r["goles"]
    return AnaliticaResultado(
        total_registros=len(limpios),
        registros_validos=len(limpios),
        goles_por_equipo=goles_por_equipo
    )

router = APIRouter(prefix="/api/v1", tags=["analisis"])

@router.get("/analisis", response_model=AnaliticaResultado)
def obtener_analisis():
    extractor: Extractor = MockExtractor()
    brutos = extractor.extraer_datos()
    limpios = limpieza_basica(brutos)
    resultado = logica_conteo(limpios)
    return resultado

app = FastAPI(title="Plantilla Predictor - FastAPI")

@app.get("/api/health")
def health(): return {"ok": True}

app.include_router(router)
