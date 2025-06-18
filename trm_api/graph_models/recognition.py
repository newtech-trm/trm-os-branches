from neomodel import (
    StructuredNode, StringProperty, UniqueIdProperty,
    DateTimeProperty, ArrayProperty, RelationshipFrom, RelationshipTo
)
from datetime import datetime
import uuid

from .base import BaseNode

class Recognition(BaseNode):
    """
    Neo4j node representing a Recognition in the system. (Ontology V3.2)
    Recognitions acknowledge value, contributions, or achievements, often linked to a WIN.
    """
    # Core Properties
    name = StringProperty(required=True, index=True)  # A concise title for the recognition
    message = StringProperty(required=True)           # Detailed message or description
    recognitionType = StringProperty(default="GRATITUDE", index=True, choices={ # e.g., 'Gratitude', 'Impact', 'Innovation', 'Endorsement'
        "GRATITUDE": "Expressing gratitude for an action or contribution.",
        "IMPACT": "Acknowledging significant impact or results.",
        "INNOVATION": "Recognizing novel ideas or approaches.",
        "ENDORSEMENT": "Endorsing a skill, capability, or work.",
        "ACHIEVEMENT": "Celebrating a specific achievement or milestone.",
        "KUDOS": "Cung cấp lời khen ngơi hoặc cổ vũ cho người khác.",
        "Gratitude": "Expressing gratitude for an action or contribution (Title-case).",
        "RecognitionType.GRATITUDE": "Enum name với giá trị GRATITUDE."
    })
    status = StringProperty(choices={
        'PROPOSED': 'Proposed', 
        'GRANTED': 'Granted', 
        'ARCHIVED': 'Archived',
        'RecognitionStatus.PROPOSED': 'Enum name với giá trị PROPOSED',
        'RecognitionStatus.GRANTED': 'Enum name với giá trị GRANTED',
        'RecognitionStatus.ARCHIVED': 'Enum name với giá trị ARCHIVED',
        'Proposed': 'Title-case PROPOSED',
        'Granted': 'Title-case GRANTED',
        'Archived': 'Title-case ARCHIVED'
    }, default='GRANTED', index=True)
    value_level = StringProperty(index=True, required=False) # Qualitative (e.g., "High Value") or quantitative score
    tags = ArrayProperty(StringProperty(), default=lambda: []) # Using lambda for default mutable

    # Relationships (Ontology V3.2)
    # Agent who grants the recognition
    given_by = RelationshipFrom('trm_api.graph_models.agent.Agent', 'GIVEN_BY')
    # Agent(s) who receive the recognition
    received_by = RelationshipTo('trm_api.graph_models.agent.Agent', 'RECEIVED_BY')
    # WIN that this recognition is for (primary focus)
    recognizes_win = RelationshipTo('trm_api.graph_models.win.WIN', 'RECOGNIZES_WIN')
    
    # What specific contribution is being recognized (Project, Task, Resource)
    # Tách thành các relationship riêng biệt thay vì dùng list
    recognizes_contribution_to_project = RelationshipTo(
        'trm_api.graph_models.project.Project',
        'RECOGNIZES_CONTRIBUTION_TO'
    )
    recognizes_contribution_to_task = RelationshipTo(
        'trm_api.graph_models.task.Task',
        'RECOGNIZES_CONTRIBUTION_TO'
    )
    recognizes_contribution_to_resource = RelationshipTo(
        'trm_api.graph_models.resource.Resource',
        'RECOGNIZES_CONTRIBUTION_TO'
    )
    
    # Event generated when this recognition is granted
    generates_event = RelationshipTo('trm_api.graph_models.event.Event', 'GENERATES_EVENT')

    def __str__(self):
        return f"Recognition: {self.name} ({self.uid})"
