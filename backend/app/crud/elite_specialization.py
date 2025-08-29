from typing import Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.models import EliteSpecialization as EliteSpecModel
from app.schemas.profession import EliteSpecializationCreate, EliteSpecializationUpdate


class CRUDEliteSpecialization(CRUDBase[EliteSpecModel, EliteSpecializationCreate, EliteSpecializationUpdate]):
    def get_by_name_and_profession(self, db: Session, *, name: str, profession_id: int) -> Optional[EliteSpecModel]:
        return (
            db.query(EliteSpecModel)
            .filter(EliteSpecModel.name == name, EliteSpecModel.profession_id == profession_id)
            .first()
        )


elite_specialization = CRUDEliteSpecialization(EliteSpecModel)
