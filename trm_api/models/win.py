from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List, Any, Union
from datetime import datetime
import uuid
import logging

class WinBase(BaseModel):
    summary: str = Field(..., min_length=10, max_length=250, description="A concise summary of the WIN.")
    description: str = Field(..., description="A detailed description of the achievement, its impact, and how it was accomplished.")
    win_type: str = Field(..., alias="winType", description="The type of WIN, e.g., 'ProcessImprovement', 'ProductFeature', 'RevenueMilestone'.")
    related_entity_ids: List[str] = Field(..., alias="relatedEntityIds", description="List of IDs (Tasks, Projects) that led to this WIN.")

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "summary": "Reduced API latency by 50% for key endpoints.",
                "description": "By optimizing database queries and implementing a caching layer, we successfully cut the P95 latency for the user dashboard and data export APIs in half.",
                "winType": "ProcessImprovement",
                "relatedEntityIds": ["task_id_1", "task_id_2"]
            }
        }
    )

class WinCreate(WinBase):
    pass

class WinUpdate(BaseModel):
    summary: Optional[str] = Field(None, min_length=10, max_length=250)
    description: Optional[str] = None
    win_type: Optional[str] = Field(None, alias="winType")

class WinInDB(WinBase):
    win_id: str = Field(alias="winId", default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(alias="createdAt", default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(alias="updatedAt", default=None)

class Win(WinInDB):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    @classmethod
    @field_validator('created_at', 'updated_at', mode='before')
    def validate_datetime(cls, value: Any) -> Union[datetime, None]:
        if value is None:
            return None
            
        # Log the type and value for debugging
        logging.debug(f"Validating datetime field: {value}, type: {type(value)}")
        
        # Handle Neo4j DateTime objects
        if hasattr(value, 'to_native'):
            logging.debug(f"Converting Neo4j DateTime to native: {value}")
            return value.to_native()
            
        # Already a datetime
        if isinstance(value, datetime):
            return value
            
        # Try to convert from string representation
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                try:
                    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")
                except ValueError:
                    pass
        
        # Last resort: return current time and log an error
        logging.error(f"Could not convert value to datetime: {value}, type: {type(value)}")
        return datetime.utcnow()
