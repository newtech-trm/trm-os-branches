from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any, List

from trm_api.models.project import Project, ProjectCreate, ProjectUpdate
from trm_api.repositories.project_repository import ProjectRepository
from trm_api.models.relationships import Relationship

router = APIRouter()

# Dependency to get the repository instance
def get_project_repo() -> ProjectRepository:
    return ProjectRepository()

@router.get("/", response_model=List[Project])
def list_projects(
    skip: int = 0,
    limit: int = 100,
    repo: ProjectRepository = Depends(get_project_repo)
) -> Any:
    """
    Retrieve a list of projects.
    """
    projects = repo.list_projects(skip=skip, limit=limit)
    return projects

@router.post("/", response_model=Project, status_code=status.HTTP_201_CREATED)
def create_project(
    *, 
    project_in: ProjectCreate, 
    repo: ProjectRepository = Depends(get_project_repo)
) -> Any:
    """
    Create a new project.
    """
    try:
        graph_project = repo.create_project(project_data=project_in)
        return graph_project
    except Exception as e:
        print(f"AN ERROR OCCURRED: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred during project creation."
        )

@router.get("/{project_id}", response_model=Project)
def get_project(
    *, 
    project_id: str, 
    repo: ProjectRepository = Depends(get_project_repo)
) -> Any:
    """
    Get a specific project by its ID.
    """
    graph_project = repo.get_project_by_uid(uid=project_id)
    if not graph_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return graph_project

@router.put("/{project_id}", response_model=Project)
def update_project(
    *,
    project_id: str,
    project_in: ProjectUpdate,
    repo: ProjectRepository = Depends(get_project_repo)
) -> Any:
    """
    Update a project.
    """
    updated_project = repo.update_project(uid=project_id, project_data=project_in)
    if not updated_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return updated_project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    *,
    project_id: str,
    repo: ProjectRepository = Depends(get_project_repo)
) -> None:
    """
    Delete a project.
    """
    deleted = repo.delete_project(uid=project_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return None

# TODO: Refactor this relationship endpoint using the repository pattern.
# @router.post("/{project_id}/add-participant/{user_id}", response_model=Relationship, status_code=status.HTTP_201_CREATED)
# def add_participant_to_project(
#     *,
#     project_id: str,
#     user_id: str,
#     # service: ProjectService = Depends(get_project_service) # This needs to be replaced with a repository call
# ) -> Any:
#     """
#     Adds a User as a participant to a Project.
#     """
#     # relationship = service.add_participant_to_project(project_id=project_id, user_id=user_id)
#     # if relationship is None:
#     #     raise HTTPException(
#     #         status_code=status.HTTP_404_NOT_FOUND,
#     #         detail="Project or User not found, or relationship could not be created"
#     #     )
#     # return relationship
