from datetime import datetime, date
from pydantic import BaseModel, Field, ConfigDict, HttpUrl, model_validator
from typing import Optional, List, Dict
from enum import Enum


class GameMode(str, Enum):
    """Modes de jeu supportés par les professions."""

    WVW = "WvW"
    PVP = "PvP"
    PVE = "PvE"


class ProfessionBase(BaseModel):
    """Schéma de base pour les données de profession.

    Représente les informations essentielles d'une profession dans Guild Wars 2.
    """

    name: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Nom de la profession (ex: Gardien, Voleur, Élémentaliste)",
        examples=["Guardian"],
        json_schema_extra={"x-example": "Guardian"},
    )

    icon_url: Optional[HttpUrl] = Field(
        None,
        description="URL de l'icône représentant la profession",
        examples=["https://example.com/icons/guardian.png"],
        json_schema_extra={"x-example": "https://example.com/icons/guardian.png"},
    )

    background_url: Optional[HttpUrl] = Field(
        None,
        description="URL de l'image de fond de la profession",
        examples=["https://example.com/backgrounds/guardian.jpg"],
        json_schema_extra={"x-example": "https://example.com/backgrounds/guardian.jpg"},
    )

    description: Optional[str] = Field(
        None,
        description="Description détaillée de la profession et de ses mécaniques uniques",
        examples=[
            "Une profession qui utilise des pouvoirs magiques pour protéger ses alliés et combattre ses ennemis."
        ],
        json_schema_extra={
            "x-example": "Une profession qui utilise des pouvoirs magiques pour protéger ses alliés et combattre ses ennemis."
        },
    )

    game_modes: List[GameMode] = Field(
        default_factory=list,
        description="Modes de jeu dans lesquels cette profession est viable",
        examples=[["WvW", "PvP"]],
        json_schema_extra={"x-example": ["WvW", "PvP"]},
    )

    is_active: bool = Field(
        default=True,
        description="Indique si la profession est actuellement disponible dans le jeu",
        json_schema_extra={"x-example": True},
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "Guardian",
                    "icon_url": "https://example.com/icons/guardian.png",
                    "background_url": "https://example.com/backgrounds/guardian.jpg",
                    "description": "Une profession qui utilise des pouvoirs magiques pour protéger ses alliés et combattre ses ennemis.",
                    "game_modes": ["WvW", "PvP", "PvE"],
                    "is_active": True,
                }
            ]
        },
        use_enum_values=True,
        from_attributes=True,
    )


class ProfessionCreate(ProfessionBase):
    """Schéma pour la création d'une nouvelle profession.

    Hérite de tous les champs de ProfessionBase.
    """


class ProfessionUpdate(BaseModel):
    """Schéma pour la mise à jour des données d'une profession.

    Tous les champs sont optionnels pour permettre des mises à jour partielles.
    La validation est appliquée uniquement si les champs sont fournis.
    """

    name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=50,
        description="Nouveau nom de la profession (2-50 caractères)",
        examples=["Guardian"],
        json_schema_extra={"x-example": "Guardian"},
    )

    icon_url: Optional[HttpUrl] = Field(
        default=None,
        description="Nouvelle URL de l'icône de la profession (format URL valide)",
        examples=["https://example.com/icons/guardian_updated.png"],
        json_schema_extra={
            "x-example": "https://example.com/icons/guardian_updated.png"
        },
    )

    background_url: Optional[HttpUrl] = Field(
        default=None,
        description="Nouvelle URL de l'image de fond de la profession (format URL valide)",
        examples=["https://example.com/backgrounds/guardian_updated.jpg"],
        json_schema_extra={
            "x-example": "https://example.com/backgrounds/guardian_updated.jpg"
        },
    )

    description: Optional[str] = Field(
        default=None,
        description="Nouvelle description de la profession (max 2000 caractères)",
        max_length=2000,
        examples=[
            "Description mise à jour du Gardien avec plus de détails sur son gameplay."
        ],
        json_schema_extra={
            "x-example": "Description mise à jour du Gardien avec plus de détails sur son gameplay."
        },
    )

    game_modes: Optional[List[GameMode]] = Field(
        default=None,
        description="Nouvelle liste des modes de jeu supportés (doit être une liste non vide si fournie)",
        min_length=1,
        examples=[["WvW", "PvE"]],
        json_schema_extra={"x-example": ["WvW", "PvE"]},
    )

    is_active: Optional[bool] = Field(
        default=None,
        description="Nouvel état d'activation de la profession (true/false)",
        json_schema_extra={"x-example": True},
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                # Mise à jour partielle - uniquement le nom et la description
                {
                    "name": "Gardien",
                    "description": "Nouvelle description en français pour le Gardien.",
                },
                # Mise à jour complète
                {
                    "name": "Guardian",
                    "icon_url": "https://example.com/icons/guardian_updated.png",
                    "background_url": "https://example.com/backgrounds/guardian_updated.jpg",
                    "description": "Description mise à jour du Gardien avec plus de détails sur son gameplay.",
                    "game_modes": ["WvW", "PvE"],
                    "is_active": True,
                },
                # Désactivation de la profession
                {"is_active": False},
            ]
        },
        use_enum_values=True,
        from_attributes=True,
        validate_assignment=True,
    )

    @model_validator(mode="after")
    def validate_update_has_at_least_one_field(self) -> "ProfessionUpdate":
        """Valide qu'au moins un champ est fourni pour la mise à jour."""
        if all(field is None for field in self.model_dump(exclude_unset=True).values()):
            raise ValueError("Au moins un champ doit être fourni pour la mise à jour")
        return self


