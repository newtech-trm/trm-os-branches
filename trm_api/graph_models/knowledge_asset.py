#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module định nghĩa KnowledgeAsset trong Ontology V3.2.
KnowledgeAsset là tài sản tri thức, bao gồm các dạng tri thức được mã hóa và lưu trữ.
"""

from typing import Optional, List, Dict, Any
from uuid import uuid4
from datetime import datetime

from neomodel import (
    StructuredNode, StringProperty, DateTimeProperty,
    UniqueIdProperty, RelationshipTo, RelationshipFrom,
    ArrayProperty, JSONProperty, BooleanProperty
)

from trm_api.graph_models.node_base import NodeBase


class KnowledgeAsset(NodeBase):
    """
    KnowledgeAsset là tài sản tri thức trong hệ thống TRM theo Ontology V3.2.
    Gồm các loại khác nhau như ConceptualFramework, Methodology, và các dạng tri thức khác.
    """
    
    # Thuộc tính cơ bản
    uid = UniqueIdProperty()
    name = StringProperty(required=True, index=True)
    description = StringProperty()
    url = StringProperty()
    created_at = DateTimeProperty(default=datetime.now)
    updated_at = DateTimeProperty(default=datetime.now)
    
    # Thuộc tính mở rộng theo Ontology V3.2
    asset_type = StringProperty(choices={
        'conceptual_framework': 'conceptual_framework', 
        'methodology': 'methodology', 
        'document': 'document',
        'article': 'article', 
        'video': 'video', 
        'audio': 'audio', 
        'course': 'course', 
        'other': 'other'
    })
    tags = ArrayProperty(StringProperty())
    status = StringProperty(choices={
        'draft': 'draft', 
        'published': 'published', 
        'archived': 'archived', 
        'deprecated': 'deprecated'
    }, default='draft')
    version = StringProperty()
    authors = ArrayProperty(StringProperty())
    access_level = StringProperty(choices={
        'public': 'public', 
        'private': 'private', 
        'restricted': 'restricted'
    }, default='private')
    metadata = JSONProperty()
    is_verified = BooleanProperty(default=False)
    
    # Relationships according to Ontology V3.2
    created_by = RelationshipFrom('trm_api.graph_models.agent.Agent', 'CREATES_KNOWLEDGE')
    used_by = RelationshipFrom('trm_api.graph_models.project.Project', 'USES_KNOWLEDGE')
    used_by_tasks = RelationshipFrom('trm_api.graph_models.task.Task', 'USES_KNOWLEDGE')
    related_to = RelationshipTo('KnowledgeAsset', 'RELATED_TO')
    generated_by_wins = RelationshipFrom('trm_api.graph_models.win.WIN', 'GENERATES_KNOWLEDGE')
    has_snippets = RelationshipTo('trm_api.graph_models.knowledge_snippet.KnowledgeSnippet', 'HAS_SNIPPET')
    
    @property
    def serialize(self) -> Dict[str, Any]:
        """
        Serialize KnowledgeAsset to dictionary representation.
        """
        return {
            'uid': self.uid,
            'name': self.name,
            'description': self.description,
            'url': self.url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'asset_type': self.asset_type,
            'tags': self.tags or [],
            'status': self.status,
            'version': self.version,
            'authors': self.authors or [],
            'access_level': self.access_level,
            'metadata': self.metadata or {},
            'is_verified': self.is_verified
        }


class KnowledgeSnippet(NodeBase):
    """
    KnowledgeSnippet là đoạn trích dẫn từ KnowledgeAsset, là đơn vị nhỏ hơn của tri thức.
    Cho phép tham chiếu đến phần cụ thể của tài sản tri thức.
    """
    uid = UniqueIdProperty()
    content = StringProperty(required=True)
    excerpt_from = StringProperty()  # Có thể là tên chương, mục, trang, phút...
    created_at = DateTimeProperty(default=datetime.now)
    tags = ArrayProperty(StringProperty())
    
    # Relationships
    part_of = RelationshipTo('KnowledgeAsset', 'PART_OF')
    referenced_by = RelationshipFrom('trm_api.graph_models.task.Task', 'REFERENCES_SNIPPET')
    
    @property
    def serialize(self) -> Dict[str, Any]:
        """
        Serialize KnowledgeSnippet to dictionary representation.
        """
        return {
            'uid': self.uid,
            'content': self.content,
            'excerpt_from': self.excerpt_from,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'tags': self.tags or []
        }
