from typing import Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import Role as RoleModel
from app.schemas.role import RoleCreate, RoleUpdate


class CRUDRole(CRUDBase[RoleModel, RoleCreate, RoleUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[RoleModel]:
        return db.query(RoleModel).filter(RoleModel.name == name).first()


role = CRUDRole(RoleModel)