class ProfessionInDBBase(ProfessionBase):
    """Schéma de base pour les données de profession en base de données.

    Inclut l'identifiant, les horodatages de création/mise à jour,
    et les relations avec d'autres modèles.
    """

    id: int = Field(
        ...,
        examples=[1],
        description="Identifiant unique de la profession",
        json_schema_extra={"x-example": 1},
    )

    created_at: datetime = Field(
        ...,
        description="Date et heure de création de l'entrée en base de données (UTC)",
        examples=["2023-01-01T12:00:00Z"],
        json_schema_extra={"x-example": "2023-01-01T12:00:00Z"},
    )

    updated_at: Optional[datetime] = Field(
        None,
        description="Date et heure de la dernière mise à jour de l'entrée en base de données (UTC)",
        examples=["2023-01-02T15:30:00Z"],
        json_schema_extra={"x-example": "2023-01-02T15:30:00Z"},
    )

    # Relations
    elite_specializations: List["EliteSpecializationInDB"] = Field(
        default_factory=list,
        description="Liste des spécialisations d'élite disponibles pour cette profession",
    )

    elite_specialization_count: int = Field(
        0,
        description="Nombre de spécialisations d'élite disponibles pour cette profession",
        json_schema_extra={"x-example": 3},
    )

    builds_count: int = Field(
        0,
        description="Nombre de builds associés à cette profession",
        json_schema_extra={"x-example": 42},
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "name": "Guardian",
                    "icon_url": "https://example.com/icons/guardian.png",
                    "background_url": "https://example.com/backgrounds/guardian.jpg",
                    "description": "Une profession qui utilise des pouvoirs magiques pour protéger ses alliés.",
                    "game_modes": ["WvW", "PvP", "PvE"],
                    "is_active": True,
                    "created_at": "2023-01-01T00:00:00Z",
                    "updated_at": "2023-01-02T00:00:00Z",
                }
            ]
        },
        use_enum_values=True,
    )


