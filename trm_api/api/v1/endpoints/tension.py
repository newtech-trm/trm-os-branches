from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any, List

from trm_api.models.tension import Tension, TensionCreate, TensionUpdate
from trm_api.models.relationships import Relationship
from trm_api.repositories.tension_repository import TensionRepository

router = APIRouter()

def get_tension_repo() -> TensionRepository:
    return TensionRepository()

@router.get("/", response_model=List[Tension])
def list_tensions_for_project(
    *, 
    project_id: str,
    skip: int = 0,
    limit: int = 100,
    repo: TensionRepository = Depends(get_tension_repo)
) -> Any:
    """
    Retrieve tensions for a specific project.
    """
    tensions = repo.list_tensions_for_project(project_id=project_id, skip=skip, limit=limit)
    return tensions

@router.post("/", response_model=Tension, status_code=status.HTTP_201_CREATED)
def create_tension(
    *, 
    tension_in: TensionCreate, 
    repo: TensionRepository = Depends(get_tension_repo)
) -> Any:
    """
    Create new tension for a project.
    """
    created_tension = repo.create_tension(tension_data=tension_in)
    if not created_tension:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not create tension. Project with ID {tension_in.project_id} not found."
        )
    return created_tension

@router.get("/{tension_id}", response_model=Tension)
def get_tension(
    *, 
    tension_id: str, 
    repo: TensionRepository = Depends(get_tension_repo)
) -> Any:
    """
    Get tension by ID.
    """
    tension = repo.get_tension_by_uid(uid=tension_id)
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
    repo: TensionRepository = Depends(get_tension_repo)
) -> Any:
    """
    Update a tension.
    """
    updated_tension = repo.update_tension(uid=tension_id, tension_data=tension_in)
    if not updated_tension:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Tension not found"
        )
    return updated_tension

@router.delete("/{tension_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tension(
    *, 
    tension_id: str,
    repo: TensionRepository = Depends(get_tension_repo)
) -> None:
    """
    Delete a tension.
    """
    deleted = repo.delete_tension(uid=tension_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tension not found"
        )
    return None

# Relationship endpoints for RESOLVES_TENSION
@router.post("/{tension_id}/resolved-by/{project_id}", response_model=dict, status_code=status.HTTP_201_CREATED)
def connect_project_to_tension(
    *,
    tension_id: str,
    project_id: str,
    repo: TensionRepository = Depends(get_tension_repo)
) -> Any:
    """
    Establish a RESOLVES_TENSION relationship from a Project to a Tension.
    This indicates that the Project was created to resolve the specified Tension.
    """
    result = repo.connect_tension_to_project(tension_uid=tension_id, project_uid=project_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tension or Project not found"
        )
    
    tension, project = result
    return {
        "message": f"Project '{project.title}' is now resolving Tension '{tension.title}'",
        "tension_id": tension.uid,
        "project_id": project.uid,
        "relationship": "RESOLVES_TENSION"
    }

@router.get("/{tension_id}/resolved-by", response_model=List[dict], status_code=status.HTTP_200_OK)
def get_projects_resolving_tension(
    *,
    tension_id: str,
    skip: int = 0,
    limit: int = 100,
    repo: TensionRepository = Depends(get_tension_repo)
) -> Any:
    """
    Get all Projects that are resolving a specific Tension.
    """
    tension = repo.get_tension_by_uid(uid=tension_id)
    if not tension:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tension not found"
        )
    
    projects = repo.get_projects_resolving_tension(tension_uid=tension_id, skip=skip, limit=limit)
    return [
        {
            "project_id": project.uid,
            "title": project.title,
            "description": project.description,
            "status": project.status
        }
        for project in projects
    ]

@router.delete("/{tension_id}/resolved-by/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def disconnect_project_from_tension(
    *,
    tension_id: str,
    project_id: str,
    repo: TensionRepository = Depends(get_tension_repo)
) -> None:
    """
    Remove the RESOLVES_TENSION relationship between a Project and a Tension.
    """
    success = repo.disconnect_project_from_tension(tension_uid=tension_id, project_uid=project_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tension or Project not found, or no relationship exists between them"
        )
    return None

# TODO: Refactor this relationship endpoint using the repository pattern.
# @router.post("/{tension_id}/identified-by/{user_id}", response_model=Relationship, status_code=status.HTTP_201_CREATED)
# def identify_tension_by_user(
#     *,
#     tension_id: str,
#     user_id: str,
#     # service: TensionService = Depends(get_tension_service) # This needs to be replaced with a repository call
# ) -> Any:
#     """
#     Creates an IDENTIFIED relationship from a User to a Tension.
#     """
#     # relationship = service.identify_tension_by_user(tension_id=tension_id, user_id=user_id)
#     # if relationship is None:
#     #     raise HTTPException(
#     #         status_code=status.HTTP_404_NOT_FOUND,
#     #         detail="Tension or User not found, or relationship could not be created"
#     #     )
#     # return relationship
