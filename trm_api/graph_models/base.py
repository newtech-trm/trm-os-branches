import uuid
from datetime import datetime, timezone
from neomodel import StructuredNode, StringProperty, DateTimeProperty, UniqueIdProperty

class BaseNode(StructuredNode):
    __abstract_node__ = True  # This makes it an abstract class, not a node in the DB

    uid = UniqueIdProperty() # neomodel's built-in UUID property
    created_at = DateTimeProperty(default_now=True)
    updated_at = DateTimeProperty(default_now=True)

    def pre_save(self):
        # Automatically update the 'updated_at' timestamp on every save
        self.updated_at = datetime.now(timezone.utc)
