from neomodel import StringProperty, RelationshipTo, ZeroOrMore
from .base import BaseNode

class Team(BaseNode):
    """
    Represents a Team in the TRM-OS ontology.
    A team is a group of users working together.
    """
    # Core properties, aligned with Pydantic's TeamBase
    name = StringProperty(required=True, unique_index=True)
    description = StringProperty()

    # --- Relationships ---

    # A team is composed of multiple users (members).
    members = RelationshipTo('trm_api.graph_models.user.User', 'MEMBER_OF', cardinality=ZeroOrMore)

    # A team works on one or more projects.
    projects = RelationshipTo('trm_api.graph_models.project.Project', 'WORKS_ON', cardinality=ZeroOrMore)

    def __str__(self):
        return self.name
