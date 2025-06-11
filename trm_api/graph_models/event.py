from neomodel import StringProperty, RelationshipTo, JSONProperty
from .base import BaseNode

class Event(BaseNode):
    """
    Represents an Event in the TRM-OS ontology.
    An event is an immutable record of something that has happened.
    """
    # Core properties
    # e.g., 'TensionDetected', 'TaskCompleted', 'UserJoinedTeam'
    event_type = StringProperty(required=True, index=True)

    # The data associated with the event, stored in a flexible JSON format
    payload = JSONProperty()

    # --- Relationships ---
    # An event is triggered by a user or an agent.
    triggered_by = RelationshipTo('BaseNode', 'TRIGGERED_BY') # User or Agent

    # An event often relates to a specific entity.
    context = RelationshipTo('BaseNode', 'RELATES_TO')

    def __str__(self):
        return f"{self.event_type} (UID: {self.uid})"
