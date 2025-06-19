#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Project Service - Triển khai các dịch vụ nghiệp vụ cho Project
theo Ontology V3.2 với đầy đủ thuộc tính mở rộng và relationship.
"""

from typing import List, Optional, Any, Dict, Tuple
from datetime import datetime
from trm_api.models.project import ProjectCreate, ProjectUpdate, Project, ProjectDetail
from trm_api.repositories.project_repository import ProjectRepository
from trm_api.graph_models.project import Project as GraphProject
from trm_api.graph_models.resource import Resource as GraphResource
from trm_api.graph_models.agent import Agent as GraphAgent
# Import PaginationHelper cho phân trang
from trm_api.repositories.pagination_helper import PaginationHelper
# Import PaginationMetadata và PaginatedResponse từ models
from trm_api.models.pagination import PaginationMetadata, PaginatedResponse

class ProjectService:
    def __init__(self):
        self.project_repository = ProjectRepository()
    
    async def create_project(self, project_data: ProjectCreate) -> Dict[str, Any]:
        """
        Creates a new project with extended properties asynchronously.
        """
        project = await self.project_repository.create_project(project_data)
        return project.model_dump() if project else None
    
    async def get_project_by_id(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a project by its ID asynchronously.
        """
        project = await self.project_repository.get_project_by_id(project_id)
        return project.model_dump() if project else None
    
    async def get_all_projects(self) -> List[Dict[str, Any]]:
        """
        Retrieves all projects asynchronously.
        """
        projects = await self.project_repository.get_all_projects()
        return [project.model_dump() for project in projects]
    
    async def get_paginated_projects(self, page: int = 1, page_size: int = 10) -> Tuple[List[Dict[str, Any]], PaginationMetadata]:
        """
        Retrieves a paginated list of projects asynchronously.
        
        Returns a tuple of (projects_list, pagination_metadata)
        """
        projects, total_count, page_count = await self.project_repository.get_paginated_projects(page=page, page_size=page_size)
        
        # Convert graph models to API models
        api_projects = [project.model_dump() for project in projects]
        
        # Create pagination metadata
        pagination_meta = PaginationMetadata(
            total=total_count,
            page=page,
            page_size=page_size,
            pages=page_count
        )
        
        return api_projects, pagination_meta
    
    async def update_project(self, project_id: str, project_data: ProjectUpdate) -> Optional[Dict[str, Any]]:
        """
        Updates an existing project asynchronously.
        """
        project = await self.project_repository.update_project(project_id=project_id, project_data=project_data)
        return project.model_dump() if project else None
    
    async def delete_project(self, project_id: str) -> bool:
        """
        Deletes a project asynchronously.
        """
        return await self.project_repository.delete_project(project_id=project_id)
    
    async def get_project_tasks(self, project_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves tasks associated with a project asynchronously.
        """
        tasks = await self.project_repository.get_project_tasks(project_id)
        if not tasks:
            return []
        
        return [task.model_dump() for task in tasks]
    
    async def add_task_to_project(self, project_id: str, task_id: str) -> bool:
        """
        Associates a task with a project asynchronously.
        """
        return await self.project_repository.add_task_to_project(project_id, task_id)
    
    async def remove_task_from_project(self, project_id: str, task_id: str) -> bool:
        """
        Removes the association of a task with a project asynchronously.
        """
        return await self.project_repository.remove_task_from_project(project_id, task_id)
    
    # --- Resource Management Methods ---
    
    async def assign_resource_to_project(self, project_id: str, resource_id: str,
                                  allocation_percentage: int = 100,
                                  assignment_type: str = "full",
                                  expected_end_date: Optional[str] = None,
                                  assignment_status: str = "active",
                                  notes: Optional[str] = None,
                                  assigned_by: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Assigns a Resource to a Project with relationship properties asynchronously.
        """
        result = await self.project_repository.assign_resource_to_project(
            project_uid=project_id,
            resource_uid=resource_id,
            allocation_percentage=allocation_percentage,
            assignment_type=assignment_type,
            expected_end_date=expected_end_date,
            assignment_status=assignment_status,
            notes=notes,
            assigned_by=assigned_by
        )
        
        if not result:
            return None
            
        project, resource = result
        return {
            "project": project.model_dump(),
            "resource": resource.model_dump(),
            "relationship": {
                "allocation_percentage": allocation_percentage,
                "assignment_type": assignment_type,
                "assignment_status": assignment_status,
                "assigned_at": datetime.now().isoformat(),
                "expected_end_date": expected_end_date,
                "notes": notes,
                "assigned_by": assigned_by
            }
        }
    
    async def get_project_resources(self, project_id: str, page: int = 1, page_size: int = 10) -> Tuple[List[Dict[str, Any]], PaginationMetadata]:
        """
        Retrieves paginated list of resources assigned to a specific project asynchronously.
        """
        resources, total_count, page_count = await self.project_repository.get_paginated_resources_by_project(project_id, page, page_size)
        
        # Convert resources to dicts
        resources_list = [resource.model_dump() for resource in resources]
        
        # Create pagination metadata
        pagination = PaginationMetadata(
            page=page,
            page_size=page_size,
            total=total_count,
            pages=page_count
        )
        
        return resources_list, pagination
    
    async def get_project_resources_with_relationships(self, project_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves resources assigned to a project including the relationship properties asynchronously.
        """
        results = await self.project_repository.get_resources_with_relationship_properties(project_id)
        
        if not results:
            return []
            
        return [{
            "resource": resource.model_dump(),
            "relationship": relationship_props
        } for resource, relationship_props in results]
    
    async def update_resource_project_relationship(self, project_id: str, resource_id: str, **relationship_props) -> Optional[Dict[str, Any]]:
        """
        Updates the properties of the ASSIGNED_TO_PROJECT relationship between a Resource and a Project asynchronously.
        """
        result = await self.project_repository.update_resource_project_relationship(project_id, resource_id, **relationship_props)
        
        if not result:
            return None
            
        resource, updated_props = result
        return {
            "resource": resource.model_dump(),
            "relationship": updated_props
        }
    
    async def unassign_resource_from_project(self, project_id: str, resource_id: str) -> bool:
        """
        Removes the ASSIGNED_TO_PROJECT relationship between a Resource and a Project asynchronously.
        """
        return await self.project_repository.unassign_resource_from_project(project_id, resource_id)
    
    # --- Project Manager and Agent Methods ---
    
    async def assign_manager_to_project(self, project_id: str, agent_id: str,
                                role: str = 'project_manager',
                                responsibility_level: str = 'primary',
                                appointed_at = None,
                                notes: str = None) -> Optional[Dict[str, Any]]:
        """
        Establishes a MANAGES_PROJECT relationship from an Agent to a Project
        according to the TRM Ontology V3.2 asynchronously.
        """
        result = await self.project_repository.assign_manager_to_project(
            project_id, agent_id, role, responsibility_level, appointed_at, notes
        )
        
        if not result:
            return None
        
        project, agent = result
        return {
            "project": project.model_dump() if project else None,
            "agent": agent.model_dump() if agent else None,
            "relationship": {
                "role": role,
                "responsibility_level": responsibility_level,
                "appointed_at": (appointed_at or datetime.now()).isoformat(),
                "notes": notes
            }
        }
    
    async def get_project_managers(self, project_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves all Agents that manage a specific Project asynchronously.
        """
        managers = await self.project_repository.get_project_managers(project_id)
        if not managers:
            return []
        
        return [manager.model_dump() for manager in managers]
    
    async def get_project_managers_with_relationships(self, project_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves all Agents that manage a specific Project,
        including the relationship properties according to the ontology V3.2 asynchronously.
        """
        results = await self.project_repository.get_agents_with_relationship_properties(project_id)
        
        if not results:
            return []
            
        return [{
            "agent": agent.model_dump(),
            "relationship": relationship_props
        } for agent, relationship_props in results]
    
    async def update_manager_project_relationship(self, project_id: str, agent_id: str,
                                          role: Optional[str] = None,
                                          responsibility_level: Optional[str] = None,
                                          notes: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Updates the relationship properties between an Agent and a Project
        according to the TRM Ontology V3.2 asynchronously.
        """
        result = await self.project_repository.update_manager_project_relationship(
            project_id, agent_id, role, responsibility_level, notes
        )
        
        if not result:
            return None
            
        agent, updated_props = result
        return {
            "agent": agent.model_dump(),
            "relationship": updated_props
        }
    
    async def remove_manager_from_project(self, project_id: str, agent_id: str) -> bool:
        """
        Removes the MANAGES_PROJECT relationship between an Agent and a Project asynchronously.
        """
        return await self.project_repository.remove_manager_from_project(project_id, agent_id)
    
    # --- Subproject Methods ---
    
    async def get_parent_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves the parent project of a given project asynchronously, if any.
        """
        # Get the project
        project = await self.project_repository.get_project_by_id(project_id)
        if not project:
            return None
        
        # Get the parent project if exists
        parent_projects = list(project.parent_project.all())
        if not parent_projects:
            return None
            
        return parent_projects[0].model_dump()
    
    async def get_subprojects(self, project_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves all subprojects of a given project asynchronously.
        """
        # Get the project
        project = await self.project_repository.get_project_by_id(project_id)
        if not project:
            return []
        
        # Get the project's child projects (if any)
        subprojects = list(project.child_projects.all())
        
        # Return the subprojects as dicts
        return [subproject.model_dump() for subproject in subprojects]
    
    async def add_subproject(self, parent_id: str, child_id: str) -> bool:
        """
        Adds a subproject to a project asynchronously.
        """
        return await self.project_repository.add_subproject(parent_id, child_id)
    
    async def remove_parent_child_relationship(self, parent_id: str, child_id: str) -> bool:
        """
        Removes a parent-child relationship between two projects asynchronously.
        """
        return await self.project_repository.remove_parent_child_relationship(parent_id, child_id)
    
    async def get_project_subprojects(self, project_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves all subprojects of a specific Project asynchronously.
        """
        # Get the project
        project = await self.project_repository.get_project_by_id(project_id)
        if not project:
            return []
        
        # Get the project's child projects (if any)
        subprojects = list(project.child_projects.all())
        
        # Return the subprojects as dicts
        return [subproject.model_dump() for subproject in subprojects]
    
    async def get_project_parent(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves the parent project of a specific Project asynchronously, if any.
        """
        # Get the project
        project = await self.project_repository.get_project_by_id(project_id)
        if not project:
            return None
        
        # Get the parent project if exists
        parent_projects = list(project.parent_project.all())
        if not parent_projects:
            return None
            
        return parent_projects[0].model_dump()
