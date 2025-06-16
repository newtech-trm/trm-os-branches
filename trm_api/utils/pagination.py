"""
Pagination utility functions.
This module re-exports calculation functions from pagination_helper for backward compatibility.
"""
from typing import Any, List, Tuple, Dict

def calculate_pagination(page: int, page_size: int, total_count: int) -> Dict[str, Any]:
    """
    Calculate pagination metadata
    
    Args:
        page: Current page number (1-indexed)
        page_size: Number of items per page
        total_count: Total number of items
        
    Returns:
        Dictionary with pagination metadata
    """
    # Normalize inputs
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 10
        
    # Calculate total pages
    page_count = (total_count + page_size - 1) // page_size if page_size > 0 else 1
    
    # Calculate has_next and has_previous
    has_next = page < page_count
    has_previous = page > 1
    
    return {
        "total_count": total_count,
        "page": page,
        "page_size": page_size,
        "page_count": page_count,
        "has_next": has_next,
        "has_previous": has_previous
    }
