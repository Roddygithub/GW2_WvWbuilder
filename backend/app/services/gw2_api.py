"""
Service d'intégration avec l'API Guild Wars 2.

Ce module fournit des méthodes pour interagir avec l'API officielle de Guild Wars 2,
y compris la récupération des métiers, compétences, caractéristiques, etc.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

import httpx
from fastapi import HTTPException, status
from pydantic import BaseModel, HttpUrl, Field

from app.core.config import settings
from app.core.cache import cache

# Configuration du logging
logger = logging.getLogger(__name__)


# Modèles de données Pydantic
class GW2Skill(BaseModel):
    """Modèle pour les compétences GW2."""

    id: int
    name: str
    description: Optional[str] = None
    icon: Optional[HttpUrl] = None
    type: Optional[str] = None
    weapon_type: Optional[str] = None
    professions: Optional[List[str]] = []
    slot: Optional[str] = None
    facts: Optional[List[Dict[str, Any]]] = []
    traited_facts: Optional[List[Dict[str, Any]]] = []


class GW2Trait(BaseModel):
    """Modèle pour les caractéristiques GW2."""

    id: int
    name: str
    description: str
    icon: Optional[HttpUrl] = None
    specialization: int
    tier: str
    slot: str
    facts: List[Dict[str, Any]] = []
    traited_facts: List[Dict[str, Any]] = []


class GW2Profession(BaseModel):
    """Modèle pour les métiers GW2."""

    id: str
    name: str
    icon: HttpUrl
    icon_big: Optional[HttpUrl] = Field(None, alias="icon_big")
    specializations: List[int] = []
    weapons: Dict[str, str] = {}
    training: List[Dict[str, Any]] = []
    flags: List[str] = []
    skills: List[GW2Skill] = []


class GW2Specialization(BaseModel):
    """Modèle pour les spécialisations GW2."""

    id: int
    name: str
    profession: str
    elite: bool
    minor_traits: List[int] = []
    major_traits: List[int] = []
    icon: Optional[HttpUrl] = None
    background: Optional[HttpUrl] = None


class GW2APIService:
    """Service pour interagir avec l'API Guild Wars 2."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialise le service avec une clé API optionnelle."""
        self.api_key = api_key or settings.GW2_API_KEY
        self.base_url = settings.GW2_API_BASE_URL.rstrip("/")
        self.timeout = 10.0  # Timeout en secondes
        self.retry_attempts = 3
        self.retry_delay = 1.0  # Délai initial en secondes

        # Configuration des en-têtes par défaut
        self.default_headers = {
            "Accept": "application/json",
            "User-Agent": f"GW2_WvWbuilder/{settings.PROJECT_VERSION}",
            "X-Schema-Version": settings.GW2_API_SCHEMA_VERSION,
        }

        if self.api_key:
            self.default_headers["Authorization"] = f"Bearer {self.api_key}"

    async def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        use_cache: bool = True,
        cache_ttl: int = 3600,  # 1 heure par défaut
    ) -> Any:
        """
        Effectue une requête HTTP vers l'API GW2 avec gestion du cache et des erreurs.

        Args:
            endpoint: Chemin de l'endpoint (sans le préfixe /v2/)
            params: Paramètres de requête
            use_cache: Si True, utilise le cache
            cache_ttl: Durée de vie du cache en secondes

        Returns:
            Les données JSON de la réponse

        Raises:
            HTTPException: En cas d'erreur lors de la requête
        """
        # Construction de l'URL complète
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        # Vérification du cache
        cache_key = f"gw2:{endpoint}:{str(params) if params else 'default'}"
        if use_cache:
            cached_data = await cache.get(cache_key)
            if cached_data is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_data

        # Configuration des paramètres de requête
        request_params = params or {}
        if "v" not in request_params and "ids" not in endpoint:  # Ne pas ajouter v=latest pour les requêtes par ID
            request_params["v"] = settings.GW2_API_SCHEMA_VERSION

        # Gestion des réessais
        last_error = None

        for attempt in range(self.retry_attempts):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    # Envoi de la requête
                    response = await client.get(url, params=request_params, headers=self.default_headers)

                    # Gestion des erreurs HTTP
                    if response.status_code == 200:
                        data = response.json()

                        # Mise en cache des données
                        if use_cache and data is not None:
                            await cache.set(cache_key, data, expire=cache_ttl)

                        return data

                    # Gestion des erreurs spécifiques
                    elif response.status_code == 404:
                        logger.warning(f"Ressource non trouvée: {url}")
                        return None

                    elif response.status_code == 429:  # Trop de requêtes
                        retry_after = int(response.headers.get("Retry-After", 5))
                        logger.warning(f"Rate limit atteint, nouvel essai dans {retry_after} secondes...")
                        await asyncio.sleep(retry_after)
                        continue

                    else:
                        response.raise_for_status()

            except httpx.HTTPStatusError as e:
                last_error = f"Erreur HTTP {e.response.status_code}: {e.response.text}"
                logger.error(last_error)
                if e.response.status_code in [401, 403, 404]:
                    break  # Pas besoin de réessayer pour ces erreurs

            except httpx.RequestError as e:
                last_error = f"Erreur de requête: {str(e)}"
                logger.error(last_error)

            except Exception as e:
                last_error = f"Erreur inattendue: {str(e)}"
                logger.error(last_error, exc_info=True)

            # Attente exponentielle avant de réessayer
            if attempt < self.retry_attempts - 1:
                wait_time = self.retry_delay * (2**attempt)
                logger.info(
                    f"Nouvel essai dans {wait_time} secondes... (tentative {attempt + 1}/{self.retry_attempts})"
                )
                await asyncio.sleep(wait_time)

        # Si on arrive ici, toutes les tentatives ont échoué
        error_msg = f"Échec après {self.retry_attempts} tentatives: {last_error}"
        logger.error(error_msg)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Impossible de joindre l'API Guild Wars 2: {last_error}",
        )

    # Méthodes pour les métiers

    async def fetch_professions(self) -> List[str]:
        """Récupère la liste des identifiants des métiers."""
        return await self._make_request("/v2/professions")

    async def fetch_profession_details(self, profession_id: str) -> Optional[GW2Profession]:
        """Récupère les détails d'un métier spécifique."""
        data = await self._make_request(f"/v2/professions/{profession_id}")
        return GW2Profession(**data) if data else None

    # Méthodes pour les compétences

    async def fetch_skills(self, skill_ids: List[int]) -> List[GW2Skill]:
        """Récupère les détails de plusieurs compétences."""
        if not skill_ids:
            return []

        # L'API GW2 a une limite de 200 IDs par requête
        chunk_size = 200
        all_skills = []

        for i in range(0, len(skill_ids), chunk_size):
            chunk = skill_ids[i : i + chunk_size]
            data = await self._make_request("/v2/skills", params={"ids": ",".join(map(str, chunk))})
            all_skills.extend([GW2Skill(**skill) for skill in data])

        return all_skills

    async def fetch_skill(self, skill_id: int) -> Optional[GW2Skill]:
        """Récupère les détails d'une compétence spécifique."""
        data = await self._make_request(f"/v2/skills/{skill_id}")
        return GW2Skill(**data) if data else None

    # Méthodes pour les caractéristiques

    async def fetch_traits(self, trait_ids: List[int]) -> List[GW2Trait]:
        """Récupère les détails de plusieurs caractéristiques."""
        if not trait_ids:
            return []

        chunk_size = 200
        all_traits = []

        for i in range(0, len(trait_ids), chunk_size):
            chunk = trait_ids[i : i + chunk_size]
            data = await self._make_request("/v2/traits", params={"ids": ",".join(map(str, chunk))})
            all_traits.extend([GW2Trait(**trait) for trait in data])

        return all_traits

    async def fetch_trait(self, trait_id: int) -> Optional[GW2Trait]:
        """Récupère les détails d'une caractéristique spécifique."""
        data = await self._make_request(f"/v2/traits/{trait_id}")
        return GW2Trait(**data) if data else None

    # Méthodes pour les spécialisations

    async def fetch_specializations(self, spec_ids: List[int] = None) -> List[GW2Specialization]:
        """Récupère les détails de plusieurs spécialisations."""
        if spec_ids is None:
            # Récupérer toutes les spécialisations
            spec_ids = await self._make_request("/v2/specializations")

        if not spec_ids:
            return []

        chunk_size = 200
        all_specs = []

        for i in range(0, len(spec_ids), chunk_size):
            chunk = spec_ids[i : i + chunk_size]
            data = await self._make_request("/v2/specializations", params={"ids": ",".join(map(str, chunk))})
            all_specs.extend([GW2Specialization(**spec) for spec in data])

        return all_specs

    async def fetch_specialization(self, spec_id: int) -> Optional[GW2Specialization]:
        """Récupère les détails d'une spécialisation spécifique."""
        data = await self._make_request(f"/v2/specializations/{spec_id}")
        return GW2Specialization(**data) if data else None

    # Méthodes de synchronisation

    async def sync_professions(self, db) -> List[GW2Profession]:
        """
        Synchronise les métiers GW2 avec la base de données.

        Returns:
            Liste des métiers synchronisés
        """
        from app.crud.crud_profession import profession as crud_profession

        # Récupérer les métiers depuis l'API
        profession_ids = await self.fetch_professions()
        professions = []

        for profession_id in profession_ids:
            try:
                # Récupérer les détails du métier
                profession_data = await self.fetch_profession_details(profession_id)
                if not profession_data:
                    continue

                # Convertir en modèle Pydantic
                profession = GW2Profession(**profession_data.dict())

                # Vérifier si le métier existe déjà
                db_profession = await crud_profession.get_by_name(db, name=profession.name)

                # Préparer les données pour la création/mise à jour
                profession_in = {
                    "name": profession.name,
                    "description": profession.description or "",
                    "icon_url": str(profession.icon) if profession.icon else None,
                    "is_active": True,
                    "data": profession.dict(),
                }

                if db_profession:
                    # Mettre à jour le métier existant
                    updated_profession = await crud_profession.update(db, db_obj=db_profession, obj_in=profession_in)
                    logger.info(f"Métier mis à jour: {updated_profession.name}")
                else:
                    # Créer un nouveau métier
                    updated_profession = await crud_profession.create(db, obj_in=profession_in)
                    logger.info(f"Nouveau métier ajouté: {updated_profession.name}")

                professions.append(updated_profession)

            except Exception as e:
                logger.error(f"Erreur lors de la synchronisation du métier {profession_id}: {str(e)}", exc_info=True)

        return professions
