from typing import Optional, List, Tuple, Dict, Any
from neomodel import db
from datetime import datetime
import uuid
import math

from trm_api.models.task import TaskCreate, TaskUpdate
from trm_api.graph_models.task import Task as GraphTask
from trm_api.graph_models.project import Project as GraphProject
from trm_api.graph_models.user import User as GraphUser
from trm_api.graph_models.agent import Agent as GraphAgent
from trm_api.utils.pagination import calculate_pagination

class TaskRepository:
    """
    Repository for handling all database operations related to Tasks.
    This repository follows the new project-centric architecture.
    """

    @db.transaction
    def create_task(self, task_data: TaskCreate) -> Optional[GraphTask]:
        """
        Creates a new Task and connects it to a parent Project according to Ontology V3.2.

        This operation is transactional. If any step fails, the entire
        operation is rolled back.
        """
        # 1. Find the parent project for this task.
        try:
            project = GraphProject.nodes.get(uid=task_data.project_id)
        except GraphProject.DoesNotExist:
            # Can't create a task for a non-existent project.
            return None

        # 2. Create the new task node.
        # Convert Pydantic model to dict and handle special mappings
        task_properties = task_data.model_dump(exclude={'project_id'})
        
        # Map from schema fields to graph model fields if names differ
        if 'effort_estimate' in task_properties and task_properties['effort_estimate'] is not None:
            task_properties['effort_estimate'] = task_properties.get('effort_estimate')
        
        # Ensure creation and last modified dates are set
        task_properties['creation_date'] = datetime.now()
        task_properties['last_modified_date'] = datetime.now()
        
        # Create and save the new task with all properties
        new_task = GraphTask(**task_properties).save()

        # 3. Create the relationship from Project to the new Task with metadata
        #    The IsPartOfProjectRel model requires a 'relationshipId'.
        relationship_props = {
            'relationshipId': str(uuid.uuid4()),
            'creationDate': datetime.now(),
            'lastModifiedDate': datetime.now()
        }
        project.tasks.connect(new_task, relationship_props)

        return new_task

    def get_task_by_uid(self, uid: str) -> Optional[GraphTask]:
        """
        Retrieves a Task node by its unique ID.
        """
        try:
            return GraphTask.nodes.get(uid=uid)
        except GraphTask.DoesNotExist:
            return None

    def list_tasks_for_project(self, project_id: str, skip: int = 0, limit: int = 100) -> List[GraphTask]:
        """
        Lists all tasks that belong to a specific project.
        """
        try:
            project = GraphProject.nodes.get(uid=project_id)
            # The relationship from Project to Task is 'tasks'
            tasks = project.tasks.all()
            return tasks[skip:skip+limit]
        except GraphProject.DoesNotExist:
            return []
            
    def get_paginated_tasks_for_project(self, project_id: str, page: int = 1, page_size: int = 10) -> Tuple[List[GraphTask], int, int]:
        """
        Gets paginated tasks for a specific project with total count and page count.
        
        Args:
            project_id: ID of the project to get tasks for
            page: Page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            Tuple of (tasks, total_count, page_count)
        """
        try:
            # Get the project
            project = GraphProject.nodes.get(uid=project_id)
            
            # Get all tasks for this project
            all_tasks = list(project.tasks.all())
            
            # Calculate pagination
            total_count = len(all_tasks)
            page_count = math.ceil(total_count / page_size) if total_count > 0 else 1
            
            # Calculate offset using the page and page_size
            offset = (page - 1) * page_size
            
            # Return paginated result
            paginated_tasks = all_tasks[offset:offset + page_size]
            
            return paginated_tasks, total_count, page_count
            
        except GraphProject.DoesNotExist:
            return [], 0, 0

    def update_task(self, uid: str, task_data: TaskUpdate) -> Optional[GraphTask]:
        """
        Updates an existing task with attributes from Ontology V3.2.
        """
        task = self.get_task_by_uid(uid)
        if not task:
            return None

        # Use exclude_unset=True to only update fields that were provided
        update_data = task_data.model_dump(exclude_unset=True)
        
        # Map any fields with different names between schema and graph model
        # Currently all fields have the same names, but this is where we'd handle any differences
        
        # Always update the last_modified_date when a task is modified
        update_data['last_modified_date'] = datetime.now()
        
        # Update the task object with all provided fields
        for key, value in update_data.items():
            setattr(task, key, value)
        
        # Save the updated task
        task.save()
        return task

    def delete_task(self, uid: str) -> bool:
        """
        Deletes a task by its unique ID.
        """
        task = self.get_task_by_uid(uid)
        if not task:
            return False
        
        task.delete()
        return True
        
    @db.transaction
    def assign_task_to_user(self, task_uid: str, user_uid: str,
                         assignment_type: str = 'Primary',
                         priority_level: int = 3,
                         estimated_effort: float = None,
                         assigned_by: str = None,
                         notes: str = None) -> Optional[Tuple[GraphTask, GraphUser]]:
        """
        Establishes an ASSIGNS_TASK relationship from a User to a Task
        with all required properties according to the TRM Ontology V3.2.
        
        Args:
            task_uid: UID of the task
            user_uid: UID of the user
            assignment_type: Type of assignment ('Primary', 'Supporting', 'Reviewer', 'Observer')
            priority_level: Priority level (1-5)
                1: Critical
                2: High
                3: Medium
                4: Low
                5: Optional
            estimated_effort: Estimated hours needed
            assigned_by: UID of user who made the assignment
            notes: Additional notes about this relationship
            
        Returns:
            Tuple of (task, user) if successful, None otherwise
        """
        # 1. Get both the task and user nodes
        task = self.get_task_by_uid(task_uid)
        if not task:
            return None
            
        try:
            user = GraphUser.nodes.get(uid=user_uid)
        except GraphUser.DoesNotExist:
            return None
        
        # 2. Create the ASSIGNS_TASK relationship with all required properties
        relationship_props = {
            'relationshipId': str(uuid.uuid4()),
            'creationDate': datetime.now(),
            'lastModifiedDate': datetime.now(),
            'assignmentType': assignment_type,
            'priorityLevel': priority_level,
            'assignmentDate': datetime.now(),
            'isAccepted': False
        }
        
        # Add optional properties if provided
        if estimated_effort is not None:
            relationship_props['estimatedEffort'] = estimated_effort
        if assigned_by:
            relationship_props['assignedBy'] = assigned_by
        if notes:
            relationship_props['notes'] = notes
        
        # Connect with relationship properties (User -> Task)
        user.assigned_tasks.connect(task, relationship_props)
        
        return (task, user)
    
    @db.transaction
    def assign_task_to_agent(self, task_uid: str, agent_uid: str,
                          assignment_type: str = 'Primary',
                          priority_level: int = 3,
                          estimated_effort: float = None,
                          assigned_by: str = None,
                          notes: str = None) -> Optional[Tuple[GraphTask, GraphAgent]]:
        """
        Establishes an ASSIGNS_TASK relationship from an Agent to a Task
        with all required properties according to the TRM Ontology V3.2.
        
        Args:
            task_uid: UID of the task
            agent_uid: UID of the agent
            assignment_type: Type of assignment ('Primary', 'Supporting', 'Reviewer', 'Observer')
            priority_level: Priority level (1-5)
                1: Critical
                2: High
                3: Medium
                4: Low
                5: Optional
            estimated_effort: Estimated hours needed
            assigned_by: UID of user who made the assignment
            notes: Additional notes about this relationship
            
        Returns:
            Tuple of (task, agent) if successful, None otherwise
        """
        # 1. Get both the task and agent nodes
        task = self.get_task_by_uid(task_uid)
        if not task:
            return None
            
        try:
            agent = GraphAgent.nodes.get(uid=agent_uid)
        except GraphAgent.DoesNotExist:
            return None
        
        # 2. Create the ASSIGNS_TASK relationship with all required properties
        relationship_props = {
            'relationshipId': str(uuid.uuid4()),
            'creationDate': datetime.now(),
            'lastModifiedDate': datetime.now(),
            'assignmentType': assignment_type,
            'priorityLevel': priority_level,
            'assignmentDate': datetime.now(),
            'isAccepted': False
        }
        
        # Add optional properties if provided
        if estimated_effort is not None:
            relationship_props['estimatedEffort'] = estimated_effort
        if assigned_by:
            relationship_props['assignedBy'] = assigned_by
        if notes:
            relationship_props['notes'] = notes
        
        # Connect with relationship properties
        agent.assigned_tasks.connect(task, relationship_props)
        
        return (task, agent)
    
    def get_task_assignees(self, task_uid: str) -> Dict[str, List]:
        """
        Retrieves all users and agents assigned to a specific task.
        
        Returns:
            Dictionary with keys 'users', 'agents' and corresponding lists of entities.
        """
        task = self.get_task_by_uid(task_uid)
        if not task:
            return {'users': [], 'agents': []}
            
        # Get all assigned users
        users = list(task.assignees_users.all())
        
        # Get all assigned agents
        agents = list(task.assignees_agents.all())
        
        return {
            'users': users,
            'agents': agents
        }
    
    def get_task_assignees_with_relationships(self, task_uid: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Retrieves all users and agents assigned to a specific task,
        including the relationship properties according to the ontology V3.2.
        
        Returns:
            Dictionary with keys 'users', 'agents' and corresponding lists of dictionaries 
            that contain entity data and relationship properties.
        """
        task = self.get_task_by_uid(task_uid)
        if not task:
            return {'users': [], 'agents': []}
            
        user_results = []
        agent_results = []
        
        # Get all user relationships
        user_relationships = task.assignees_users.all_relationships()
        
        for rel in user_relationships:
            # Get user node data
            user = rel.start_node()
            
            # Combine user data with relationship properties
            user_data = {
                'user': user.model_dump(),
                'relationship': {
                    'relationshipId': rel.relationshipId,
                    'assignmentType': rel.assignmentType,
                    'priorityLevel': rel.priorityLevel,
                    'creationDate': rel.creationDate,
                    'lastModifiedDate': rel.lastModifiedDate,
                    'assignmentDate': rel.assignmentDate,
                    'isAccepted': rel.isAccepted,
                    'estimatedEffort': getattr(rel, 'estimatedEffort', None),
                    'actualEffort': getattr(rel, 'actualEffort', None),
                    'assignedBy': getattr(rel, 'assignedBy', None),
                    'acceptanceDate': getattr(rel, 'acceptanceDate', None),
                    'completionDate': getattr(rel, 'completionDate', None),
                    'acceptance_notes': getattr(rel, 'acceptance_notes', None),
                    'notes': getattr(rel, 'notes', None)
                }
            }
            user_results.append(user_data)
        
        # Get all agent relationships
        agent_relationships = task.assignees_agents.all_relationships()
        
        for rel in agent_relationships:
            # Get agent node data
            agent = rel.start_node()
            
            # Combine agent data with relationship properties
            agent_data = {
                'agent': agent.model_dump(),
                'relationship': {
                    'relationshipId': rel.relationshipId,
                    'assignmentType': rel.assignmentType,
                    'priorityLevel': rel.priorityLevel,
                    'creationDate': rel.creationDate,
                    'lastModifiedDate': rel.lastModifiedDate,
                    'assignmentDate': rel.assignmentDate,
                    'isAccepted': rel.isAccepted,
                    'estimatedEffort': getattr(rel, 'estimatedEffort', None),
                    'actualEffort': getattr(rel, 'actualEffort', None),
                    'assignedBy': getattr(rel, 'assignedBy', None),
                    'acceptanceDate': getattr(rel, 'acceptanceDate', None),
                    'completionDate': getattr(rel, 'completionDate', None),
                    'acceptance_notes': getattr(rel, 'acceptance_notes', None),
                    'notes': getattr(rel, 'notes', None)
                }
            }
            agent_results.append(agent_data)
            
        return {
            'users': user_results,
            'agents': agent_results
        }
    
    @db.transaction
    def accept_task_assignment(self, task_uid: str, assignee_uid: str, 
                              acceptance_notes: str = None) -> bool:
        """
        Marks a task assignment as accepted by the assignee.
        Works for both Users and Agents.
        
        Returns True if acceptance was successful, False otherwise.
        """
        task = self.get_task_by_uid(task_uid)
        if not task:
            return False
        
        # Try to find the assignee as a User
        try:
            user = GraphUser.nodes.get(uid=assignee_uid)
            if not user.assigned_tasks.is_connected(task):
                return False
                
            # Get and update the relationship
            rel = user.assigned_tasks.relationship(task)
            rel.isAccepted = True
            rel.acceptanceDate = datetime.now()
            if acceptance_notes:
                rel.acceptance_notes = acceptance_notes
            rel.lastModifiedDate = datetime.now()
            rel.save()
            return True
        except GraphUser.DoesNotExist:
            # User not found, try Agent
            pass
            
        # Try to find the assignee as an Agent
        try:
            agent = GraphAgent.nodes.get(uid=assignee_uid)
            if not agent.assigned_tasks.is_connected(task):
                return False
                
            # Get and update the relationship
            rel = agent.assigned_tasks.relationship(task)
            rel.isAccepted = True
            rel.acceptanceDate = datetime.now()
            if acceptance_notes:
                rel.acceptance_notes = acceptance_notes
            rel.lastModifiedDate = datetime.now()
            rel.save()
            return True
        except GraphAgent.DoesNotExist:
            # Agent not found
            return False
    
    @db.transaction
    def complete_task_assignment(self, task_uid: str, assignee_uid: str, 
                               actual_effort: float = None) -> bool:
        """
        Marks a task assignment as completed by the assignee.
        Works for both Users and Agents.
        
        Returns True if completion was successful, False otherwise.
        """
        task = self.get_task_by_uid(task_uid)
        if not task:
            return False
        
        # Try to find the assignee as a User
        try:
            user = GraphUser.nodes.get(uid=assignee_uid)
            if not user.assigned_tasks.is_connected(task):
                return False
                
            # Get and update the relationship
            rel = user.assigned_tasks.relationship(task)
            rel.completionDate = datetime.now()
            if actual_effort is not None:
                rel.actualEffort = actual_effort
            rel.lastModifiedDate = datetime.now()
            rel.save()
            return True
        except GraphUser.DoesNotExist:
            # User not found, try Agent
            pass
            
        # Try to find the assignee as an Agent
        try:
            agent = GraphAgent.nodes.get(uid=assignee_uid)
            if not agent.assigned_tasks.is_connected(task):
                return False
                
            # Get and update the relationship
            rel = agent.assigned_tasks.relationship(task)
            rel.completionDate = datetime.now()
            if actual_effort is not None:
                rel.actualEffort = actual_effort
            rel.lastModifiedDate = datetime.now()
            rel.save()
            return True
        except GraphAgent.DoesNotExist:
            # Agent not found
            return False
    
    @db.transaction
    def remove_assignment(self, task_uid: str, assignee_uid: str) -> bool:
        """
        Removes the ASSIGNS_TASK relationship from a User/Agent to a Task.
        
        Returns True if disconnection was successful, False otherwise.
        """
        task = self.get_task_by_uid(task_uid)
        if not task:
            return False
        
        # Try to find the assignee as a User
        try:
            user = GraphUser.nodes.get(uid=assignee_uid)
            if user.assigned_tasks.is_connected(task):
                user.assigned_tasks.disconnect(task)
                return True
        except GraphUser.DoesNotExist:
            # User not found, try Agent
            pass
            
        # Try to find the assignee as an Agent
        try:
            agent = GraphAgent.nodes.get(uid=assignee_uid)
            if agent.assigned_tasks.is_connected(task):
                agent.assigned_tasks.disconnect(task)
                return True
        except GraphAgent.DoesNotExist:
            # Agent not found
            return False
            
        return False
