from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
import uuid

# The base model for a Task, containing shared fields.
class TaskBase(BaseModel):
    name: str = Field(..., min_length=5, max_length=150, description="A clear and actionable name for the task.")
    description: Optional[str] = Field(None, description="A detailed description of what needs to be done.")
    status: str = Field("todo", description="The current status of the task (e.g., todo, in_progress, done, blocked).")
    effort: int = Field(1, ge=0, le=10, description="Estimated effort required, on a scale of 0-10.")

    # Configuration for Pydantic model.
    # from_attributes=True allows the model to be created from ORM objects.
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "Refactor the database query for user dashboards",
                "description": "The current query uses multiple joins and is causing performance issues. It needs to be optimized.",
                "status": "todo",
                "effort": 5
            }
        }
    )

# Pydantic model for creating a new Task.
# It requires a project_id to link the task to a project.
class TaskCreate(TaskBase):
    project_id: str = Field(..., description="The ID of the project this task belongs to.")

# Pydantic model for updating an existing Task.
# All fields are optional.
class TaskUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=5, max_length=150)
    description: Optional[str] = Field(None)
    status: Optional[str] = Field(None)
    effort: Optional[int] = Field(None, ge=0, le=10)

# This class represents the data structure of a Task as stored in the database.
# It inherits from TaskBase and adds system-generated fields like uid, created_at, updated_at.
class TaskInDB(TaskBase):
    # Align these fields with the BaseNode graph_model
    uid: str
    created_at: datetime
    updated_at: datetime

# This is the model that will be returned to the client in API responses.
# It inherits all fields from TaskInDB.
class Task(TaskInDB):
    pass
