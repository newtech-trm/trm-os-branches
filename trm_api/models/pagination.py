from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel, Field

T = TypeVar('T')

class PaginationMetadata(BaseModel):
    """Metadata for pagination results"""
    total_count: int = Field(..., description="Total number of items available")
    page_count: int = Field(..., description="Total number of pages available")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_previous: bool = Field(..., description="Whether there is a previous page")
    next_page: Optional[int] = Field(None, description="Next page number, if available")
    previous_page: Optional[int] = Field(None, description="Previous page number, if available")

class PaginatedResponse(BaseModel, Generic[T]):
    """Standard response format for paginated data"""
    items: List[T] = Field(..., description="List of items in the current page")
    metadata: PaginationMetadata = Field(..., description="Pagination metadata")

    @classmethod
    def create(cls, items: List[T], total_count: int, page: int, page_size: int) -> "PaginatedResponse[T]":
        """
        Helper function to create a paginated response
        
        Args:
            items: The list of items for the current page
            total_count: The total number of items across all pages
            page: The current page number (1-indexed)
            page_size: The number of items per page
        """
        # Calculate page count
        page_count = (total_count + page_size - 1) // page_size if page_size > 0 else 1
        
        # Check if there's a next or previous page
        has_next_page = page < page_count
        has_previous_page = page > 1
        
        # Calculate next and previous page numbers if they exist
        next_page = page + 1 if has_next_page else None
        previous_page = page - 1 if has_previous_page else None
        
        # Create metadata
        metadata = PaginationMetadata(
            total_count=total_count,
            page_count=page_count,
            page=page,
            page_size=page_size,
            has_next=has_next_page,
            has_previous=has_previous_page,
            next_page=next_page,
            previous_page=previous_page
        )
        
        return cls(items=items, metadata=metadata)
