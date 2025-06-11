from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any, List

from trm_api.models.tension import Tension, TensionCreate, TensionUpdate
from trm_api.models.relationships import Relationship
from trm_api.services.tension_service import tension_service, TensionService

router = APIRouter()

def get_tension_service() -> TensionService:
    return tension_service

@router.get("/", response_model=List[Tension])
def list_tensions_for_project(
    *, 
    project_id: str,
    skip: int = 0,
    limit: int = 100,
    service: TensionService = Depends(get_tension_service)
) -> Any:
    """
    Retrieve tensions for a specific project.
    """
    # Here you might want to add a check to see if the project exists first
    # but for now, we'll rely on the query returning an empty list if no match.
    tensions = service.list_tensions_for_project(project_id=project_id, skip=skip, limit=limit)
    return tensions

@router.get("/{tension_id}", response_model=Tension)
def get_tension(
    *, 
    tension_id: str,
    service: TensionService = Depends(get_tension_service)
) -> Any:
    """
    Get tension by ID.
    """
    tension = service.get_tension_by_id(tension_id=tension_id)
    if not tension:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Tension not found"
        )
    return tension

@router.put("/{tension_id}", response_model=Tension)
def update_tension(
    *, 
    tension_id: str,
    tension_in: TensionUpdate,
    service: TensionService = Depends(get_tension_service)
) -> Any:
    """
    Update a tension.
    """
    tension = service.get_tension_by_id(tension_id=tension_id)
    if not tension:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Tension not found"
        )
    updated_tension = service.update_tension(tension_id=tension_id, tension_update=tension_in)
    return updated_tension

@router.delete("/{tension_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tension(
    *, 
    tension_id: str,
    service: TensionService = Depends(get_tension_service)
) -> None:
    """
    Delete a tension.
    """
    tension = service.get_tension_by_id(tension_id=tension_id)
    if not tension:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Tension not found"
        )
    service.delete_tension(tension_id=tension_id)
    return None

@router.post("/", response_model=Tension, status_code=status.HTTP_201_CREATED)
def create_tension(
    *, 
    tension_in: TensionCreate,
    service: TensionService = Depends(get_tension_service)
) -> Any:
    """
    Create new tension for a project.
    """
    created_tension = service.create_tension_for_project(tension_create=tension_in)
    if not created_tension:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {tension_in.project_id} not found."
        )
    return created_tension


@router.post("/{tension_id}/identified-by/{user_id}", response_model=Relationship, status_code=status.HTTP_201_CREATED)
def identify_tension_by_user(
    *,
    tension_id: str,
    user_id: str,
    service: TensionService = Depends(get_tension_service)
) -> Any:
    """
    Creates an IDENTIFIED relationship from a User to a Tension.
    """
    relationship = service.identify_tension_by_user(tension_id=tension_id, user_id=user_id)
    if relationship is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tension or User not found, or relationship could not be created"
        )
    return relationship