class Profession(ProfessionInDBBase):
    """Schéma complet pour une profession, incluant les relations.

    Ce schéma est utilisé pour la lecture des données complètes d'une profession,
    y compris ses relations avec d'autres entités comme les spécialisations d'élite.
    """

    # Relations avec d'autres modèles
    elite_specializations: List["EliteSpecialization"] = Field(
        default_factory=list,
        description="Liste complète des spécialisations d'élite disponibles pour cette profession",
    )

    # Méthodes utilitaires
    def has_elite_specialization(self, spec_id: int) -> bool:
        """Vérifie si la profession a une spécialisation d'élite spécifique.

        Args:
            spec_id: L'identifiant de la spécialisation d'élite à vérifier

        Returns:
            bool: True si la spécialisation est trouvée, False sinon
        """
        return any(spec.id == spec_id for spec in self.elite_specializations)

    def get_elite_specialization_by_id(
        self, spec_id: int
    ) -> Optional["EliteSpecialization"]:
        """Récupère une spécialisation d'élite par son identifiant.

        Args:
            spec_id: L'identifiant de la spécialisation d'élite à récupérer

        Returns:
            Optional[EliteSpecialization]: La spécialisation d'élite si trouvée, None sinon
        """
        return next(
            (spec for spec in self.elite_specializations if spec.id == spec_id), None
        )

    def get_active_elite_specializations(self) -> List["EliteSpecialization"]:
        """Récupère la liste des spécialisations d'élite actives.

        Returns:
            List[EliteSpecialization]: Liste des spécialisations d'élite actives
        """
        return [spec for spec in self.elite_specializations if spec.is_active]

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "name": "Guardian",
                    "icon_url": "https://example.com/icons/guardian.png",
                    "background_url": "https://example.com/backgrounds/guardian.jpg",
                    "description": "Une profession qui utilise des pouvoirs magiques pour protéger ses alliés et combattre ses ennemis.",
                    "game_modes": ["WvW", "PvP", "PvE"],
                    "is_active": True,
                    "created_at": "2023-01-01T12:00:00Z",
                    "updated_at": "2023-01-02T15:30:00Z",
                    "elite_specialization_count": 3,
                    "builds_count": 42,
                    "elite_specializations": [
                        {
                            "id": 1,
                            "name": "Dragonhunter",
                            "icon_url": "https://example.com/icons/dragonhunter.png",
                            "description": "Spécialisation d'élite du Gardien qui se concentre sur les pièges et les compétences à distance.",
                            "is_active": True,
                            "background_url": "https://example.com/backgrounds/dragonhunter.jpg",
                            "weapon_type": "Longbow",
                        },
                        {
                            "id": 2,
                            "name": "Firebrand",
                            "icon_url": "https://example.com/icons/firebrand.png",
                            "description": "Spécialisation d'élite du Gardien qui utilise des livres sacrés pour invoquer des sorts puissants.",
                            "is_active": True,
                            "background_url": "https://example.com/backgrounds/firebrand.jpg",
                            "weapon_type": "Axe",
                        },
                        {
                            "id": 3,
                            "name": "Willbender",
                            "icon_url": "https://example.com/icons/willbender.png",
                            "description": "Spécialisation d'élite du Gardien axée sur la mobilité et les attaques rapides.",
                            "is_active": True,
                            "background_url": "https://example.com/backgrounds/willbender.jpg",
                            "weapon_type": "Épée",
                        },
                    ],
                }
            ]
        },
    )


class ProfessionInDB(ProfessionInDBBase):
    """Schéma pour les données complètes d'une profession en base de données.

    Inclut toutes les relations et champs sensibles.
    """

    pass


