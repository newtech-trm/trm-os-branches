#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module định nghĩa lớp cơ sở NodeBase cho tất cả các node trong Neo4j.
Lớp này cung cấp các phương thức và thuộc tính chung cho tất cả các node.
"""

from typing import Dict, Any, List, Optional, Union
from neomodel import StructuredNode


class NodeBase(StructuredNode):
    """
    Lớp cơ sở cho tất cả các node trong Neo4j.
    Cung cấp các phương thức và thuộc tính chung.
    """
    
    __abstract__ = True  # Đánh dấu lớp này là abstract, không tạo node trực tiếp
    
    @property
    def serialize(self) -> Dict[str, Any]:
        """
        Phương thức cơ bản để serialize một node thành dictionary.
        Các lớp con sẽ override phương thức này để thêm các trường cụ thể.
        
        Returns:
            Dict[str, Any]: Dictionary chứa dữ liệu của node.
        """
        return {}
    
    @classmethod
    def get_by_uid(cls, uid: str) -> Optional['NodeBase']:
        """
        Lấy node theo UID.
        
        Args:
            uid: Unique identifier của node.
            
        Returns:
            Optional[NodeBase]: Node nếu tìm thấy, None nếu không tìm thấy.
        """
        try:
            return cls.nodes.get(uid=uid)
        except (cls.DoesNotExist, ValueError):
            return None
    
    @classmethod
    def get_all(cls, skip: int = 0, limit: Optional[int] = None) -> List['NodeBase']:
        """
        Lấy tất cả các node của một loại, hỗ trợ phân trang.
        
        Args:
            skip: Số node bỏ qua (cho phân trang).
            limit: Số node tối đa trả về (cho phân trang).
            
        Returns:
            List[NodeBase]: Danh sách các node.
        """
        query = cls.nodes
        
        if skip:
            query = query.skip(skip)
        
        if limit is not None:
            query = query.limit(limit)
            
        return list(query.all())
    
    @classmethod
    def count(cls) -> int:
        """
        Đếm số lượng node của một loại.
        
        Returns:
            int: Số lượng node.
        """
        return len(cls.nodes.all())
    
    def update(self, props: Dict[str, Any]) -> 'NodeBase':
        """
        Cập nhật các thuộc tính của node.
        
        Args:
            props: Dictionary chứa các thuộc tính cần cập nhật.
            
        Returns:
            NodeBase: Node sau khi cập nhật.
        """
        for key, value in props.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        self.save()
        return self
    
    def add_relationship(self, target: 'NodeBase', rel_type: str, 
                        rel_props: Optional[Dict[str, Any]] = None) -> Any:
        """
        Thêm mối quan hệ từ node này đến node đích.
        
        Args:
            target: Node đích của mối quan hệ.
            rel_type: Loại mối quan hệ.
            rel_props: Thuộc tính của mối quan hệ (optional).
            
        Returns:
            Any: Kết quả của việc tạo mối quan hệ.
        """
        if not hasattr(self, rel_type):
            raise AttributeError(f"Node {self.__class__.__name__} không có relationship {rel_type}")
        
        relationship = getattr(self, rel_type)
        
        if rel_props:
            return relationship.connect(target, rel_props)
        else:
            return relationship.connect(target)
    
    def remove_relationship(self, target: 'NodeBase', rel_type: str) -> None:
        """
        Xóa mối quan hệ từ node này đến node đích.
        
        Args:
            target: Node đích của mối quan hệ.
            rel_type: Loại mối quan hệ.
        """
        if not hasattr(self, rel_type):
            raise AttributeError(f"Node {self.__class__.__name__} không có relationship {rel_type}")
        
        relationship = getattr(self, rel_type)
        relationship.disconnect(target)
    
    def get_related_nodes(self, rel_type: str) -> List[Union['NodeBase', Dict[str, Any]]]:
        """
        Lấy danh sách các node có liên quan thông qua một loại mối quan hệ cụ thể.
        
        Args:
            rel_type: Loại mối quan hệ.
            
        Returns:
            List[Union[NodeBase, Dict[str, Any]]]: Danh sách các node liên quan.
        """
        if not hasattr(self, rel_type):
            raise AttributeError(f"Node {self.__class__.__name__} không có relationship {rel_type}")
        
        relationship = getattr(self, rel_type)
        return list(relationship.all())
