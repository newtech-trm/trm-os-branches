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
    
    def create_project(self, project_data: ProjectCreate) -> Dict[str, Any]:
        """
        Creates a new project with extended properties.
        """
        project = self.project_repository.create_project(project_data)
        return project.model_dump() if project else None
    
    def get_project_by_id(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a project by its ID.
        """
        project = self.project_repository.get_project_by_uid(project_id)
        return project.model_dump() if project else None
    
    def get_all_projects(self) -> List[Dict[str, Any]]:
        """
        Retrieves all projects.
        """
        projects = self.project_repository.get_all_projects()
        return [project.model_dump() for project in projects]
    
    def get_paginated_projects(self, page: int = 1, page_size: int = 10) -> Tuple[List[Dict[str, Any]], PaginationMetadata]:
        """
        Retrieves a paginated list of projects.
        
        Returns a tuple of (projects_list, pagination_metadata)
        """
        projects, total_count, page_count = self.project_repository.get_paginated_projects(page, page_size)
        
        # Convert projects to dicts
        projects_list = [project.model_dump() for project in projects]
        
        # Create pagination metadata
        pagination = PaginationMetadata(
            page=page,
            page_size=page_size,
            total_count=total_count,
            page_count=page_count,
            has_next=page < page_count,
            has_previous=page > 1
        )
        
        return projects_list, pagination
    
    def update_project(self, project_id: str, project_data: ProjectUpdate) -> Optional[Dict[str, Any]]:
        """
        Updates a project by its ID, including extended properties.
        """
        project = self.project_repository.update_project(project_id, project_data)
        return project.model_dump() if project else None
    
    def delete_project(self, project_id: str) -> bool:
        """
        Deletes a project by its ID.
        """
        return self.project_repository.delete_project(project_id)
    
    def get_project_tasks(self, project_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves tasks associated with a project.
        """
        tasks = self.project_repository.get_project_tasks(project_id)
        if not tasks:
            return []
        
        return [task.model_dump() for task in tasks]
    
    def add_task_to_project(self, project_id: str, task_id: str) -> bool:
        """
        Associates a task with a project.
        """
        return self.project_repository.add_task_to_project(project_id, task_id)
    
    def remove_task_from_project(self, project_id: str, task_id: str) -> bool:
        """
        Removes the association of a task with a project.
        """
        return self.project_repository.remove_task_from_project(project_id, task_id)
    
    # --- Resource Management Methods ---
    
    def assign_resource_to_project(self, project_id: str, resource_id: str,
                                allocation_percentage: int = 100,
                                assignment_type: str = 'full',
                                expected_end_date = None,
                                assignment_status: str = 'active',
                                notes: str = None,
                                assigned_by: str = None) -> Optional[Dict[str, Any]]:
        """
        Establishes an ASSIGNED_TO_PROJECT relationship from a Resource to a Project
        with all required properties according to the TRM Ontology V3.2.
        """
        result = self.project_repository.assign_resource_to_project(
            project_id, resource_id, allocation_percentage, 
            assignment_type, expected_end_date,
            assignment_status, notes, assigned_by
        )
        
        if not result:
            return None
        
        project, resource = result
        return {
            "project": project.model_dump() if project else None,
            "resource": resource.model_dump() if resource else None,
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
    
    def get_project_resources(self, project_id: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieves all Resources that are assigned to a specific Project.
        """
        resources = self.project_repository.get_project_resources(project_id, skip, limit)
        if not resources:
            return []
        
        return [resource.model_dump() for resource in resources]
    
    def get_paginated_resources_by_project(self, project_id: str, 
                                           page: int = 1, page_size: int = 10) -> Tuple[List[Dict[str, Any]], PaginationMetadata]:
        """
        Retrieves a paginated list of resources that are assigned to a specific project.
        
        Returns a tuple of (resources_list, pagination_metadata)
        """
        resources, total_count, page_count = self.project_repository.get_paginated_resources_by_project(
            project_id, page, page_size)
        
        if not resources:
            return [], PaginationMetadata(
                page=page,
                page_size=page_size,
                total_count=0,
                page_count=0,
                has_next=False,
                has_previous=False
            )
        
        # Convert resources to dicts
        resources_list = [resource.model_dump() for resource in resources]
        
        # Create pagination metadata
        pagination = PaginationMetadata(
            page=page,
            page_size=page_size,
            total_count=total_count,
            page_count=page_count,
            has_next=page < page_count,
            has_previous=page > 1
        )
        
        return resources_list, pagination
    
    def get_project_resources_with_relationships(self, project_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves all Resources that are assigned to a specific Project,
        including the relationship properties according to the ontology V3.2.
        """
        return self.project_repository.get_project_resources_with_relationships(project_id)
    
    def update_resource_project_relationship(self, project_id: str, resource_id: str,
                                           allocation_percentage: int = None,
                                           expected_end_date = None,
                                           actual_end_date = None,
                                           assignment_type: str = None,
                                           assignment_status: str = None,
                                           notes: str = None) -> bool:
        """
        Updates the relationship properties between a Resource and a Project
        according to the TRM Ontology V3.2.
        """
        return self.project_repository.update_resource_project_relationship(
            project_id, resource_id, allocation_percentage, expected_end_date,
            actual_end_date, assignment_type, assignment_status, notes
        )
    
    def unassign_resource_from_project(self, project_id: str, resource_id: str) -> bool:
        """
        Removes the ASSIGNED_TO_PROJECT relationship between a Resource and a Project.
        """
        return self.project_repository.unassign_resource_from_project(project_id, resource_id)
    
    # --- Project Manager and Agent Methods ---
    
    def assign_manager_to_project(self, project_id: str, agent_id: str,
                                role: str = 'project_manager',
                                responsibility_level: str = 'primary',
                                appointed_at = None,
                                notes: str = None) -> Optional[Dict[str, Any]]:
        """
        Establishes a MANAGES_PROJECT relationship from an Agent to a Project
        according to the TRM Ontology V3.2.
        """
        result = self.project_repository.assign_manager_to_project(
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
    
    def get_project_managers(self, project_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves all Agents that manage a specific Project.
        """
        managers = self.project_repository.get_project_managers(project_id)
        if not managers:
            return []
        
        return [manager.model_dump() for manager in managers]
    
    def get_project_managers_with_relationships(self, project_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves all Agents that manage a specific Project,
        including the relationship properties according to the ontology V3.2.
        """
        return self.project_repository.get_project_managers_with_relationships(project_id)
    
    def update_manager_project_relationship(self, project_id: str, agent_id: str,
                                          role: str = None,
                                          responsibility_level: str = None,
                                          notes: str = None) -> bool:
        """
        Updates the relationship properties between an Agent and a Project
        according to the TRM Ontology V3.2.
        """
        return self.project_repository.update_manager_project_relationship(
            project_id, agent_id, role, responsibility_level, notes
        )
    
    def remove_manager_from_project(self, project_id: str, agent_id: str) -> bool:
        """
        Removes the MANAGES_PROJECT relationship between an Agent and a Project.
        """
        return self.project_repository.remove_manager_from_project(project_id, agent_id)
    
    # --- Subproject Methods ---
    
    def get_project_subprojects(self, project_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves all subprojects of a specific Project.
        """
        # Get the project
        project = self.project_repository.get_project_by_uid(project_id)
        if not project:
            return []
        
        # Get the project's child projects (if any)
        subprojects = list(project.child_projects.all())
        
        # Return the subprojects as dicts
        return [subproject.model_dump() for subproject in subprojects]
    
    def get_project_parent(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves the parent project of a specific Project, if any.
        """
        # Get the project
        project = self.project_repository.get_project_by_uid(project_id)
        if not project:
            return None
        
        # Get the project's parent projects (should be 0 or 1)
        parents = list(project.parent_project.all())
        if not parents:
            return None
        
        # Return the parent project as a dict
        return parents[0].model_dump()
