from neomodel import StringProperty, IntegerProperty, RelationshipTo, RelationshipFrom, DateTimeProperty, ZeroOrMore
from .base import BaseNode

class Task(BaseNode):
    """
    Represents a Task in the TRM-OS ontology.
    A task is a specific action item that is part of a project.
    This model is aligned with the Pydantic TaskBase model.
    """
    # --- Core properties aligned with Pydantic's TaskBase ---
    name = StringProperty(required=True, index=True)
    description = StringProperty()
    status = StringProperty(default='todo')
    effort = IntegerProperty(default=1)
    due_date = DateTimeProperty()

    # --- Relationships ---
    # Define the relationship back to the parent project.
    # This complements the 'tasks' relationship in the Project model.
    project = RelationshipFrom('trm_api.graph_models.project.Project', 'HAS_TASK', cardinality=ZeroOrMore)

    # A task can be assigned to specific users.
    assignees = RelationshipTo('trm_api.graph_models.user.User', 'ASSIGNED_TO', cardinality=ZeroOrMore)

    # A task can block other tasks.
    blocks = RelationshipTo('Task', 'BLOCKS', cardinality=ZeroOrMore)

    def __str__(self):
        return self.name
