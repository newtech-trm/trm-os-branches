from typing import Optional, List, Dict, Any, Tuple
from neomodel import db

from trm_api.models.resource import (
    ResourceBase, ResourceType, 
    FinancialResourceCreate, KnowledgeResourceCreate,
    HumanResourceCreate, ToolResourceCreate, EquipmentResourceCreate,
    SpaceResourceCreate
)
from trm_api.graph_models.resource import Resource as GraphResource
from trm_api.graph_models.project import Project as GraphProject
from trm_api.graph_models.task import Task as GraphTask
from trm_api.repositories.pagination_helper import PaginationHelper

class ResourceRepository:
    """
    Repository for handling all database operations related to Resources.
    """

    @db.transaction
    def create_resource(self, resource_data: Dict[str, Any]) -> GraphResource:
        """
        Creates a new Resource node.
        """
        resource = GraphResource(**resource_data).save()
        return resource
    
    def create_typed_resource(self, resource_data: ResourceBase) -> GraphResource:
        """
        Creates a new Resource node with type-specific details.
        """
        # Convert Pydantic model to dictionary for graph model
        data = resource_data.model_dump(by_alias=True)
        
        # Extract details if they exist
        if hasattr(resource_data, 'details'):
            details = resource_data.details.model_dump(by_alias=True)
            data["details"] = details
        else:
            data["details"] = {}
            
        return self.create_resource(data)

    def get_resource_by_uid(self, uid: str) -> Optional[GraphResource]:
        """
        Retrieves a Resource node by its unique ID.
        """
        try:
            return GraphResource.nodes.get(uid=uid)
        except GraphResource.DoesNotExist:
            return None

    def list_resources(self, skip: int = 0, limit: int = 100, resource_type: Optional[str] = None) -> List[GraphResource]:
        """
        Lists all Resource nodes with optional type filtering and pagination.
        """
        if resource_type:
            return GraphResource.nodes.filter(resourceType=resource_type)[skip:skip+limit]
        else:
            return GraphResource.nodes.all()[skip:skip+limit]
    
    def get_paginated_resources(self, page: int = 1, page_size: int = 10, resource_type: Optional[str] = None) -> Tuple[List[GraphResource], int, int]:
        """
        Retrieves a paginated list of resources with optional type filtering.
        
        Args:
            page: The page number (1-indexed)
            page_size: Number of items per page
            resource_type: Optional filter by resource type
            
        Returns:
            Tuple of (resources, total_count, page_count)
        """
        if resource_type:
            node_set = GraphResource.nodes.filter(resourceType=resource_type)
        else:
            node_set = GraphResource.nodes.all()
            
        return PaginationHelper.paginate_query(node_set, page, page_size)

    def update_resource(self, uid: str, update_data: Dict[str, Any]) -> Optional[GraphResource]:
        """
        Updates an existing Resource node.
        """
        resource = self.get_resource_by_uid(uid)
        if not resource:
            return None

        # Handle details as a nested property if it exists
        if 'details' in update_data:
            details = update_data.pop('details')
            # Merge with existing details rather than replace
            existing_details = resource.details or {}
            existing_details.update(details)
            resource.details = existing_details

        # Update other fields
        for key, value in update_data.items():
            setattr(resource, key, value)
        
        resource.save()
        return resource

    def delete_resource(self, uid: str) -> bool:
        """
        Deletes a Resource node by its unique ID.
        """
        resource = self.get_resource_by_uid(uid)
        if not resource:
            return False
        
        resource.delete()
        return True
    
    @db.transaction
    def assign_resource_to_project(self, resource_uid: str, project_uid: str) -> Optional[GraphResource]:
        """
        Assigns a resource to a project, creating a HAS_RESOURCE relationship.
        """
        resource = self.get_resource_by_uid(resource_uid)
        if not resource:
            return None
        
        try:
            project = GraphProject.nodes.get(uid=project_uid)
        except GraphProject.DoesNotExist:
            return None
            
        project.resources.connect(resource)
        return resource
    
    @db.transaction
    def assign_resource_to_task(self, resource_uid: str, task_uid: str) -> Optional[GraphResource]:
        """
        Assigns a resource to a task, creating a USES_RESOURCE relationship.
        """
        resource = self.get_resource_by_uid(resource_uid)
        if not resource:
            return None
        
        try:
            task = GraphTask.nodes.get(uid=task_uid)
        except GraphTask.DoesNotExist:
            return None
            
        task.resources.connect(resource)
        return resource
    
    def list_project_resources(self, project_uid: str, skip: int = 0, limit: int = 100) -> List[GraphResource]:
        """
        Lists all resources assigned to a specific project.
        """
        try:
            project = GraphProject.nodes.get(uid=project_uid)
            return project.resources.all()[skip:skip+limit]
        except GraphProject.DoesNotExist:
            return []
    
    def get_paginated_project_resources(self, project_uid: str, page: int = 1, page_size: int = 10) -> Tuple[List[GraphResource], int, int]:
        """
        Retrieves a paginated list of resources assigned to a specific project.
        
        Args:
            project_uid: UID of the project
            page: The page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            Tuple of (resources, total_count, page_count)
        """
        try:
            project = GraphProject.nodes.get(uid=project_uid)
            return PaginationHelper.paginate_relationship(project.resources, page, page_size)
        except GraphProject.DoesNotExist:
            return [], 0, 0
    
    def list_task_resources(self, task_uid: str, skip: int = 0, limit: int = 100) -> List[GraphResource]:
        """
        Lists all resources used by a specific task.
        """
        try:
            task = GraphTask.nodes.get(uid=task_uid)
            return task.resources.all()[skip:skip+limit]
        except GraphTask.DoesNotExist:
            return []
            
    def get_paginated_task_resources(self, task_uid: str, page: int = 1, page_size: int = 10) -> Tuple[List[GraphResource], int, int]:
        """
        Retrieves a paginated list of resources used by a specific task.
        
        Args:
            task_uid: UID of the task
            page: The page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            Tuple of (resources, total_count, page_count)
        """
        try:
            task = GraphTask.nodes.get(uid=task_uid)
            return PaginationHelper.paginate_relationship(task.resources, page, page_size)
        except GraphTask.DoesNotExist:
            return [], 0, 0
