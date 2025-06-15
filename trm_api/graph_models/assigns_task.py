from neomodel import (
    StructuredRel,
    StringProperty,
    IntegerProperty,
    DateTimeProperty,
    BooleanProperty,
    FloatProperty
)
from datetime import datetime
import uuid

def generate_relationship_id():
    """Tạo ID duy nhất cho mối quan hệ"""
    return str(uuid.uuid4())

class AssignsTaskRel(StructuredRel):
    """
    Relationship class for ASSIGNS_TASK, connecting User/Agent -> Task.
    Following the TRM Ontology V3.2 specification.
    """
    # Required properties - do neomodel không cho phép dùng cả required và default, chúng ta sử dụng default để đảm bảo luôn có ID
    relationshipId = StringProperty(unique_index=True, default=generate_relationship_id)
    creationDate = DateTimeProperty(default_now=True)
    lastModifiedDate = DateTimeProperty(default_now=True)
    
    # Optional properties
    assignmentType = StringProperty(
        choices={
            'Primary': 'Primary assignee responsible for completion',
            'Supporting': 'Supporting role in completion',
            'Reviewer': 'Reviewing completed task',
            'Observer': 'Observing task progress only'
        }, 
        default='Primary'
    )
    
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
    
    estimatedEffort = FloatProperty()  # Estimated hours needed
    actualEffort = FloatProperty()     # Actual hours spent
    
    assignedBy = StringProperty()  # UID of user who made the assignment
    assignmentDate = DateTimeProperty(default_now=True)  # When task was assigned
    acceptanceDate = DateTimeProperty()  # When assignee accepted the task
    completionDate = DateTimeProperty()  # When assignee completed the task
    
    isAccepted = BooleanProperty(default=False)  # Whether assignee has accepted the task
    acceptance_notes = StringProperty()  # Notes during task acceptance
    
    notes = StringProperty()  # General notes about assignment
