"""
GW2Optimizer - Compositions Generate Endpoint
Endpoint pour générer des compositions via prompt avec Mistral 7B
"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.api import dependencies as deps
from app import models

router = APIRouter()


class CompositionGenerateRequest(BaseModel):
    prompt: str
    squad_size: int = 15
    mode: str | None = None


class BuildInfo(BaseModel):
    id: str
    profession: str
    specialization: str
    role: str
    count: int
    weight: float


class SquadResponse(BaseModel):
    id: str
    name: str
    builds: list[BuildInfo]
    weight: float
    synergy: float
    buffs: list[str]
    nerfs: list[str]
    timestamp: str
    mode: str | None
    squad_size: int


class CompositionGenerateResponse(BaseModel):
    squads: list[SquadResponse]
    meta: dict[str, Any]


@router.post("/generate", response_model=CompositionGenerateResponse)
async def generate_composition(
    *,
    db: AsyncSession = Depends(deps.get_async_db),
    request: CompositionGenerateRequest,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Génère une composition optimale via prompt texte.
    
    TODO: Intégrer avec Mistral 7B pour parser le prompt
    TODO: Appeler l'optimizer avec les paramètres extraits
    TODO: Formater le résultat en Squad pour le frontend
    
    Pour l'instant, retourne des données mock pour tester l'interface.
    """
    
    # Mock data pour démonstration
    from datetime import datetime
    
    mode = request.mode or "zerg"
    squad_size = request.squad_size
    
    # Composition mock basée sur le mode
    if mode == "zerg":
        builds = [
            BuildInfo(
                id="1",
                profession="Guardian",
                specialization="Firebrand",
                role="Support",
                count=3,
                weight=0.85
            ),
            BuildInfo(
                id="2",
                profession="Engineer",
                specialization="Scrapper",
                role="Support",
                count=2,
                weight=1.1
            ),
            BuildInfo(
                id="3",
                profession="Revenant",
                specialization="Herald",
                role="Support",
                count=2,
                weight=0.95
            ),
            BuildInfo(
                id="4",
                profession="Necromancer",
                specialization="Scourge",
                role="DPS",
                count=3,
                weight=0.92
            ),
            BuildInfo(
                id="5",
                profession="Elementalist",
                specialization="Tempest",
                role="Healer",
                count=2,
                weight=0.88
            ),
            BuildInfo(
                id="6",
                profession="Warrior",
                specialization="Spellbreaker",
                role="DPS",
                count=3,
                weight=0.90
            ),
        ]
        buffs = ["Quickness +95%", "Stability +90%", "Resistance +85%"]
        nerfs = []
    elif mode == "havoc":
        builds = [
            BuildInfo(
                id="1",
                profession="Guardian",
                specialization="Firebrand",
                role="Support",
                count=2,
                weight=0.85
            ),
            BuildInfo(
                id="2",
                profession="Engineer",
                specialization="Scrapper",
                role="Support",
                count=2,
                weight=1.1
            ),
            BuildInfo(
                id="4",
                profession="Necromancer",
                specialization="Scourge",
                role="DPS",
                count=2,
                weight=0.92
            ),
            BuildInfo(
                id="7",
                profession="Elementalist",
                specialization="Weaver",
                role="DPS",
                count=2,
                weight=0.94
            ),
        ]
        buffs = ["Quickness +90%", "Stability +85%"]
        nerfs = ["Lower sustain"]
    else:  # roaming
        builds = [
            BuildInfo(
                id="8",
                profession="Guardian",
                specialization="Willbender",
                role="DPS",
                count=1,
                weight=0.88
            ),
            BuildInfo(
                id="2",
                profession="Engineer",
                specialization="Scrapper",
                role="Support",
                count=1,
                weight=1.1
            ),
            BuildInfo(
                id="7",
                profession="Elementalist",
                specialization="Weaver",
                role="DPS",
                count=1,
                weight=0.94
            ),
        ]
        buffs = ["High mobility", "Burst damage"]
        nerfs = ["Limited sustain"]
    
    squad = SquadResponse(
        id="squad-1",
        name=f"Squad Alpha - {mode.capitalize()}",
        builds=builds,
        weight=0.95,
        synergy=0.87,
        buffs=buffs,
        nerfs=nerfs,
        timestamp=datetime.now().isoformat(),
        mode=mode,
        squad_size=squad_size
    )
    
    return CompositionGenerateResponse(
        squads=[squad],
        meta={
            "total_players": squad_size,
            "avg_weight": 0.95,
            "avg_synergy": 0.87,
        }
    )
