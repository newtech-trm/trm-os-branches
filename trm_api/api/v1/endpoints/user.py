from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Any, List

from trm_api.models.pagination import PaginatedResponse

from trm_api.models.user import User, UserCreate, UserUpdate
from trm_api.repositories.user_repository import UserRepository

router = APIRouter()

# Dependency to get the repository instance
def get_user_repo() -> UserRepository:
    return UserRepository()

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(
    *, 
    user_in: UserCreate, 
    repo: UserRepository = Depends(get_user_repo)
) -> Any:
    """
    Create a new User.
    """
    # Check for existing user
    db_user = repo.get_user_by_email(email=user_in.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    graph_user = repo.create_user(user_data=user_in)
    return graph_user

@router.get("/{user_id}", response_model=User)
def get_user(
    *, 
    user_id: str, 
    repo: UserRepository = Depends(get_user_repo)
) -> Any:
    """
    Get a specific User by its ID.
    """
    graph_user = repo.get_user_by_uid(uid=user_id)
    if not graph_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return graph_user

@router.get("/", response_model=PaginatedResponse[User])
def list_users(
    page: int = Query(1, ge=1, description="Page number, 1-indexed"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    repo: UserRepository = Depends(get_user_repo)
) -> Any:
    """
    Retrieve a paginated list of Users.
    """
    users, total_count, page_count = repo.get_paginated_users(
        page=page,
        page_size=page_size
    )
    return PaginatedResponse.create(items=users, total_count=total_count, page=page, page_size=page_size)

@router.put("/{user_id}", response_model=User)
def update_user(
    *,
    user_id: str,
    user_in: UserUpdate,
    repo: UserRepository = Depends(get_user_repo)
) -> Any:
    """
    Update an existing User.
    """
    updated_user = repo.update_user(uid=user_id, user_data=user_in)
    if updated_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return updated_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    *,
    user_id: str,
    repo: UserRepository = Depends(get_user_repo)
) -> None:
    """
    Delete a User.
    """
    deleted = repo.delete_user(uid=user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return None
