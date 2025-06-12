from neomodel import (
    StructuredRel,
    StringProperty,
    FloatProperty,
    DateTimeProperty,
    RelationshipTo,
    RelationshipFrom
)
from datetime import datetime

class ResolvesTensionRel(StructuredRel):
    """
    Relationship class for RESOLVES_TENSION, connecting Project -> Tension.
    Following the TRM Ontology V3.2 specification.
    """
    # Required properties
    relationshipId = StringProperty(unique_index=True, required=True)
    resolutionStatus = StringProperty(
        default='Proposed',  # Không thể dùng cả required=True và default cùng lúc
        choices={
            'Proposed': 'Proposed',
            'ApprovedForResolution': 'Approved for Resolution',
            'ResolutionInProgress': 'Resolution in Progress',
            'PartiallyResolved': 'Partially Resolved',
            'Resolved': 'Resolved',
            'ResolutionFailed': 'Resolution Failed',
            'OnHold': 'On Hold',
            'Cancelled': 'Cancelled',
            'RequiresReview': 'Requires Review'
        }
    )
    creationDate = DateTimeProperty(default=datetime.now)
    lastModifiedDate = DateTimeProperty(default=datetime.now)
    
    # Optional properties
    resolutionApproach = StringProperty()
    expectedOutcome = StringProperty()
    alignmentScore = FloatProperty(default=0.0)
    priority = StringProperty(
        default='Medium',
        choices={
            'Critical': 'Critical',
            'High': 'High',
            'Medium': 'Medium',
            'Low': 'Low',
            'Informational': 'Informational'
        }
    )
    startDate = DateTimeProperty()
    targetResolutionDate = DateTimeProperty()
    actualResolutionDate = DateTimeProperty()
    notes = StringProperty()
