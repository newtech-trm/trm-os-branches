from neomodel import StringProperty, RelationshipTo
from trm_api.graph_models.resolves_tension import ResolvesTensionRel
from trm_api.graph_models.generates_event import GeneratesEventRel
from trm_api.graph_models.leads_to_win import LeadsToWinRel
from trm_api.graph_models.is_part_of_project import IsPartOfProjectRel
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
    # Use IsPartOfProjectRel to store relationship properties according to ontology V3.2
    tasks = RelationshipTo('trm_api.graph_models.task.Task', 'HAS_TASK', model=IsPartOfProjectRel)
    
    # A project can resolve multiple tensions
    # Use ResolvesTensionRel to store relationship properties according to ontology V3.2
    resolves_tensions = RelationshipTo('trm_api.graph_models.tension.Tension', 'RESOLVES_TENSION', model=ResolvesTensionRel)
    
    # A project can generate events
    # Use GeneratesEventRel to store relationship properties according to ontology V3.2
    generates_events = RelationshipTo('trm_api.graph_models.event.Event', 'GENERATES_EVENT', model=GeneratesEventRel)
    
    # A project can lead to WINs (Wisdom-Infused Narratives)
    # Use LeadsToWinRel to store relationship properties according to ontology V3.2
    leads_to_wins = RelationshipTo('trm_api.graph_models.win.WIN', 'LEADS_TO_WIN', model=LeadsToWinRel)

    def __str__(self):
        return self.title
