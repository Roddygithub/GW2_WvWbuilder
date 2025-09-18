from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.config import settings
from app.core.security import get_current_active_user

router = APIRouter()

@router.get("/", response_model=List[schemas.User])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve users.
    """
    users = crud.user.get_multi(db, skip=skip, limit=limit)
    return users

@router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new user.
    """
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user = crud.user.create(db, obj_in=user_in)
    return user

@router.put("/me", response_model=schemas.User)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update own user.
    """
    # Update the user and commit the transaction
    user = crud.user.update(db, db_obj=current_user, obj_in=user_in, commit=True)
    return user

@router.get("/me", response_model=schemas.User)
def read_user_me(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.get("/{user_id}", response_model=schemas.User)
def read_user_by_id(
    user_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific user by id.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 50)
    logger.info(f"read_user_by_id called with user_id={user_id}")
    
    # Debug current user
    if current_user is None:
        logger.error("Current user is None! This should not happen with get_current_active_user")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    logger.info(f"Current user: id={current_user.id if current_user else 'None'}, "
                f"email={getattr(current_user, 'email', 'No email')}, "
                f"is_superuser={getattr(current_user, 'is_superuser', False)}")
    
    # Get the requested user
    user = crud.user.get(db, id=user_id)
    if not user:
        logger.warning(f"User with id {user_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
        
    logger.info(f"Found requested user: id={user.id}, "
                f"email={user.email}, "
                f"is_superuser={getattr(user, 'is_superuser', False)}")
    
    # Debug information
    logger.info("-" * 50)
    logger.info("Debug Information:")
    logger.info(f"User IDs - Requested: {user.id}, Current: {current_user.id}")
    logger.info(f"User emails - Requested: {user.email}, Current: {current_user.email}")
    logger.info(f"User types - Requested: {type(user)}, Current: {type(current_user)}")
    logger.info(f"User comparison: user == current_user -> {user == current_user}")
    logger.info(f"Is superuser: {crud.user.is_superuser(current_user)}")
    logger.info("-" * 50)
    
    # Check permissions
    is_user_superuser = getattr(current_user, "is_superuser", False)
    logger.info(f"User is superuser: {is_user_superuser}")
    
    if user.id == current_user.id or is_user_superuser:
        logger.info("Access granted")
        return user
        
    logger.warning("Access denied - insufficient privileges")
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, 
        detail="The user doesn't have enough privileges"
    )

@router.put("/{user_id}", response_model=schemas.User)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a user.
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this ID does not exist in the system",
        )
    
    try:
        user = crud.user.update(db, db_obj=user, obj_in=user_in, commit=True)
        return user
    except ValueError as e:
        if "Email already registered" in str(e):
            raise HTTPException(
                status_code=400,
                detail="The email is already registered to another user"
            )
        raise  # Re-raise other ValueErrors

@router.post("/{user_id}/roles/{role_id}", response_model=schemas.User)
def add_role_to_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    role_id: int,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Add a role to a user.
    """
    # Vérifier si l'utilisateur existe
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Vérifier si le rôle existe
    role = crud.role.get(db, id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Vérifier si l'utilisateur a déjà ce rôle
    if role in user.roles:
        return user
    
    # Ajouter le rôle à l'utilisateur
    user.roles.append(role)
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user

@router.delete("/{user_id}/roles/{role_id}", response_model=schemas.User)
def remove_role_from_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    role_id: int,
    current_user: models.User = Depends(get_current_active_user),
) -> Any:
    """
    Remove a role from a user.
    """
    # Vérifier si l'utilisateur existe
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Vérifier si le rôle existe
    role = crud.role.get(db, id=role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Vérifier si l'utilisateur a ce rôle
    if role not in user.roles:
        return user
    
    # Retirer le rôle de l'utilisateur
    user.roles.remove(role)
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user
