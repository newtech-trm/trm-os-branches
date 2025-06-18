import unittest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List, Tuple

from trm_api.services.task_service import TaskService
from trm_api.models.task import TaskCreate, TaskUpdate, Task, TaskStatus, TaskType, EffortUnit
from trm_api.models.pagination import PaginatedResponse

class TestTaskService(unittest.TestCase):
    """Test cases for TaskService according to Ontology V3.2."""
    
    def setUp(self):
        """Set up test environment before each test."""
        self.mock_repo = Mock()
        self.task_service = TaskService(repository=self.mock_repo)
        
        # Create sample data for testing
        self.sample_task_data = {
            "uid": "task123",
            "name": "Test Task",
            "description": "This is a test task",
            "status": TaskStatus.TODO,
            "priority": 0,  # 0=Normal
            "task_type": TaskType.FEATURE,
            "effort_unit": EffortUnit.HOURS,
            "project_id": "project123",
            "due_date": "2025-06-30T00:00:00",
            "created_at": "2025-06-16T00:00:00",
            "updated_at": "2025-06-16T00:00:00",
        }
        
        # Create a sample Task object
        self.sample_task = Task(**self.sample_task_data)
        
        # Create sample TaskCreate and TaskUpdate objects
        self.task_create = TaskCreate(
            name="Test Task",
            description="This is a test task",
            status=TaskStatus.TODO,
            priority=0,  # 0=Normal
            task_type=TaskType.FEATURE,
            effort_unit=EffortUnit.HOURS,
            project_id="project123",
            due_date="2025-06-30T00:00:00",
        )
        
        self.task_update = TaskUpdate(
            name="Updated Task",
            description="This is an updated test task",
            status=TaskStatus.IN_PROGRESS,
            priority=1,  # 1=High
            task_type=TaskType.FEATURE,
        )
        
    def test_create_task(self):
        """Test creating a task."""
        self.mock_repo.create_task.return_value = self.sample_task
        
        result = self.task_service.create_task(self.task_create)
        
        self.mock_repo.create_task.assert_called_once_with(task_data=self.task_create)
        self.assertEqual(result, self.sample_task)
        
    def test_get_task_by_id(self):
        """Test retrieving a task by ID."""
        self.mock_repo.get_task_by_uid.return_value = self.sample_task
        
        result = self.task_service.get_task_by_id("task123")
        
        self.mock_repo.get_task_by_uid.assert_called_once_with(uid="task123")
        self.assertEqual(result, self.sample_task)
        
    def test_get_task_by_id_not_found(self):
        """Test retrieving a non-existent task."""
        self.mock_repo.get_task_by_uid.return_value = None
        
        result = self.task_service.get_task_by_id("nonexistent_task")
        
        self.mock_repo.get_task_by_uid.assert_called_once_with(uid="nonexistent_task")
        self.assertIsNone(result)
        
    def test_update_task(self):
        """Test updating a task."""
        updated_task = Task(**{**self.sample_task_data, "name": "Updated Task", "status": TaskStatus.IN_PROGRESS})
        self.mock_repo.update_task.return_value = updated_task
        
        result = self.task_service.update_task("task123", self.task_update)
        
        self.mock_repo.update_task.assert_called_once_with(uid="task123", task_data=self.task_update)
        self.assertEqual(result, updated_task)
        
    def test_delete_task(self):
        """Test deleting a task."""
        self.mock_repo.delete_task.return_value = True
        
        result = self.task_service.delete_task("task123")
        
        self.mock_repo.delete_task.assert_called_once_with(uid="task123")
        self.assertTrue(result)
        
    def test_list_tasks_for_project(self):
        """Test listing tasks for a project."""
        task_list = [self.sample_task]
        self.mock_repo.list_tasks_for_project.return_value = task_list
        
        result = self.task_service.list_tasks_for_project("project123", skip=0, limit=100)
        
        self.mock_repo.list_tasks_for_project.assert_called_once_with(project_id="project123", skip=0, limit=100)
        self.assertEqual(result, task_list)
        
    def test_get_paginated_tasks_for_project(self):
        """Test getting paginated tasks for a project."""
        task_list = [self.sample_task]
        total_count = 1
        page_count = 1
        
        self.mock_repo.get_paginated_tasks_for_project.return_value = (task_list, total_count, page_count)
        
        result = self.task_service.get_paginated_tasks_for_project("project123", page=1, page_size=10)
        
        self.mock_repo.get_paginated_tasks_for_project.assert_called_once_with(
            project_id="project123", page=1, page_size=10
        )
        
        self.assertIsInstance(result, PaginatedResponse)
        self.assertEqual(result.items, task_list)
        self.assertEqual(result.metadata.total_count, total_count)
        self.assertEqual(result.metadata.page, 1)
        self.assertEqual(result.metadata.page_size, 10)
        self.assertEqual(result.metadata.page_count, page_count)
        
    def test_assign_task_to_user_success(self):
        """Test assigning a task to a user successfully."""
        mock_user = Mock(uid="user123")
        self.mock_repo.assign_task_to_user.return_value = (self.sample_task, mock_user)
        
        result = self.task_service.assign_task_to_user(
            task_id="task123",
            user_id="user123",
            assignment_type="Primary",
            priority_level=2,
            estimated_effort=5.0,
            assigned_by="admin123",
            notes="Test assignment"
        )
        
        self.mock_repo.assign_task_to_user.assert_called_once_with(
            task_uid="task123",
            user_uid="user123",
            assignment_type="Primary",
            priority_level=2,
            estimated_effort=5.0,
            assigned_by="admin123",
            notes="Test assignment"
        )
        
        self.assertEqual(result, (self.sample_task, mock_user))
        
    def test_assign_task_to_user_invalid_assignment_type(self):
        """Test assigning a task with invalid assignment type."""
        result = self.task_service.assign_task_to_user(
            task_id="task123",
            user_id="user123",
            assignment_type="Invalid",  # Invalid type
            priority_level=2
        )
        
        self.mock_repo.assign_task_to_user.assert_not_called()
        self.assertIsNone(result)
        
    def test_assign_task_to_user_invalid_priority(self):
        """Test assigning a task with invalid priority level."""
        result = self.task_service.assign_task_to_user(
            task_id="task123",
            user_id="user123",
            assignment_type="Primary",
            priority_level=6  # Invalid priority (should be 1-5)
        )
        
        self.mock_repo.assign_task_to_user.assert_not_called()
        self.assertIsNone(result)
        
    def test_assign_task_to_agent_success(self):
        """Test assigning a task to an agent successfully."""
        mock_agent = Mock(uid="agent123")
        self.mock_repo.assign_task_to_agent.return_value = (self.sample_task, mock_agent)
        
        result = self.task_service.assign_task_to_agent(
            task_id="task123",
            agent_id="agent123",
            assignment_type="Supporting",
            priority_level=3,
            estimated_effort=2.5,
            assigned_by="admin123",
            notes="Test agent assignment"
        )
        
        self.mock_repo.assign_task_to_agent.assert_called_once_with(
            task_uid="task123",
            agent_uid="agent123",
            assignment_type="Supporting",
            priority_level=3,
            estimated_effort=2.5,
            assigned_by="admin123",
            notes="Test agent assignment"
        )
        
        self.assertEqual(result, (self.sample_task, mock_agent))
        
    def test_get_task_assignees_without_details(self):
        """Test getting task assignees without relationship details."""
        mock_assignees = {
            "users": [{"id": "user123", "name": "Test User"}],
            "agents": [{"id": "agent123", "name": "Test Agent"}]
        }
        self.mock_repo.get_task_assignees.return_value = mock_assignees
        
        result = self.task_service.get_task_assignees(
            task_id="task123", 
            include_relationship_details=False
        )
        
        self.mock_repo.get_task_assignees.assert_called_once_with(
            task_uid="task123"
        )
        
        self.assertEqual(result, mock_assignees)
        
    def test_get_task_assignees_with_details(self):
        """Test getting task assignees with relationship details."""
        mock_assignees_with_details = {
            "users": [{"user": {"id": "user123", "name": "Test User"}, "relationship": {"assignmentType": "Primary"}}],
            "agents": [{"agent": {"id": "agent123", "name": "Test Agent"}, "relationship": {"assignmentType": "Supporting"}}]
        }
        self.mock_repo.get_task_assignees_with_relationships.return_value = mock_assignees_with_details
        
        result = self.task_service.get_task_assignees(
            task_id="task123", 
            include_relationship_details=True
        )
        
        self.mock_repo.get_task_assignees_with_relationships.assert_called_once_with(
            task_uid="task123"
        )
        
        self.assertEqual(result, mock_assignees_with_details)
        
    def test_accept_task_assignment(self):
        """Test accepting a task assignment."""
        self.mock_repo.accept_task_assignment.return_value = True
        
        result = self.task_service.accept_task_assignment(
            task_id="task123",
            assignee_id="user123",
            acceptance_notes="Accepted with notes"
        )
        
        self.mock_repo.accept_task_assignment.assert_called_once_with(
            task_uid="task123",
            assignee_uid="user123",
            acceptance_notes="Accepted with notes"
        )
        
        self.assertTrue(result)
        
    def test_complete_task_assignment(self):
        """Test completing a task assignment."""
        self.mock_repo.complete_task_assignment.return_value = True
        
        result = self.task_service.complete_task_assignment(
            task_id="task123",
            assignee_id="user123",
            actual_effort=4.5
        )
        
        self.mock_repo.complete_task_assignment.assert_called_once_with(
            task_uid="task123",
            assignee_uid="user123",
            actual_effort=4.5
        )
        
        self.assertTrue(result)
        
    def test_remove_task_assignment(self):
        """Test removing a task assignment."""
        self.mock_repo.remove_assignment.return_value = True
        
        result = self.task_service.remove_task_assignment(
            task_id="task123",
            assignee_id="user123"
        )
        
        self.mock_repo.remove_assignment.assert_called_once_with(
            task_uid="task123",
            assignee_uid="user123"
        )
        
        self.assertTrue(result)
        
if __name__ == "__main__":
    unittest.main()
