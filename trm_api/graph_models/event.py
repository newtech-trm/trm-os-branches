from neomodel import StringProperty, RelationshipTo, RelationshipFrom, JSONProperty, ArrayProperty
from neomodel.sync_.cardinality import ZeroOrOne, ZeroOrMore

from .base import BaseNode
from .generates_event import GeneratesEventRel # Assuming this defines GeneratesEventRel
# Ensure other models are accessible for relationship definitions if not directly imported:
# e.g., .agent.Agent, .project.Project, .task.Task, .recognition.Recognition, .win.WIN, .resource.Resource, .team.Team

class Event(BaseNode):
    """
    Represents an Event in the TRM-OS ontology.
    An event is an immutable record of something that has happened, providing an audit trail 
    and enabling reactive logic or data analysis.
    """
    # Core properties from BaseNode: uid, created_at, updated_at

    # Specific Event properties
    name = StringProperty(required=True, index=True, description="The type or name of the event, e.g., 'TASK_CREATED', 'USER_LOGGED_IN'.")
    description = StringProperty(required=False, description="A human-readable description of the event.")
    payload = JSONProperty(required=False, description="A flexible JSON object containing event-specific data.")
    tags = ArrayProperty(StringProperty(), default=list, description="Tags for categorizing or filtering events.")

    # --- Relationships ---

    # Who/What triggered or initiated this event.
    # Assumes Agent model is at '.agent.Agent'. Add other actor types if necessary (e.g., '.user.User').
    # This means an Agent has an outgoing 'ACTOR_TRIGGERED_EVENT' relationship to this Event.
    triggered_by_actor = RelationshipFrom('.agent.Agent', 'ACTOR_TRIGGERED_EVENT')

    # The primary entity this event relates to or is in the context of.
    # Event has an outgoing 'EVENT_CONTEXT' relationship to specific entity types.
    # Instead of connecting to abstract BaseNode, define separate relationships for each type
    primary_context_agent = RelationshipTo('.agent.Agent', 'EVENT_CONTEXT', cardinality=ZeroOrOne)
    primary_context_project = RelationshipTo('.project.Project', 'EVENT_CONTEXT', cardinality=ZeroOrOne)
    primary_context_task = RelationshipTo('.task.Task', 'EVENT_CONTEXT', cardinality=ZeroOrOne)
    primary_context_resource = RelationshipTo('.resource.Resource', 'EVENT_CONTEXT', cardinality=ZeroOrOne)

    # Entities that generate this event.
    # These are incoming 'GENERATES_EVENT' relationships to this Event node.
    generated_by_projects = RelationshipFrom('.project.Project', 'GENERATES_EVENT', model=GeneratesEventRel)
    generated_by_tasks = RelationshipFrom('.task.Task', 'GENERATES_EVENT', model=GeneratesEventRel)
    generated_by_agents = RelationshipFrom('.agent.Agent', 'GENERATES_EVENT', model=GeneratesEventRel)
    generated_by_recognitions = RelationshipFrom('.recognition.Recognition', 'GENERATES_EVENT', cardinality=ZeroOrMore)
    generated_by_wins = RelationshipFrom('.win.WIN', 'GENERATES_EVENT', cardinality=ZeroOrMore)
    # Consider if other entities like 'User' (if distinct from Agent) or 'Team' can generate events.

    def __str__(self):
        return f"{self.name} (UID: {self.uid})"