class EliteSpecializationBase(BaseModel):
    """Schéma de base pour les données de spécialisation d'élite.

    Représente les informations essentielles d'une spécialisation d'élite dans Guild Wars 2.
    Une spécialisation d'élite est une version avancée d'une profession de base,
    apportant de nouvelles compétences, mécaniques et armes.
    """

    name: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Nom de la spécialisation d'élite (ex: Firebrand, Dragonhunter, Willbender)",
        examples=["Firebrand"],
        json_schema_extra={"x-example": "Firebrand"},
    )

    profession_id: int = Field(
        ...,
        description="Identifiant de la profession parente à laquelle cette spécialisation appartient",
        examples=[1],
        json_schema_extra={"x-example": 1},
        gt=0,  # L'ID doit être supérieur à 0
    )

    icon_url: Optional[HttpUrl] = Field(
        None,
        description="URL de l'icône représentant la spécialisation d'élite",
        examples=["https://example.com/icons/firebrand.png"],
        json_schema_extra={"x-example": "https://example.com/icons/firebrand.png"},
    )

    background_url: Optional[HttpUrl] = Field(
        None,
        description="URL de l'image de fond de la spécialisation",
        examples=["https://example.com/backgrounds/firebrand.jpg"],
        json_schema_extra={
            "x-example": "https://example.com/backgrounds/firebrand.jpg"
        },
    )

    weapon_type: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Type d'arme principale ajoutée par cette spécialisation (ex: 'Axe', 'Longbow', 'Pistol')",
        examples=["Axe"],
        json_schema_extra={"x-example": "Axe"},
    )

    secondary_weapon_types: List[str] = Field(
        default_factory=list,
        description="Liste des types d'armes secondaires ajoutées par cette spécialisation",
        examples=[["Mace", "Sword"]],
        json_schema_extra={"x-example": ["Mace", "Sword"]},
    )

    description: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Description détaillée de la spécialisation, ses mécaniques uniques et son style de jeu",
        examples=[
            "Spécialisation d'élite maniant le grimoire et axée sur le support et les dégâts de condition."
        ],
        json_schema_extra={
            "x-example": "Spécialisation d'élite maniant le grimoire et axée sur le support et les dégâts de condition."
        },
    )

    is_active: bool = Field(
        default=True,
        description="Indique si la spécialisation est actuellement disponible dans le jeu",
        json_schema_extra={"x-example": True},
    )

    release_date: Optional[date] = Field(
        None,
        description="Date de sortie de la spécialisation dans le jeu",
        examples=["2017-09-22"],
        json_schema_extra={"x-example": "2017-09-22"},
    )

    game_mode_affinity: Dict[GameMode, float] = Field(
        default_factory=dict,
        description="Affinité de la spécialisation avec chaque mode de jeu (0-1)",
        examples=[{"WvW": 0.9, "PvP": 0.8, "PvE": 0.7}],
        json_schema_extra={"x-example": {"WvW": 0.9, "PvP": 0.8, "PvE": 0.7}},
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "Firebrand",
                    "profession_id": 1,
                    "icon_url": "https://example.com/icons/firebrand.png",
                    "background_url": "https://example.com/backgrounds/firebrand.jpg",
                    "weapon_type": "Axe",
                    "description": "Spécialisation d'élite maniant le grimoire et axée sur le support et les dégâts de condition.",
                    "is_active": True,
                }
            ]
        },
        use_enum_values=True,
    )


class EliteSpecializationCreate(EliteSpecializationBase):
    """Schéma pour la création d'une nouvelle spécialisation d'élite.

    Hérite de tous les champs de EliteSpecializationBase.
    """

    pass


