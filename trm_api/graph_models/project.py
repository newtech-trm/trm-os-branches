from neomodel import StringProperty, RelationshipTo
from .base import BaseNode

class Project(BaseNode):
    """
    Represents a Project in the TRM-OS ontology.
    """
    # Core properties
    title = StringProperty(required=True, index=True)
    description = StringProperty()
    status = StringProperty(default='active') # e.g., 'active', 'completed', 'on_hold'

    # --- Relationships ---
    # A project consists of multiple tasks.
    # Use a full path forward reference to avoid circular import issues
    tasks = RelationshipTo('trm_api.graph_models.task.Task', 'HAS_TASK')

    def __str__(self):
        return self.title
