from neomodel import (
    StructuredNode, StringProperty, UniqueIdProperty,
    DateTimeProperty, ArrayProperty, RelationshipFrom, RelationshipTo
)
from datetime import datetime
import uuid

from trm_api.graph_models.base_node import BaseNode

class Recognition(BaseNode):
    """
    Neo4j node representing a Recognition in the system.
    Recognitions are typically given to acknowledge a WIN or contribution.
    """
    winId = StringProperty(required=True, index=True)
    granterUserId = StringProperty(required=True, index=True)  # ID of user giving the recognition
    recipientUserIds = ArrayProperty(StringProperty(), required=True)  # IDs of users receiving the recognition
    message = StringProperty(required=True)
    recognitionType = StringProperty(default="Gratitude")  # e.g., 'Gratitude', 'Impact', 'Innovation'
    
    # Relationships
    given_by = RelationshipFrom('trm_api.graph_models.user.User', 'GIVES_RECOGNITION')
    received_by = RelationshipTo('trm_api.graph_models.user.User', 'RECEIVES_RECOGNITION')
    recognizes_win = RelationshipTo('trm_api.graph_models.win.WIN', 'RECOGNIZES')
    
    @classmethod
    def create(cls, **props):
        """Create a new Recognition node with a generated recognitionId."""
        # Set default values for required fields
        props.setdefault('uid', str(uuid.uuid4()))
        props.setdefault('createdAt', datetime.utcnow())
        
        return super(Recognition, cls).create(**props)
