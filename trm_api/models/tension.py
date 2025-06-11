from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
import uuid

class TensionBase(BaseModel):
    summary: str = Field(..., min_length=10, max_length=200, description="A concise summary of the tension.")
    description: str = Field(..., description="A detailed description of the tension, its context, and impact.")
    status: str = Field("open", description="The current status of the tension (e.g., open, in_progress, resolved, closed).")
    priority: str = Field("medium", description="The priority of the tension (e.g., low, medium, high, critical).")

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "summary": "API response time is too slow for user-facing queries.",
                "description": "Users are experiencing significant delays when fetching their data from the dashboard. This seems to be caused by an inefficient database query in the backend.",
                "status": "open",
                "priority": "high"
            }
        }
    )

class TensionCreate(TensionBase):
    # When creating a tension, we need to know which project it belongs to.
    project_id: str = Field(..., alias="projectId", description="The ID of the project this tension belongs to.")

class TensionUpdate(BaseModel):
    summary: Optional[str] = Field(None, min_length=10, max_length=200)
    description: Optional[str] = Field(None)
    status: Optional[str] = Field(None)
    priority: Optional[str] = Field(None)

class TensionInDB(TensionBase):
    tension_id: str = Field(alias="tensionId", default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(alias="createdAt", default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(alias="updatedAt", default=None)

class Tension(TensionInDB):
    pass
