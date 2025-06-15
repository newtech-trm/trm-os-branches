from neomodel import (
    StructuredRel,
    StringProperty,
    IntegerProperty,
    DateTimeProperty,
    BooleanProperty
)
from datetime import datetime

class IsPartOfProjectRel(StructuredRel):
    """
    Relationship class for IS_PART_OF_PROJECT, connecting Task -> Project.
    Following the TRM Ontology V3.2 specification.
    """
    # Required properties
    relationshipId = StringProperty(unique_index=True, required=True)
    taskOrder = IntegerProperty(default=0)  # Không thể dùng cả required=True và default cùng lúc
    creationDate = DateTimeProperty(default_now=True)
    lastModifiedDate = DateTimeProperty(default_now=True)
    
    # Optional properties
    isRequired = BooleanProperty(default=True)  # Whether task is required for project completion
    criticality = IntegerProperty(
        default=3,
        choices={
            1: "Critical",
            2: "High", 
            3: "Medium",
            4: "Low",
            5: "Optional"
        }
    )
    dependsOn = StringProperty()  # UID of task that this task depends on
    milestone = StringProperty()  # Milestone this task contributes to
    addedBy = StringProperty()  # UID of user who added this task to the project
    notes = StringProperty()
