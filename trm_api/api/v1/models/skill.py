from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class SkillBase(BaseModel):
    """
    Base Pydantic model for a Skill.
    """
    name: str
    description: Optional[str] = None
    category: Optional[str] = None

class SkillCreate(SkillBase):
    """
    Pydantic model for creating a new Skill.
    """
    pass

class SkillUpdate(SkillBase):
    """
    Pydantic model for updating an existing Skill.
    All fields are optional for updates.
    """
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None


class Skill(SkillBase):
    """
    Pydantic model for representing a Skill, including database-generated fields.
    """
    uid: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )
