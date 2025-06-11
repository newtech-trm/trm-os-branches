from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from trm_api.models.user import User, UserCreate, UserUpdate
from trm_api.services.user_service import user_service, UserService

router = APIRouter()

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserCreate,
    service: UserService = Depends(lambda: user_service)
):
    """
    Create a new User.
    """
    # In a real application, you might want to check for existing email
    db_user = service.get_user_by_email(email=user_in.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    return service.create_user(user_create=user_in)

@router.get("/{user_id}", response_model=User)
def get_user(
    user_id: str,
    service: UserService = Depends(lambda: user_service)
):
    """
    Get a specific User by its ID.
    """
    db_user = service.get_user_by_id(user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user

@router.get("/", response_model=List[User])
def list_users(
    skip: int = 0,
    limit: int = 100,
    service: UserService = Depends(lambda: user_service)
):
    """
    Retrieve a list of Users.
    """
    return service.list_users(skip=skip, limit=limit)

@router.put("/{user_id}", response_model=User)
def update_user(
    user_id: str,
    user_in: UserUpdate,
    service: UserService = Depends(lambda: user_service)
):
    """
    Update an existing User.
    """
    updated_user = service.update_user(user_id=user_id, user_update=user_in)
    if updated_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return updated_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,
    service: UserService = Depends(lambda: user_service)
):
    """
    Delete a User.
    """
    deleted = service.delete_user(user_id=user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return
