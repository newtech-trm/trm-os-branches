from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any, List

from trm_api.models.project import Project, ProjectCreate, ProjectUpdate
from trm_api.models.relationships import Relationship
from trm_api.services.project_service import project_service, ProjectService

router = APIRouter()

# Dependency to get the service instance
def get_project_service() -> ProjectService:
    return project_service

@router.get("/", response_model=List[Project])
def list_projects(
    skip: int = 0,
    limit: int = 100,
    service: ProjectService = Depends(get_project_service)
) -> Any:
    """
    Retrieve projects.
    """
    projects = service.list_projects(skip=skip, limit=limit)
    return projects

@router.get("/{project_id}", response_model=Project)
def get_project(
    *, 
    project_id: str,
    service: ProjectService = Depends(get_project_service)
) -> Any:
    """
    Get project by ID.
    """
    project = service.get_project_by_id(project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return project

@router.put("/{project_id}", response_model=Project)
def update_project(
    *, 
    project_id: str,
    project_in: ProjectUpdate,
    service: ProjectService = Depends(get_project_service)
) -> Any:
    """
    Update a project.
    """
    project = service.get_project_by_id(project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    updated_project = service.update_project(project_id=project_id, project_update=project_in)
    return updated_project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    *, 
    project_id: str,
    service: ProjectService = Depends(get_project_service)
) -> None:
    """
    Delete a project.
    """
    project = service.get_project_by_id(project_id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    service.delete_project(project_id=project_id)
    return None # No content to return

@router.post("/", response_model=Project, status_code=status.HTTP_201_CREATED)
def create_project(
    *, 
    project_in: ProjectCreate,
    service: ProjectService = Depends(get_project_service)
) -> Any:
    """
    Create new project.
    """
    try:
        created_project = service.create_project(project_create=project_in)
        return created_project
    except Exception as e:
        # In a real app, you'd have more specific error handling
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {e}"
        )


@router.post("/{project_id}/add-participant/{user_id}", response_model=Relationship, status_code=status.HTTP_201_CREATED)
def add_participant_to_project(
    *,
    project_id: str,
    user_id: str,
    service: ProjectService = Depends(get_project_service)
) -> Any:
    """
    Adds a User as a participant to a Project.
    """
    relationship = service.add_participant_to_project(project_id=project_id, user_id=user_id)
    if relationship is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project or User not found, or relationship could not be created"
        )
    return relationship
