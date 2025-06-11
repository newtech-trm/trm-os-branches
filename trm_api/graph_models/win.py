from neomodel import StringProperty, RelationshipTo, RelationshipFrom, IntegerProperty
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
    # A WIN results from resolving a tension.
    source_tension = RelationshipFrom('Tension', 'LEADS_TO_WIN')

    # A WIN can generate new knowledge.
    generated_knowledge = RelationshipTo('KnowledgeSnippet', 'GENERATES_KNOWLEDGE')

    def __str__(self):
        return self.title
