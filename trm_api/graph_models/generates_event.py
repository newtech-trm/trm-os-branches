from neomodel import (
    StructuredRel,
    StringProperty,
    IntegerProperty,
    DateTimeProperty,
    BooleanProperty
)
from datetime import datetime

class GeneratesEventRel(StructuredRel):
    """
    Relationship class for GENERATES_EVENT, connecting Project/Task/Agent -> Event.
    Following the TRM Ontology V3.2 specification.
    """
    # Required properties
    relationshipId = StringProperty(unique_index=True, required=True)
    generationType = StringProperty(
        default='Direct',  # Không thể dùng cả required=True và default cùng lúc
        choices={
            'Direct': 'Direct',
            'Indirect': 'Indirect',
            'Automated': 'Automated',
            'Manual': 'Manual',
            'System': 'System'
        }
    )
    creationDate = DateTimeProperty(default_now=True)
    lastModifiedDate = DateTimeProperty(default_now=True)
    
    # Optional properties
    impact = IntegerProperty(default=1)  # 1-5 scale of impact
    isVerified = BooleanProperty(default=False)
    verificationSource = StringProperty()
    context = StringProperty()
    notes = StringProperty()
