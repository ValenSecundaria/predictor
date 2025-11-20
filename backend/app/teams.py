from fastapi import APIRouter, Depends
from typing import List

from app.core.entities import TeamGroupInfo
from app.api.deps import get_all_teams

router = APIRouter()

@router.get(
    "/teams",
    response_model=List[TeamGroupInfo],
    tags=["Teams"]
)
def get_teams(teams: List[TeamGroupInfo] = Depends(get_all_teams)):
    return teams