class EliteSpecializationUpdate(BaseModel):
    """Schéma pour la mise à jour des données d'une spécialisation d'élite.

    Tous les champs sont optionnels pour permettre des mises à jour partielles.
    La validation est appliquée uniquement si les champs sont fournis.
    """

    name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=50,
        description="Nouveau nom de la spécialisation d'élite (2-50 caractères)",
        examples=["Firebrand"],
        json_schema_extra={"x-example": "Firebrand"},
    )

    profession_id: Optional[int] = Field(
        default=None,
        description="Nouvel identifiant de la profession parente (doit être > 0)",
        examples=[1],
        json_schema_extra={"x-example": 1},
        gt=0,
    )

    icon_url: Optional[HttpUrl] = Field(
        default=None,
        description="Nouvelle URL de l'icône de la spécialisation (format URL valide)",
        examples=["https://example.com/icons/firebrand_updated.png"],
        json_schema_extra={
            "x-example": "https://example.com/icons/firebrand_updated.png"
        },
    )

    background_url: Optional[HttpUrl] = Field(
        default=None,
        description="Nouvelle URL de l'image de fond de la spécialisation (format URL valide)",
        examples=["https://example.com/backgrounds/firebrand_updated.jpg"],
        json_schema_extra={
            "x-example": "https://example.com/backgrounds/firebrand_updated.jpg"
        },
    )

    weapon_type: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=50,
        description="Nouveau type d'arme principale (ex: 'Axe', 'Longbow', 'Pistol')",
        examples=["Axe"],
        json_schema_extra={"x-example": "Axe"},
    )

    secondary_weapon_types: Optional[List[str]] = Field(
        default=None,
        description="Nouvelle liste des types d'armes secondaires",
        examples=[["Mace", "Sword"]],
        json_schema_extra={"x-example": ["Mace", "Sword"]},
    )

    description: Optional[str] = Field(
        default=None,
        min_length=10,
        max_length=2000,
        description="Nouvelle description de la spécialisation (10-2000 caractères)",
        examples=["Nouvelle description mise à jour de la spécialisation Firebrand."],
        json_schema_extra={
            "x-example": "Nouvelle description mise à jour de la spécialisation Firebrand."
        },
    )

    is_active: Optional[bool] = Field(
        default=None,
        description="Nouvel état d'activation de la spécialisation",
        json_schema_extra={"x-example": True},
    )

    release_date: Optional[date] = Field(
        default=None,
        description="Nouvelle date de sortie de la spécialisation (format YYYY-MM-DD)",
        examples=["2017-09-22"],
        json_schema_extra={"x-example": "2017-09-22"},
    )

    game_mode_affinity: Optional[Dict[GameMode, float]] = Field(
        default=None,
        description="Nouvelles affinités avec les modes de jeu (0-1)",
        examples=[{"WvW": 0.9, "PvP": 0.8, "PvE": 0.7}],
        json_schema_extra={"x-example": {"WvW": 0.9, "PvP": 0.8, "PvE": 0.7}},
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                # Mise à jour partielle - uniquement le nom et la description
                {
                    "name": "Firebrand",
                    "description": "Nouvelle description mise à jour de la spécialisation Firebrand.",
                },
                # Mise à jour complète
                {
                    "name": "Firebrand",
                    "profession_id": 1,
                    "icon_url": "https://example.com/icons/firebrand_updated.png",
                    "background_url": "https://example.com/backgrounds/firebrand_updated.jpg",
                    "weapon_type": "Axe",
                    "secondary_weapon_types": ["Mace", "Sword"],
                    "description": "Description mise à jour de la spécialisation Firebrand.",
                    "is_active": True,
                    "release_date": "2017-09-22",
                    "game_mode_affinity": {"WvW": 0.9, "PvP": 0.8, "PvE": 0.7},
                },
                # Désactivation de la spécialisation
                {"is_active": False},
            ]
        },
        use_enum_values=True,
        from_attributes=True,
        validate_assignment=True,
    )

    @model_validator(mode="after")
    def validate_update_has_at_least_one_field(self) -> "EliteSpecializationUpdate":
        """Valide qu'au moins un champ est fourni pour la mise à jour."""
        if all(field is None for field in self.model_dump(exclude_unset=True).values()):
            raise ValueError("Au moins un champ doit être fourni pour la mise à jour")
        return self


class EliteSpecializationInDBBase(EliteSpecializationBase):
    """Schéma de base pour les données de spécialisation d'élite en base de données.

    Inclut l'identifiant, les horodatages de création/mise à jour,
    et les relations avec d'autres modèles.
    """

    id: int = Field(
        ...,
        examples=[1],
        description="Identifiant unique de la spécialisation d'élite",
        json_schema_extra={"x-example": 1},
        gt=0,  # L'ID doit être supérieur à 0
    )

    created_at: datetime = Field(
        ...,
        description="Date et heure de création de l'entrée en base de données (UTC)",
        examples=["2023-01-01T12:00:00Z"],
        json_schema_extra={"x-example": "2023-01-01T12:00:00Z"},
    )

    updated_at: Optional[datetime] = Field(
        None,
        description="Date et heure de la dernière mise à jour de l'entrée en base de données (UTC)",
        examples=["2023-01-02T15:30:00Z"],
        json_schema_extra={"x-example": "2023-01-02T15:30:00Z"},
    )

    # Relations
    builds_count: int = Field(
        0,
        description="Nombre de builds associés à cette spécialisation d'élite",
        json_schema_extra={"x-example": 27},
    )

    profession_name: Optional[str] = Field(
        None,
        description="Nom de la profession parente (peut être utilisé pour l'affichage)",
        examples=["Guardian"],
        json_schema_extra={"x-example": "Guardian"},
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "name": "Firebrand",
                    "profession_id": 1,
                    "profession_name": "Guardian",
                    "icon_url": "https://example.com/icons/firebrand.png",
                    "background_url": "https://example.com/backgrounds/firebrand.jpg",
                    "weapon_type": "Axe",
                    "secondary_weapon_types": ["Mace", "Sword"],
                    "description": "Spécialisation d'élite maniant le grimoire et axée sur le support et les dégâts de condition.",
                    "is_active": True,
                    "release_date": "2017-09-22",
                    "game_mode_affinity": {"WvW": 0.9, "PvP": 0.8, "PvE": 0.7},
                    "created_at": "2023-01-01T12:00:00Z",
                    "updated_at": "2023-01-02T15:30:00Z",
                    "builds_count": 27,
                }
            ]
        },
        use_enum_values=True,
        validate_assignment=True,
    )

    @model_validator(mode="after")
    def set_profession_name_if_missing(self) -> "EliteSpecializationInDBBase":
        """Définit le nom de la profession si non fourni."""
        if (
            hasattr(self, "profession")
            and self.profession
            and not hasattr(self, "profession_name")
        ):
            self.profession_name = self.profession.name
        return self


