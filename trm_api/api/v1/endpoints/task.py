from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any, List

from trm_api.models.task import Task, TaskCreate, TaskUpdate
from trm_api.repositories.task_repository import TaskRepository

router = APIRouter()

def get_task_repo() -> TaskRepository:
    return TaskRepository()

@router.get("/", response_model=List[Task])
def list_tasks_for_project(
    *, 
    project_id: str,
    skip: int = 0,
    limit: int = 100,
    repo: TaskRepository = Depends(get_task_repo)
) -> Any:
    """
    Retrieve tasks for a specific project.
    """
    tasks = repo.list_tasks_for_project(project_id=project_id, skip=skip, limit=limit)
    return tasks

@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(
    *, 
    task_in: TaskCreate, 
    repo: TaskRepository = Depends(get_task_repo)
) -> Any:
    """
    Create a new task for a project.
    """
    # The repository now handles finding the project and linking it.
    created_task = repo.create_task(task_data=task_in)
    if not created_task:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not create task. Ensure project with ID {task_in.project_id} exists."
        )
    return created_task

@router.get("/{task_id}", response_model=Task)
def get_task(
    *, 
    task_id: str, 
    repo: TaskRepository = Depends(get_task_repo)
) -> Any:
    """
    Get task by ID.
    """
    task = repo.get_task_by_uid(uid=task_id)
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
    repo: TaskRepository = Depends(get_task_repo)
) -> Any:
    """
    Update a task.
    """
    updated_task = repo.update_task(uid=task_id, task_data=task_in)
    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return updated_task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    *, 
    task_id: str,
    repo: TaskRepository = Depends(get_task_repo)
) -> None:
    """
    Delete a task.
    """
    deleted = repo.delete_task(uid=task_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return None
