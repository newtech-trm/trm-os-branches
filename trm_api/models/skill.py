from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
import uuid

class SkillBase(BaseModel):
    name: str = Field(..., description="The unique name of the skill, e.g., 'PythonProgramming', 'DataAnalysis', 'ProjectManagement'.")
    description: str = Field(..., description="A detailed description of the skill and what it entails.")
    category: str = Field(..., description="The category of the skill, e.g., 'Technical', 'SoftSkills', 'Management'.")

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "name": "Neo4jCypherQuerying",
                "description": "The ability to write efficient and complex Cypher queries for the Neo4j graph database.",
                "category": "Technical"
            }
        }
    )

class SkillCreate(SkillBase):
    pass

class SkillUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None

class SkillInDB(SkillBase):
    skill_id: str = Field(alias="skillId", default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(alias="createdAt", default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(alias="updatedAt", default=None)

class Skill(SkillInDB):
    pass
