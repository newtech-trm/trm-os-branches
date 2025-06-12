from neomodel import StringProperty, IntegerProperty, RelationshipTo, RelationshipFrom, DateTimeProperty, ZeroOrMore
from trm_api.graph_models.generates_event import GeneratesEventRel
from trm_api.graph_models.is_part_of_project import IsPartOfProjectRel
from trm_api.graph_models.assigns_task import AssignsTaskRel
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
    # Use IsPartOfProjectRel to store relationship properties according to ontology V3.2
    project = RelationshipFrom('trm_api.graph_models.project.Project', 'HAS_TASK', model=IsPartOfProjectRel, cardinality=ZeroOrMore)

    # A task can be assigned to specific users or agents
    # Use AssignsTaskRel to store relationship properties according to ontology V3.2
    assignees_users = RelationshipFrom('trm_api.graph_models.user.User', 'ASSIGNS_TASK', model=AssignsTaskRel, cardinality=ZeroOrMore)
    assignees_agents = RelationshipFrom('trm_api.graph_models.agent.Agent', 'ASSIGNS_TASK', model=AssignsTaskRel, cardinality=ZeroOrMore)

    # A task can block other tasks.
    blocks = RelationshipTo('Task', 'BLOCKS', cardinality=ZeroOrMore)
    
    # A task can generate events
    # Use GeneratesEventRel to store relationship properties according to ontology V3.2
    generates_events = RelationshipTo('trm_api.graph_models.event.Event', 'GENERATES_EVENT', model=GeneratesEventRel)

    def __str__(self):
        return self.name