class EliteSpecialization(EliteSpecializationInDBBase):
    """Schéma complet pour une spécialisation d'élite, incluant les relations.

    Ce schéma est utilisé pour la lecture des données complètes d'une spécialisation d'élite,
    y compris ses relations avec d'autres entités comme la profession parente.
    """

    profession: Optional["Profession"] = Field(
        None,
        description="Détails complets de la profession parente à laquelle cette spécialisation appartient",
    )

    # Méthodes utilitaires
    def get_weapon_types(self) -> List[str]:
        """Retourne la liste de tous les types d'armes de la spécialisation.

        Returns:
            List[str]: Liste des types d'armes (arme principale + armes secondaires)
        """
        weapons = [self.weapon_type] if self.weapon_type else []
        if hasattr(self, "secondary_weapon_types") and self.secondary_weapon_types:
            weapons.extend(self.secondary_weapon_types)
        return list(
            dict.fromkeys(weapons)
        )  # Supprime les doublons tout en préservant l'ordre

    def get_game_mode_affinity(self, game_mode: GameMode) -> float:
        """Récupère l'affinité de la spécialisation pour un mode de jeu donné.

        Args:
            game_mode: Le mode de jeu pour lequel récupérer l'affinité

        Returns:
            float: La valeur d'affinité (entre 0 et 1) ou 0.5 par défaut si non spécifiée
        """
        if hasattr(self, "game_mode_affinity") and self.game_mode_affinity:
            return self.game_mode_affinity.get(game_mode, 0.5)
        return 0.5

    def is_viable_for_game_mode(
        self, game_mode: GameMode, threshold: float = 0.5
    ) -> bool:
        """Vérifie si la spécialisation est viable pour un mode de jeu donné.

        Args:
            game_mode: Le mode de jeu à vérifier
            threshold: Le seuil minimum d'affinité pour considérer la spécialisation comme viable

        Returns:
            bool: True si la spécialisation est viable, False sinon
        """
        return self.get_game_mode_affinity(game_mode) >= threshold

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "name": "Firebrand",
                    "profession_id": 1,
                    "profession": {
                        "id": 1,
                        "name": "Guardian",
                        "icon_url": "https://example.com/icons/guardian.png",
                        "is_active": True,
                    },
                    "icon_url": "https://example.com/icons/firebrand.png",
                    "background_url": "https://example.com/backgrounds/firebrand.jpg",
                    "weapon_type": "Axe",
                    "secondary_weapon_types": ["Mace", "Sword"],
                    "description": "Spécialisation d'élite maniant le grimoire et axée sur le support et les dégâts de condition.",
                    "is_active": True,
                    "release_date": "2017-09-22",
                    "game_mode_affinity": {"WvW": 0.9, "PvP": 0.8, "PvE": 0.7},
                    "created_at": "2023-01-01T12:00:00Z",
                    "updated_at": "2023-01-02T15:30:00Z",
                    "builds_count": 27,
                    "profession_name": "Guardian",
                }
            ]
        },
        use_enum_values=True,
        validate_assignment=True,
    )


class EliteSpecializationInDB(EliteSpecializationInDBBase):
    """Schéma pour les données complètes d'une spécialisation d'élite en base de données.

    Inclut toutes les relations et champs sensibles.
    """

    pass
