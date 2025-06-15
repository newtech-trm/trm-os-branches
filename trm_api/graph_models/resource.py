from neomodel import (
    StructuredNode, StringProperty, UniqueIdProperty,
    DateTimeProperty, JSONProperty, RelationshipTo, RelationshipFrom
)
from datetime import datetime
import uuid

from trm_api.graph_models.base import BaseNode

class Resource(BaseNode):
    """
    Neo4j node representing a Resource in the system.
    Resources can be of different types: Financial, Knowledge, Human, Tool, Equipment, Space.
    """
    name = StringProperty(required=True)
    description = StringProperty()
    resourceType = StringProperty(required=True)
    status = StringProperty(default="available")
    ownerAgentId = StringProperty()
    details = JSONProperty(default={})

    # Relationships
    used_by_projects = RelationshipFrom('trm_api.graph_models.project.Project', 'HAS_RESOURCE')
    used_by_tasks = RelationshipFrom('trm_api.graph_models.task.Task', 'USES_RESOURCE')
    
    @classmethod
    def create(cls, **props):
        """
        Create a new Resource node with a generated resourceId.
        """
        # Set default values for required fields
        props.setdefault('uid', str(uuid.uuid4()))
        props.setdefault('createdAt', datetime.utcnow())
        props.setdefault('updatedAt', datetime.utcnow())

        return super(Resource, cls).create(**props)
