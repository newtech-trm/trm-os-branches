from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
import uuid

class AgentBase(BaseModel):
    name: str = Field(..., description="The unique name of the agent, e.g., 'CodeReviewerAgent'.")
    purpose: str = Field(..., description="The agent's primary function or goal.")
    version: str = Field("1.0.0", description="The version of the agent's logic and capabilities.")
    # Could be 'active', 'inactive', 'deprecated'
    status: str = Field("active", description="The operational status of the agent.")

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "name": "ReleaseNotesDrafterAgent",
                "purpose": "Monitors 'done' tasks in a project and drafts release notes based on them.",
                "version": "1.1.0",
                "status": "active"
            }
        }
    )

class AgentCreate(AgentBase):
    # When creating an agent, we can specify the tools it can use by their IDs
    tool_ids: Optional[List[str]] = Field(None, alias="toolIds", description="List of tool IDs this agent is equipped to use.")

class AgentUpdate(BaseModel):
    name: Optional[str] = None
    purpose: Optional[str] = None
    version: Optional[str] = None
    status: Optional[str] = None
    tool_ids: Optional[List[str]] = Field(None, alias="toolIds")

class AgentInDB(AgentBase):
    agent_id: str = Field(alias="agentId", default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(alias="createdAt", default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(alias="updatedAt", default=None)

class Agent(AgentInDB):
    # In the future, this could be populated with a list of Tool models
    # tools: List['Tool'] = []
    pass
