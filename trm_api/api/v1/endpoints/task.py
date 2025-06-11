from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any, List

from trm_api.models.task import Task, TaskCreate, TaskUpdate
from trm_api.models.relationships import Relationship
from trm_api.services.task_service import task_service, TaskService

router = APIRouter()

def get_task_service() -> TaskService:
    return task_service

@router.get("/", response_model=List[Task])
def list_tasks_for_tension(
    *, 
    tension_id: str,
    skip: int = 0,
    limit: int = 100,
    service: TaskService = Depends(get_task_service)
) -> Any:
    """
    Retrieve tasks for a specific tension.
    """
    tasks = service.list_tasks_for_tension(tension_id=tension_id, skip=skip, limit=limit)
    return tasks

@router.get("/{task_id}", response_model=Task)
def get_task(
    *, 
    task_id: str,
    service: TaskService = Depends(get_task_service)
) -> Any:
    """
    Get task by ID.
    """
    task = service.get_task_by_id(task_id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Task not found"
        )
    return task

@router.put("/{task_id}", response_model=Task)
def update_task(
    *, 
    task_id: str,
    task_in: TaskUpdate,
    service: TaskService = Depends(get_task_service)
) -> Any:
    """
    Update a task.
    """
    task = service.get_task_by_id(task_id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Task not found"
        )
    updated_task = service.update_task(task_id=task_id, task_update=task_in)
    return updated_task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    *, 
    task_id: str,
    service: TaskService = Depends(get_task_service)
) -> None:
    """
    Delete a task.
    """
    task = service.get_task_by_id(task_id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Task not found"
        )
    service.delete_task(task_id=task_id)
    return None

@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(
    *, 
    task_in: TaskCreate,
    service: TaskService = Depends(get_task_service)
) -> Any:
    """
    Create new task for a tension.
    """
    created_task = service.create_task_for_tension(task_create=task_in)
    if not created_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tension with ID {task_in.tension_id} not found."
        )
    return created_task


@router.post("/{task_id}/assign-to/{user_id}", response_model=Relationship, status_code=status.HTTP_201_CREATED)
def assign_task_to_user(
    *,
    task_id: str,
    user_id: str,
    service: TaskService = Depends(get_task_service)
) -> Any:
    """
    Assigns a task to a user, creating a PERFORMS relationship.
    """
    relationship = service.assign_task_to_user(task_id=task_id, user_id=user_id)
    if relationship is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task or User not found, or relationship could not be created"
        )
    return relationship
