from typing import Optional, Dict, Any

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.models import User as UserModel
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[UserModel, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[UserModel]:
        return db.query(UserModel).filter(UserModel.email == email).first()

    def is_superuser(self, user: UserModel) -> bool:
        return bool(getattr(user, "is_superuser", False))

    def create(self, db: Session, *, obj_in: UserCreate | Dict[str, Any]) -> UserModel:
        if isinstance(obj_in, UserCreate):
            data = obj_in.model_dump(exclude_unset=True)
        else:
            data = obj_in
        # Map plain password to hashed_password (no-op hashing for tests)
        pwd = data.pop("password", None)
        if pwd is not None:
            data["hashed_password"] = pwd if isinstance(pwd, str) else str(pwd)
        db_obj = UserModel(**data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


user = CRUDUser(UserModel)
