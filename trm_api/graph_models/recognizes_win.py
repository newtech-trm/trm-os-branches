import uuid
from datetime import datetime
from neomodel import StructuredRel, StringProperty, DateTimeProperty, UniqueIdProperty

class RecognizesWinRel(StructuredRel):
    """
    Represents the relationship RECOGNIZES_WIN between a Recognition and a WIN.
    This relationship signifies that a Recognition acknowledges or is associated with a specific WIN.
    """
    # Properties of the relationship itself
    relationshipId = UniqueIdProperty(primary_key=True)
    created_at = DateTimeProperty(default_now=True)
    updated_at = DateTimeProperty(default_now=True)

    # Optional: Add other properties specific to this relationship if defined in Ontology V3.2
    # e.g., context = StringProperty(description="Context or reason for the recognition of this WIN.")

    def pre_save(self):
        self.updated_at = datetime.utcnow()

    def __str__(self):
        return f"RecognizesWinRel ({self.relationshipId})"
