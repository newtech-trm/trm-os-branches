from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class TargetEntityTypeEnum(str, Enum):
    """Enum for all possible entity types that can be part of a relationship."""
    AGENT = "Agent"
    EVENT = "Event"
    KNOWLEDGE_SNIPPET = "KnowledgeSnippet"
    PROJECT = "Project"
    RECOGNITION = "Recognition"
    SKILL = "Skill"
    TASK = "Task"
    TEAM = "Team"
    TENSION = "Tension"
    TOOL = "Tool"
    USER = "User"
    WIN = "Win"


class RelationshipType(str, Enum):
    """Enum for all possible relationship types in the ontology."""
    # User-centric
    IDENTIFIED = "IDENTIFIED"      # User -> Tension
    PERFORMS = "PERFORMS"          # User -> Task
    HAS_SKILL = "HAS_SKILL"        # User -> Skill
    HAS_MEMBER = "HAS_MEMBER"      # Team -> User
    HAS_PARTICIPANT = "HAS_PARTICIPANT" # Project -> User
    AUTHORED = "AUTHORED"          # User -> KnowledgeSnippet
    RECEIVED = "RECEIVED"          # User -> Recognition
    GAVE = "GAVE"                  # User -> Recognition
    OWNS = "OWNS"                  # User -> Project/Team

    # Task-centric
    RELATES_TO = "RELATES_TO"      # Task -> Tension/Win
    REQUIRES = "REQUIRES"          # Task -> Skill
    USES = "USES"                  # Task -> Tool

    # Project/Team-centric
    HAS_TENSION = "HAS_TENSION"    # Project -> Tension
    RESOLVES_TENSION = "RESOLVES_TENSION"  # Project -> Tension
    ACHIEVED = "ACHIEVED"          # Project -> Win

    # Knowledge-centric
    DOCUMENTS = "DOCUMENTS"        # KnowledgeSnippet -> Win/Tension/Task
    IMPROVES = "IMPROVES"          # KnowledgeSnippet -> Skill


class Relationship(BaseModel):
    """
    Pydantic model representing a generic relationship between two nodes as returned by a Cypher query.
    """
    source_id: str
    source_type: str
    target_id: str
    target_type: str
    type: str
    createdAt: datetime

    class Config:
        from_attributes = True
        populate_by_name = True
