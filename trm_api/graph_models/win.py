from neomodel import StringProperty, RelationshipFrom, RelationshipTo, IntegerProperty
from trm_api.graph_models.leads_to_win import LeadsToWinRel
from .base import BaseNode

class WIN(BaseNode):
    """
    Represents a WIN (Wisdom-Infused Narrative) in the TRM-OS ontology.
    A WIN is the valuable outcome of resolving a tension.
    """
    # Core properties
    title = StringProperty(required=True, index=True)
    narrative = StringProperty(required=True, description="The story of how the tension was resolved and what was learned.")
    impact_level = IntegerProperty(default=1) # e.g., 1 (Low), 2 (Medium), 3 (High)

    # --- Relationships ---
    # A WIN can result from various sources like RecognitionEvents or Projects
    # Using LeadsToWinRel to store relationship properties according to ontology V3.2
    source_recognition_events = RelationshipFrom('trm_api.graph_models.event.Event', 'LEADS_TO_WIN', model=LeadsToWinRel)
    source_projects = RelationshipFrom('trm_api.graph_models.project.Project', 'LEADS_TO_WIN', model=LeadsToWinRel)

    # A WIN can generate new knowledge.
    generated_knowledge = RelationshipTo('KnowledgeSnippet', 'GENERATES_KNOWLEDGE')

    def __str__(self):
        return self.title
