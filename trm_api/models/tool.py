from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

class ToolBase(BaseModel):
    name: str = Field(..., description="Unique name for the tool, e.g., 'git_clone_repository'.")
    description: str = Field(..., description="What this tool does and when to use it.")
    # Example: 'python_function', 'shell_command', 'api_endpoint'
    type: str = Field(..., description="The type of the tool.")
    # Contains invocation details, e.g., function name, command template, API URL
    invocation_details: Dict[str, Any] = Field(..., alias="invocationDetails", description="Details needed to run the tool.")

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "name": "send_slack_message",
                "description": "Sends a message to a specified Slack channel.",
                "type": "api_endpoint",
                "invocationDetails": {
                    "method": "POST",
                    "url": "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX",
                    "headers": {"Content-type": "application/json"},
                    "body_template": "{\"text\": \"{{message}}\"}"
                }
            }
        }
    )

class ToolCreate(ToolBase):
    pass

class ToolUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    invocation_details: Optional[Dict[str, Any]] = Field(None, alias="invocationDetails")

class ToolInDB(ToolBase):
    tool_id: str = Field(alias="toolId", default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(alias="createdAt", default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(alias="updatedAt", default=None)

class Tool(ToolInDB):
    pass
