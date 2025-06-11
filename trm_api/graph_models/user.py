from neomodel import StringProperty, RelationshipTo, EmailProperty, BooleanProperty
from .base import BaseNode

class User(BaseNode):
    """
    Represents a User or Person in the TRM-OS ontology.
    This is a graph model, not an API schema.
    """
    # Core properties based on the ontology design
    username = StringProperty(unique_index=True, required=True)
    email = EmailProperty(unique_index=True, required=True)
    hashed_password = StringProperty(required=True)
    full_name = StringProperty()
    is_active = BooleanProperty(default=True)
    role = StringProperty(default="Member") # e.g., Founder, Member, Admin

    # --- Relationships ---
    # Using forward reference strings ('Skill', 'Team', 'Project') to avoid circular import issues.
    # The actual classes will be resolved by neomodel at runtime.
    skills = RelationshipTo('trm_api.graph_models.skill.Skill', 'HAS_SKILL')
    teams = RelationshipTo('trm_api.graph_models.team.Team', 'PARTICIPATES_IN')
    managed_projects = RelationshipTo('trm_api.graph_models.project.Project', 'MANAGES_PROJECT')

    def __str__(self):
        return self.username
