from neomodel import (
    StructuredRel,
    StringProperty,
    IntegerProperty,
    DateTimeProperty,
    BooleanProperty,
    FloatProperty
)
from datetime import datetime

class LeadsToWinRel(StructuredRel):
    """
    Relationship class for LEADS_TO_WIN, connecting RecognitionEvent/Project -> WIN.
    Following the TRM Ontology V3.2 specification.
    """
    # Required properties
    relationshipId = StringProperty(unique_index=True, required=True)
    contributionLevel = IntegerProperty(
        default=1,  # Không thể dùng cả required=True và default cùng lúc
        choices={
            1: "Minimal",
            2: "Minor", 
            3: "Moderate",
            4: "Significant",
            5: "Critical"
        }
    )
    creationDate = DateTimeProperty(default=datetime.now)
    lastModifiedDate = DateTimeProperty(default=datetime.now)
    
    # Optional properties
    directContribution = BooleanProperty(default=True)
    impactRatio = FloatProperty(min_value=0.0, max_value=1.0)  # Value between 0 and 1
    recognitionScore = IntegerProperty(min_value=1, max_value=100)
    verifiedBy = StringProperty()  # UID of the user/agent who verified this relationship
    verificationDate = DateTimeProperty()
    notes = StringProperty()
