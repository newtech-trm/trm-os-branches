from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional

from trm_api.models.resource import (
    Resource, ResourceCreate, ResourceUpdate, ResourceType,
    FinancialResourceCreate, KnowledgeResourceCreate,
    HumanResourceCreate, ToolResourceCreate, EquipmentResourceCreate,
    SpaceResourceCreate
)
from trm_api.models.relationships import Relationship
from trm_api.repositories.resource_repository import ResourceRepository

router = APIRouter()

def get_resource_repository() -> ResourceRepository:
    return ResourceRepository()

# --- Basic Resource CRUD Endpoints ---

@router.post("/", response_model=Resource, status_code=status.HTTP_201_CREATED)
def create_resource(
    resource: ResourceCreate,
    repo: ResourceRepository = Depends(get_resource_repository)
):
    """
    Create a new generic Resource.
    """
    db_resource = repo.create_typed_resource(resource_data=resource)
    return db_resource

@router.get("/", response_model=List[Resource])
def list_resources(
    skip: int = 0,
    limit: int = 100,
    resource_type: Optional[ResourceType] = None,
    repo: ResourceRepository = Depends(get_resource_repository)
):
    """
    Retrieve a list of resources with optional type filtering.
    """
    resources = repo.list_resources(
        skip=skip, 
        limit=limit, 
        resource_type=resource_type.value if resource_type else None
    )
    return resources

@router.get("/{uid}", response_model=Resource)
def get_resource(
    uid: str,
    repo: ResourceRepository = Depends(get_resource_repository)
):
    """
    Get a specific resource by its UID.
    """
    resource = repo.get_resource_by_uid(uid)
    if not resource:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
    return resource

@router.put("/{uid}", response_model=Resource)
def update_resource(
    uid: str,
    resource_update: ResourceUpdate,
    repo: ResourceRepository = Depends(get_resource_repository)
):
    """
    Update a resource's details.
    """
    update_data = resource_update.model_dump(exclude_unset=True)
    updated_resource = repo.update_resource(uid=uid, update_data=update_data)
    if not updated_resource:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
    return updated_resource

@router.delete("/{uid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resource(
    uid: str,
    repo: ResourceRepository = Depends(get_resource_repository)
):
    """
    Delete a resource.
    """
    success = repo.delete_resource(uid)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
    return

# --- Type-specific Resource Creation Endpoints ---

@router.post("/financial", response_model=Resource, status_code=status.HTTP_201_CREATED)
def create_financial_resource(
    resource: FinancialResourceCreate,
    repo: ResourceRepository = Depends(get_resource_repository)
):
    """
    Create a new Financial Resource.
    """
    db_resource = repo.create_typed_resource(resource_data=resource)
    return db_resource

@router.post("/knowledge", response_model=Resource, status_code=status.HTTP_201_CREATED)
def create_knowledge_resource(
    resource: KnowledgeResourceCreate,
    repo: ResourceRepository = Depends(get_resource_repository)
):
    """
    Create a new Knowledge Resource.
    """
    db_resource = repo.create_typed_resource(resource_data=resource)
    return db_resource

@router.post("/human", response_model=Resource, status_code=status.HTTP_201_CREATED)
def create_human_resource(
    resource: HumanResourceCreate,
    repo: ResourceRepository = Depends(get_resource_repository)
):
    """
    Create a new Human Resource.
    """
    db_resource = repo.create_typed_resource(resource_data=resource)
    return db_resource

@router.post("/tool", response_model=Resource, status_code=status.HTTP_201_CREATED)
def create_tool_resource(
    resource: ToolResourceCreate,
    repo: ResourceRepository = Depends(get_resource_repository)
):
    """
    Create a new Tool Resource.
    """
    db_resource = repo.create_typed_resource(resource_data=resource)
    return db_resource

@router.post("/equipment", response_model=Resource, status_code=status.HTTP_201_CREATED)
def create_equipment_resource(
    resource: EquipmentResourceCreate,
    repo: ResourceRepository = Depends(get_resource_repository)
):
    """
    Create a new Equipment Resource.
    """
    db_resource = repo.create_typed_resource(resource_data=resource)
    return db_resource

@router.post("/space", response_model=Resource, status_code=status.HTTP_201_CREATED)
def create_space_resource(
    resource: SpaceResourceCreate,
    repo: ResourceRepository = Depends(get_resource_repository)
):
    """
    Create a new Space Resource.
    """
    db_resource = repo.create_typed_resource(resource_data=resource)
    return db_resource

# --- Resource Relationship Endpoints ---

@router.post("/{resource_uid}/assign-to-project/{project_uid}", response_model=Resource)
def assign_resource_to_project(
    resource_uid: str,
    project_uid: str,
    repo: ResourceRepository = Depends(get_resource_repository)
):
    """
    Assign a resource to a project.
    """
    resource = repo.assign_resource_to_project(resource_uid=resource_uid, project_uid=project_uid)
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Resource or Project not found"
        )
    return resource

@router.post("/{resource_uid}/assign-to-task/{task_uid}", response_model=Resource)
def assign_resource_to_task(
    resource_uid: str,
    task_uid: str,
    repo: ResourceRepository = Depends(get_resource_repository)
):
    """
    Assign a resource to a task.
    """
    resource = repo.assign_resource_to_task(resource_uid=resource_uid, task_uid=task_uid)
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Resource or Task not found"
        )
    return resource

# --- Additional Resource Query Endpoints ---

@router.get("/project/{project_uid}/resources", response_model=List[Resource])
def list_project_resources(
    project_uid: str,
    skip: int = 0,
    limit: int = 100,
    repo: ResourceRepository = Depends(get_resource_repository)
):
    """
    List all resources assigned to a specific project.
    """
    resources = repo.list_project_resources(project_uid=project_uid, skip=skip, limit=limit)
    return resources

@router.get("/task/{task_uid}/resources", response_model=List[Resource])
def list_task_resources(
    task_uid: str,
    skip: int = 0,
    limit: int = 100,
    repo: ResourceRepository = Depends(get_resource_repository)
):
    """
    List all resources used by a specific task.
    """
    resources = repo.list_task_resources(task_uid=task_uid, skip=skip, limit=limit)
    return resources
