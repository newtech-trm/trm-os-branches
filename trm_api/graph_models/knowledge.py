from neomodel import StringProperty, RelationshipFrom, RelationshipTo, ArrayProperty, JSONProperty, IntegerProperty
from .base import BaseNode
from trm_api.graph_models.custom_properties import Neo4jDateTimeProperty
from datetime import datetime

class KnowledgeSnippet(BaseNode):
    """
    Represents a KnowledgeSnippet in the TRM-OS ontology (Ontology V3.2).
    
    KnowledgeSnippet là đơn vị cơ bản của tri thức, được tạo ra từ các WIN,
    project hoặc task. Nó có thể được sử dụng để xây dựng KnowledgeAsset
    hoặc được tham khảo trực tiếp để giải quyết vấn đề.
    """
    # Core properties theo Ontology V3.2
    title = StringProperty(required=True, index=True)
    content = StringProperty(required=True)
    summary = StringProperty()
    status = StringProperty(choices={
        'draft': 'Draft',
        'reviewed': 'Reviewed',
        'approved': 'Approved',
        'published': 'Published',
        'archived': 'Archived'
    }, default='draft')
    
    # Extended properties
    tags = ArrayProperty(StringProperty(), default=list)
    domain = StringProperty(help_text="Lĩnh vực tri thức: tech, business, organization, etc.")
    importance = IntegerProperty(default=3, help_text="Mức độ quan trọng từ 1-5")
    confidence_level = IntegerProperty(default=3, help_text="Độ tin cậy từ 1-5")
    metadata = JSONProperty(default=dict, help_text="Metadata bổ sung về snippet")
    
    # Thời gian
    created_at = Neo4jDateTimeProperty(default_now=True)
    updated_at = Neo4jDateTimeProperty(default_now=True)
    
    # --- Relationships ---
    # KnowledgeSnippet được tạo ra từ WIN
    generated_from_win = RelationshipFrom('.win.WIN', 'GENERATES_KNOWLEDGE')
    
    # KnowledgeSnippet có thể được tạo ra từ Project
    generated_from_project = RelationshipFrom('.project.Project', 'GENERATES_KNOWLEDGE')
    
    # KnowledgeSnippet có thể được tạo ra từ Task
    generated_from_task = RelationshipFrom('.task.Task', 'GENERATES_KNOWLEDGE')
    
    # KnowledgeSnippet là một phần của KnowledgeAsset
    # part_of_asset = RelationshipTo('.knowledge_asset.KnowledgeAsset', 'IS_PART_OF')
    
    def __str__(self):
        return self.title
