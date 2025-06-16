from typing import TypeVar, List, Tuple, Optional, Any, Dict, Generic
from neomodel import StructuredNode, db

T = TypeVar('T', bound=StructuredNode)

class PaginationHelper:
    """
    Utility class to help with pagination in repositories
    """
    
    @staticmethod
    def paginate_query(node_set: Any, page: int = 1, page_size: int = 10) -> Tuple[List[T], int, int]:
        """
        Paginate a node set query and return items with count
        
        Args:
            node_set: A NodeSet query that can be sliced
            page: The page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            Tuple of (items, total_count, page_count)
        """
        # Validate page and page_size
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 10
            
        # Calculate skip value (0-indexed)
        skip = (page - 1) * page_size
        
        # Count total items
        total_count = len(node_set)
        
        # Get paginated items
        items = node_set[skip:skip + page_size]
        
        # Calculate page count
        page_count = (total_count + page_size - 1) // page_size if page_size > 0 else 1
        
        return list(items), total_count, page_count
    
    @staticmethod
    def paginate_relationship(relationship: Any, page: int = 1, page_size: int = 10) -> Tuple[List[T], int, int]:
        """
        Paginate a relationship query and return items with count
        
        Args:
            relationship: A Relationship query that can be sliced
            page: The page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            Tuple of (items, total_count, page_count)
        """
        # Similar to paginate_query but for relationship objects
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 10
            
        skip = (page - 1) * page_size
        
        # Count total items efficiently
        total_count = len(relationship.all())
        
        # Get items for this page
        items = list(relationship.all()[skip:skip + page_size])
        
        # Calculate page count
        page_count = (total_count + page_size - 1) // page_size if page_size > 0 else 1
        
        return items, total_count, page_count
        
    @staticmethod
    def get_count_by_label(label: str) -> int:
        """
        Get the count of nodes with a specific label
        
        Args:
            label: The node label to count
            
        Returns:
            Count of nodes
        """
        query = f"MATCH (n:{label}) RETURN count(n) as count"
        results, meta = db.cypher_query(query, {})
        return results[0][0] if results else 0
