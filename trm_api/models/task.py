from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
import uuid

class TaskBase(BaseModel):
    name: str = Field(..., min_length=5, max_length=150, description="A clear and actionable name for the task.")
    description: Optional[str] = Field(None, description="A detailed description of what needs to be done.")
    status: str = Field("todo", description="The current status of the task (e.g., todo, in_progress, done, blocked).")
    effort: int = Field(1, ge=0, le=10, description="Estimated effort required, on a scale of 0-10.")

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "name": "Refactor the database query for user dashboards",
                "description": "The current query uses multiple joins and is causing performance issues. It needs to be optimized.",
                "status": "todo",
                "effort": 5
            }
        }
    )

class TaskCreate(TaskBase):
    # When creating a task, we need to know which tension it resolves.
    tension_id: str = Field(..., alias="tensionId", description="The ID of the tension this task helps to resolve.")

class TaskUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=5, max_length=150)
    description: Optional[str] = Field(None)
    status: Optional[str] = Field(None)
    effort: Optional[int] = Field(None, ge=0, le=10)

class TaskInDB(TaskBase):
    task_id: str = Field(alias="taskId", default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(alias="createdAt", default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(alias="updatedAt", default=None)
    completed_at: Optional[datetime] = Field(alias="completedAt", default=None)

class Task(TaskInDB):
    pass
