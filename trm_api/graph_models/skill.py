from neomodel import StringProperty, RelationshipFrom
from .base import BaseNode

class GraphSkill(BaseNode):
    """
    Represents a skill or competency in the TRM-OS ontology.
    e.g., 'Python Programming', 'Project Management', 'Financial Analysis'
    """
    # Core properties
    name = StringProperty(required=True, unique_index=True)
    description = StringProperty()
    category = StringProperty()

    # --- Relationships ---
    # A skill is possessed by one or more users.
    skilled_users = RelationshipFrom('trm_api.graph_models.user.GraphUser', 'HAS_SKILL')

    def __str__(self):
        return self.name
