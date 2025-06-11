from neomodel import StringProperty, RelationshipTo
from .base import BaseNode

class Agent(BaseNode):
    """
    Represents an AI Agent in the TRM-OS ontology.
    Agents are non-human actors that perform automated tasks.
    """
    # Core properties
    name = StringProperty(required=True, unique_index=True)
    # e.g., 'KnowledgeValidationAgent', 'ProjectManagementAgent'
    agent_type = StringProperty(required=True, index=True)
    status = StringProperty(default='active') # e.g., 'active', 'inactive', 'error'
    description = StringProperty()

    # --- Relationships ---
    # An agent can trigger events.
    triggered_events = RelationshipTo('Event', 'TRIGGERED_EVENT')

    # An agent can be managed by another agent (e.g., AGE).
    managed_by = RelationshipTo('Agent', 'MANAGED_BY')

    def __str__(self):
        return self.name
