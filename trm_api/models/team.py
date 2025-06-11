from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
import uuid

class TeamBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, description="The unique name of the team.")
    description: Optional[str] = Field(None, description="A brief description of the team's purpose.")

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "name": "Core Platform Engineering",
                "description": "Manages the core infrastructure and CI/CD pipelines."
            }
        }
    )

class TeamCreate(TeamBase):
    pass

class TeamUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None

class TeamInDB(TeamBase):
    team_id: str = Field(alias="teamId", default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(alias="createdAt", default_factory=datetime.utcnow)
    updated_at: datetime = Field(alias="updatedAt", default_factory=datetime.utcnow)

class Team(TeamInDB):
    # In the future, this could be populated with a list of User models
    # members: List['User'] = []
    pass
