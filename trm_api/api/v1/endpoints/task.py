from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Any, List, Dict, Optional

from trm_api.models.pagination import PaginatedResponse

from trm_api.models.task import Task, TaskCreate, TaskUpdate
from trm_api.repositories.task_repository import TaskRepository

router = APIRouter()

def get_task_repo() -> TaskRepository:
    return TaskRepository()

@router.get("/", response_model=PaginatedResponse[Task])
def list_tasks_for_project(
    *, 
    project_id: str,
    page: int = Query(1, ge=1, description="Page number, 1-indexed"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    repo: TaskRepository = Depends(get_task_repo)
) -> Any:
    """
    Retrieve paginated tasks for a specific project.
    """
    tasks, total_count, page_count = repo.get_paginated_tasks_for_project(
        project_id=project_id, 
        page=page, 
        page_size=page_size
    )
    return PaginatedResponse.create(items=tasks, total_count=total_count, page=page, page_size=page_size)

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

# --- Task Assignment Endpoints ---

@router.post("/{task_id}/assign/user/{user_id}", status_code=status.HTTP_200_OK)
def assign_task_to_user(
    *,
    task_id: str,
    user_id: str,
    assignment_type: str = Query('Primary', description="Type of assignment: Primary, Supporting, Reviewer, Observer"),
    priority_level: int = Query(3, description="Priority level (1-5): 1=Critical, 2=High, 3=Medium, 4=Low, 5=Optional"),
    estimated_effort: Optional[float] = Query(None, description="Estimated effort in hours"),
    assigned_by: Optional[str] = Query(None, description="User ID of the person making the assignment"),
    notes: Optional[str] = Query(None, description="Additional notes about this assignment"),
    repo: TaskRepository = Depends(get_task_repo)
) -> Dict[str, Any]:
    """
    Assign a task to a user with ASSIGNS_TASK relationship properties.
    
    This follows the TRM Ontology V3.2 specification for ASSIGNS_TASK relationship.
    """
    result = repo.assign_task_to_user(
        task_uid=task_id, 
        user_uid=user_id,
        assignment_type=assignment_type,
        priority_level=priority_level,
        estimated_effort=estimated_effort,
        assigned_by=assigned_by,
        notes=notes
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task or user not found"
        )
    
    task, user = result
    return {
        "message": f"Task {task_id} successfully assigned to user {user_id}",
        "task_id": task_id,
        "user_id": user_id,
        "assignment_type": assignment_type,
        "priority_level": priority_level
    }

@router.post("/{task_id}/assign/agent/{agent_id}", status_code=status.HTTP_200_OK)
def assign_task_to_agent(
    *,
    task_id: str,
    agent_id: str,
    assignment_type: str = Query('Primary', description="Type of assignment: Primary, Supporting, Reviewer, Observer"),
    priority_level: int = Query(3, description="Priority level (1-5): 1=Critical, 2=High, 3=Medium, 4=Low, 5=Optional"),
    estimated_effort: Optional[float] = Query(None, description="Estimated effort in hours"),
    assigned_by: Optional[str] = Query(None, description="User ID of the person making the assignment"),
    notes: Optional[str] = Query(None, description="Additional notes about this assignment"),
    repo: TaskRepository = Depends(get_task_repo)
) -> Dict[str, Any]:
    """
    Assign a task to an agent with ASSIGNS_TASK relationship properties.
    
    This follows the TRM Ontology V3.2 specification for ASSIGNS_TASK relationship.
    """
    result = repo.assign_task_to_agent(
        task_uid=task_id, 
        agent_uid=agent_id,
        assignment_type=assignment_type,
        priority_level=priority_level,
        estimated_effort=estimated_effort,
        assigned_by=assigned_by,
        notes=notes
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task or agent not found"
        )
    
    task, agent = result
    return {
        "message": f"Task {task_id} successfully assigned to agent {agent_id}",
        "task_id": task_id,
        "agent_id": agent_id,
        "assignment_type": assignment_type,
        "priority_level": priority_level
    }

@router.get("/{task_id}/assignees", status_code=status.HTTP_200_OK)
def get_task_assignees(
    *,
    task_id: str,
    include_relationship_details: bool = Query(False, description="Include detailed relationship properties"),
    repo: TaskRepository = Depends(get_task_repo)
) -> Dict[str, Any]:
    """
    Get all assignees (users and agents) for a specific task.
    
    If include_relationship_details is True, returns full relationship properties
    according to TRM Ontology V3.2.
    """
    # Check if task exists
    task = repo.get_task_by_uid(uid=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Get assignees with or without relationship details
    if include_relationship_details:
        assignees = repo.get_task_assignees_with_relationships(task_uid=task_id)
    else:
        assignees = repo.get_task_assignees(task_uid=task_id)
    
    return assignees

@router.post("/{task_id}/accept", status_code=status.HTTP_200_OK)
def accept_task_assignment(
    *,
    task_id: str,
    assignee_id: str = Query(..., description="ID of the user or agent accepting the task"),
    acceptance_notes: Optional[str] = Query(None, description="Optional notes about task acceptance"),
    repo: TaskRepository = Depends(get_task_repo)
) -> Dict[str, Any]:
    """
    Accept a task assignment by the assigned user or agent.
    
    Updates the ASSIGNS_TASK relationship with acceptance information.
    """
    success = repo.accept_task_assignment(
        task_uid=task_id,
        assignee_uid=assignee_id,
        acceptance_notes=acceptance_notes
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task, assignee, or assignment relationship not found"
        )
    
    return {
        "message": f"Task {task_id} has been accepted by {assignee_id}",
        "task_id": task_id,
        "assignee_id": assignee_id,
        "accepted": True
    }

@router.post("/{task_id}/complete", status_code=status.HTTP_200_OK)
def complete_task_assignment(
    *,
    task_id: str,
    assignee_id: str = Query(..., description="ID of the user or agent completing the task"),
    actual_effort: Optional[float] = Query(None, description="Actual effort spent in hours"),
    repo: TaskRepository = Depends(get_task_repo)
) -> Dict[str, Any]:
    """
    Mark a task assignment as completed by the assigned user or agent.
    
    Updates the ASSIGNS_TASK relationship with completion information.
    """
    success = repo.complete_task_assignment(
        task_uid=task_id,
        assignee_uid=assignee_id,
        actual_effort=actual_effort
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task, assignee, or assignment relationship not found"
        )
    
    return {
        "message": f"Task {task_id} has been completed by {assignee_id}",
        "task_id": task_id,
        "assignee_id": assignee_id,
        "completed": True
    }

@router.delete("/{task_id}/assignment/{assignee_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_task_assignment(
    *,
    task_id: str,
    assignee_id: str,
    repo: TaskRepository = Depends(get_task_repo)
) -> None:
    """
    Remove a task assignment (ASSIGNS_TASK relationship) between a task and a user/agent.
    """
    success = repo.remove_assignment(task_uid=task_id, assignee_uid=assignee_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task, assignee, or assignment relationship not found"
        )
    
    return None
