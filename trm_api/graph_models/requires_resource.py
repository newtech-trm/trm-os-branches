from neomodel import (
    StructuredRel,
    StringProperty,
    IntegerProperty,
    DateTimeProperty,
    BooleanProperty,
    FloatProperty
)
from datetime import datetime

class RequiresResourceRel(StructuredRel):
    """
    Relationship class for REQUIRES_RESOURCE, connecting Project/Task -> Resource.
    Following the TRM Ontology V3.2 specification.
    """
    # Required properties
    relationshipId = StringProperty(unique_index=True, required=True)
    quantityNeeded = IntegerProperty(default=1)  # Không thể dùng cả required=True và default cùng lúc
    creationDate = DateTimeProperty(default_now=True)
    lastModifiedDate = DateTimeProperty(default_now=True)
    
    # Optional properties
    priorityLevel = IntegerProperty(
        default=3,
        choices={
            1: "Critical",
            2: "High", 
            3: "Medium",
            4: "Low",
            5: "Optional"
        }
    )
    isAvailable = BooleanProperty(default=False)
    estimatedCost = FloatProperty()  # Estimated cost of the resource
    actualCost = FloatProperty()  # Actual cost incurred
    procurementDeadline = DateTimeProperty()  # When the resource needs to be procured by
    allocatedBy = StringProperty()  # UID of the user/agent who allocated this resource
    allocatedDate = DateTimeProperty()  # When the resource was allocated
    notes = StringProperty()
