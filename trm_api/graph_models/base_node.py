import uuid
from neomodel import StructuredNode, DateTimeProperty, UniqueIdProperty
from datetime import datetime, timezone

class BaseNode(StructuredNode):
    __abstract_node__ = True  # Đánh dấu đây là một lớp trừu tượng, không tạo node riêng trong DB

    uid = UniqueIdProperty()
    created_date = DateTimeProperty(default_now=True)
    last_modified_date = DateTimeProperty(default_now=True)

    def pre_save(self):
        self.last_modified_date = datetime.now(timezone.utc)

    # If you have a common way to convert to dictionary that includes uid
    # you might add it here, though process_record in utils.py handles this for API responses.
    # def to_dict(self):
    #     data = self.__properties__.copy()
    #     data['uid'] = self.uid # Ensure uid is always present
    #     # Convert datetime objects to ISO format string if needed for other purposes
    #     for key, value in data.items():
    #         if isinstance(value, datetime):
    #             data[key] = value.isoformat()
    #     return data
