from typing import Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.models import Profession as ProfessionModel
from app.schemas.profession import ProfessionCreate, ProfessionUpdate


class CRUDProfession(CRUDBase[ProfessionModel, ProfessionCreate, ProfessionUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[ProfessionModel]:
        return db.query(ProfessionModel).filter(ProfessionModel.name == name).first()


profession = CRUDProfession(ProfessionModel)
