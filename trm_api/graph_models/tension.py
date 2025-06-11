from neomodel import StringProperty, RelationshipTo, RelationshipFrom, IntegerProperty
from .base import BaseNode

class Tension(BaseNode):
    """
    Represents a Tension in the TRM-OS ontology.
    A tension is a gap between the current reality and a desired potential.
    It can be a problem, risk, issue, or opportunity.
    """
    # Core properties
    title = StringProperty(required=True, index=True)
    description = StringProperty(required=True)
    status = StringProperty(default='detected') # e.g., 'detected', 'in_resolution', 'resolved', 'archived'
    severity = IntegerProperty(default=1) # e.g., 1 (Low), 2 (Medium), 3 (High), 4 (Critical)

    # --- Relationships ---
    # A tension is detected by a user or an agent.
    detected_by = RelationshipTo('User', 'DETECTED_BY') # Can also be an Agent later

    # A tension relates to a specific context, like a project or task.
    # Using a generic relationship for flexibility.
    context = RelationshipTo('BaseNode', 'RELATES_TO')

    # A resolved tension leads to a WIN.
    resolution = RelationshipTo('WIN', 'LEADS_TO_WIN')

    def __str__(self):
        return self.title
