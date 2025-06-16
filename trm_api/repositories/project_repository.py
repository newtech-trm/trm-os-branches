from typing import Optional, List, Tuple, Dict, Any
from neomodel import db
import uuid
from datetime import datetime
from trm_api.graph_models.project import Project as GraphProject
from trm_api.graph_models.tension import Tension as GraphTension
from trm_api.graph_models.task import Task as GraphTask
from trm_api.models.project import ProjectCreate, ProjectUpdate # This is the Pydantic model for API data

class ProjectRepository:
    def create_project(self, project_data: ProjectCreate) -> GraphProject:
        """
        Creates a new project.
        """
        project = GraphProject(
            title=project_data.title,
            description=project_data.description,
            status=project_data.status
        ).save()
        return project

    def get_project_by_uid(self, uid: str) -> Optional[GraphProject]:
        """
        Retrieves a project by its unique ID.
        """
        try:
            return GraphProject.nodes.get(uid=uid)
        except GraphProject.DoesNotExist:
            return None

    def list_projects(self, skip: int = 0, limit: int = 100) -> List[GraphProject]:
        """
        Retrieves a list of all projects with pagination.
        """
        return GraphProject.nodes.all()[skip:skip + limit]
        
    def get_paginated_projects(self, page: int = 1, page_size: int = 10) -> Tuple[List[GraphProject], int, int]:
        """
        Retrieves a paginated list of all projects.
        
        Args:
            page: The page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            Tuple of (projects, total_count, page_count)
        """
        from trm_api.repositories.pagination_helper import PaginationHelper
        
        return PaginationHelper.paginate_query(GraphProject.nodes, page, page_size)

    def update_project(self, uid: str, project_data: ProjectUpdate) -> Optional[GraphProject]:
        """
        Updates an existing project.
        """
        project = self.get_project_by_uid(uid)
        if not project:
            return None

        update_data = project_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(project, key, value)
        
        project.save()
        return project

    def delete_project(self, uid: str) -> bool:
        """
        Deletes a project by its unique ID.
        Returns True if deletion was successful, False otherwise.
        """
        project = self.get_project_by_uid(uid)
        if not project:
            return False
        
        project.delete()
        return True
        
    @db.transaction
    def add_tension_to_resolve(self, project_uid: str, tension_uid: str, 
                        resolution_status: str = 'Proposed',
                        resolution_approach: str = None,
                        expected_outcome: str = None,
                        alignment_score: float = None,
                        priority: str = 'Medium',
                        start_date = None,
                        target_resolution_date = None,
                        actual_resolution_date = None,
                        notes: str = None) -> Optional[Tuple[GraphProject, GraphTension]]:
        """
        Establishes a RESOLVES_TENSION relationship from a Project to a Tension
        with all required properties according to the TRM Ontology V3.2.
        
        Args:
            project_uid: UID of the project
            tension_uid: UID of the tension
            resolution_status: Status of the resolution (e.g. 'Proposed', 'ResolutionInProgress')
            resolution_approach: Description of the approach to resolve the tension
            expected_outcome: Expected outcome after tension resolution
            alignment_score: Score (0.0-1.0) evaluating how well the project fits for resolving this tension
            priority: Priority level ('Critical', 'High', 'Medium', 'Low', 'Informational')
            start_date: Date when project started resolving this tension
            target_resolution_date: Target date for tension resolution
            actual_resolution_date: Actual date when tension was resolved
            notes: Additional notes about this relationship
        
        Returns:
            Tuple of (project, tension) if successful, None otherwise
        """
        import uuid
        from datetime import datetime
        
        # 1. Get both the project and tension nodes
        project = self.get_project_by_uid(project_uid)
        if not project:
            return None
            
        try:
            tension = GraphTension.nodes.get(uid=tension_uid)
        except GraphTension.DoesNotExist:
            return None
        
        # 2. Create the RESOLVES_TENSION relationship with all properties
        relationship_props = {
            'relationshipId': str(uuid.uuid4()),
            'resolutionStatus': resolution_status,
            'creationDate': datetime.now(),
            'lastModifiedDate': datetime.now()
        }
        
        # Add optional properties if provided
        if resolution_approach:
            relationship_props['resolutionApproach'] = resolution_approach
        if expected_outcome:
            relationship_props['expectedOutcome'] = expected_outcome
        if alignment_score is not None:
            relationship_props['alignmentScore'] = alignment_score
        if priority:
            relationship_props['priority'] = priority
        if start_date:
            relationship_props['startDate'] = start_date
        if target_resolution_date:
            relationship_props['targetResolutionDate'] = target_resolution_date
        if actual_resolution_date:
            relationship_props['actualResolutionDate'] = actual_resolution_date
        if notes:
            relationship_props['notes'] = notes
        
        # Connect with relationship properties
        project.resolves_tensions.connect(tension, relationship_props)
        
        return (project, tension)
        
    def get_tensions_resolved_by_project(self, project_uid: str, skip: int = 0, limit: int = 100) -> List[GraphTension]:
        """
        Retrieves all Tensions that are being resolved by a specific Project.
        """
        project = self.get_project_by_uid(project_uid)
        if not project:
            return []
            
        # Get all tensions connected with RESOLVES_TENSION relationship
        return list(project.resolves_tensions.all()[skip:skip+limit])
        
    def get_paginated_tensions_by_project(self, project_uid: str, page: int = 1, page_size: int = 10) -> Tuple[List[GraphTension], int, int]:
        """
        Retrieves a paginated list of tensions that are resolved by a specific project.
        
        Args:
            project_uid: UID of the project
            page: The page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            Tuple of (tensions, total_count, page_count)
        """
        from trm_api.repositories.pagination_helper import PaginationHelper
        
        project = self.get_project_by_uid(project_uid)
        if not project:
            return [], 0, 0
            
        return PaginationHelper.paginate_relationship(project.resolves_tensions, page, page_size)
        
    @db.transaction
    def remove_tension_from_project(self, project_uid: str, tension_uid: str) -> bool:
        """
        Removes the RESOLVES_TENSION relationship between a Project and a Tension.
        
        Returns True if disconnection was successful, False otherwise.
        """
        # 1. Get both the project and tension nodes
        project = self.get_project_by_uid(project_uid)
        if not project:
            return False
            
        try:
            tension = GraphTension.nodes.get(uid=tension_uid)
        except GraphTension.DoesNotExist:
            return False
            
        # 2. Remove the relationship
        project.resolves_tensions.disconnect(tension)
        
        return True
        
    @db.transaction
    def add_task_to_project(self, project_uid: str, task_uid: str, 
                            task_order: int = 0,
                            is_required: bool = True,
                            criticality: int = 3,
                            depends_on: str = None,
                            milestone: str = None,
                            added_by: str = None,
                            notes: str = None) -> Optional[Tuple[GraphProject, GraphTask]]:
        """
        Establishes an IS_PART_OF_PROJECT (HAS_TASK) relationship from a Project to a Task
        with all required properties according to the TRM Ontology V3.2.
        
        Args:
            project_uid: UID of the project
            task_uid: UID of the task
            task_order: Order/position of the task in the project (0 = first)
            is_required: Whether task is required for project completion
            criticality: Criticality level (1-5)
                1: Critical
                2: High
                3: Medium
                4: Low
                5: Optional
            depends_on: UID of task that this task depends on
            milestone: Milestone this task contributes to
            added_by: UID of user who added this task to the project
            notes: Additional notes about this relationship
            
        Returns:
            Tuple of (project, task) if successful, None otherwise
        """
        # 1. Get both the project and task nodes
        project = self.get_project_by_uid(project_uid)
        if not project:
            return None
            
        try:
            task = GraphTask.nodes.get(uid=task_uid)
        except GraphTask.DoesNotExist:
            return None
        
        # 2. Create the IS_PART_OF_PROJECT relationship with all properties
        relationship_props = {
            'relationshipId': str(uuid.uuid4()),
            'taskOrder': task_order,
            'creationDate': datetime.now(),
            'lastModifiedDate': datetime.now(),
            'isRequired': is_required,
            'criticality': criticality
        }
        
        # Add optional properties if provided
        if depends_on:
            relationship_props['dependsOn'] = depends_on
        if milestone:
            relationship_props['milestone'] = milestone
        if added_by:
            relationship_props['addedBy'] = added_by
        if notes:
            relationship_props['notes'] = notes
        
        # Connect with relationship properties
        project.tasks.connect(task, relationship_props)
        
        return (project, task)
        
    def get_project_tasks(self, project_uid: str, skip: int = 0, limit: int = 100) -> List[GraphTask]:
        """
        Retrieves all Tasks that are part of a specific Project.
        
        Args:
            project_uid: UID of the project
            skip: Number of items to skip (pagination)
            limit: Maximum number of items to return (pagination)
            
        Returns:
            List of Task nodes
        """
        project = self.get_project_by_uid(project_uid)
        if not project:
            return []
            
        # Get all tasks connected with HAS_TASK relationship
        return list(project.tasks.all()[skip:skip+limit])
        
    def get_paginated_tasks_by_project(self, project_uid: str, page: int = 1, page_size: int = 10) -> Tuple[List[GraphTask], int, int]:
        """
        Retrieves a paginated list of tasks that are part of a specific project.
        
        Args:
            project_uid: UID of the project
            page: The page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            Tuple of (tasks, total_count, page_count)
        """
        from trm_api.repositories.pagination_helper import PaginationHelper
        
        project = self.get_project_by_uid(project_uid)
        if not project:
            return [], 0, 0
            
        return PaginationHelper.paginate_relationship(project.tasks, page, page_size)
        
    def get_project_tasks_with_relationships(self, project_uid: str) -> List[Dict[str, Any]]:
        """
        Retrieves all Tasks that are part of a specific Project,
        including the relationship properties according to the ontology V3.2.
        
        Args:
            project_uid: UID of the project
            
        Returns:
            List of dictionaries with task data and relationship properties
        """
        project = self.get_project_by_uid(project_uid)
        if not project:
            return []
            
        results = []
        # Get all task relationships
        relationships = project.tasks.all_relationships()
        
        for rel in relationships:
            # Get task node data
            task = rel.end_node()
            
            # Combine task data with relationship properties
            task_data = {
                'task': task.model_dump(),
                'relationship': {
                    'relationshipId': rel.relationshipId,
                    'taskOrder': rel.taskOrder,
                    'creationDate': rel.creationDate,
                    'lastModifiedDate': rel.lastModifiedDate,
                    'isRequired': rel.isRequired,
                    'criticality': rel.criticality,
                    'dependsOn': getattr(rel, 'dependsOn', None),
                    'milestone': getattr(rel, 'milestone', None),
                    'addedBy': getattr(rel, 'addedBy', None),
                    'notes': getattr(rel, 'notes', None)
                }
            }
            results.append(task_data)
        
        # Sort by taskOrder
        results.sort(key=lambda x: x['relationship']['taskOrder'])
        
        return results
        
    @db.transaction
    def update_task_project_relationship(self, project_uid: str, task_uid: str,
                                         task_order: int = None,
                                         is_required: bool = None,
                                         criticality: int = None,
                                         depends_on: str = None,
                                         milestone: str = None,
                                         notes: str = None) -> bool:
        """
        Updates the relationship properties between a Project and a Task
        according to the TRM Ontology V3.2.
        
        Returns True if update was successful, False otherwise.
        """
        # 1. Get both the project and task nodes
        project = self.get_project_by_uid(project_uid)
        if not project:
            return False
            
        try:
            task = GraphTask.nodes.get(uid=task_uid)
        except GraphTask.DoesNotExist:
            return False
            
        # Check if relationship exists
        if not project.tasks.is_connected(task):
            return False
            
        # 2. Get the relationship
        rel = project.tasks.relationship(task)
        
        # 3. Update the properties
        if task_order is not None:
            rel.taskOrder = task_order
        if is_required is not None:
            rel.isRequired = is_required
        if criticality is not None:
            rel.criticality = criticality
        if depends_on is not None:
            rel.dependsOn = depends_on
        if milestone is not None:
            rel.milestone = milestone
        if notes is not None:
            rel.notes = notes
            
        rel.lastModifiedDate = datetime.now()
        rel.save()
        
        return True
        
    @db.transaction
    def remove_task_from_project(self, project_uid: str, task_uid: str) -> bool:
        """
        Removes the IS_PART_OF_PROJECT relationship between a Project and a Task.
        
        Returns True if disconnection was successful, False otherwise.
        """
        # 1. Get both the project and task nodes
        project = self.get_project_by_uid(project_uid)
        if not project:
            return False
            
        try:
            task = GraphTask.nodes.get(uid=task_uid)
        except GraphTask.DoesNotExist:
            return False
            
        # 2. Remove the relationship
        project.tasks.disconnect(task)
        
        return True
