import json
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import unittest
from datetime import datetime, timedelta

from trm_api.main import app
from trm_api.models.task import Task, TaskCreate, TaskUpdate, TaskStatus, TaskType, EffortUnit
from trm_api.models.pagination import PaginatedResponse
from trm_api.services.task_service import TaskService

# Khởi tạo TestClient
client = TestClient(app)

def get_mock_task():
    """Return a mock task with standard fields"""
    return {
        "uid": "task123",
        "name": "Test Task",
        "description": "This is a test task",
        "status": TaskStatus.TODO,
        "priority": 0,  # 0=Normal
        "task_type": TaskType.FEATURE,
        "project_id": "project123",
        "due_date": (datetime.now() + timedelta(days=14)).isoformat(),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "tags": ["test", "integration"],
        "effort_estimate": 10.0,
        "effort_unit": EffortUnit.HOURS,
        "metadata": {"source": "API test"},
        "dependencies": [],
        "sub_tasks": [],
        "assignee_agent_id": None,
        "reporter_agent_id": None
    }

class TestTaskEndpoints:
    """Test cases for Task API endpoints according to Ontology V3.2."""
    
    @patch('trm_api.api.v1.endpoints.task.get_task_service')
    def test_create_task(self, mock_get_service):
        """Test creating a task via API endpoint"""
        # Setup mock
        mock_task = Task(**get_mock_task())
        mock_service = MagicMock()
        mock_service.create_task.return_value = mock_task
        mock_get_service.return_value = mock_service
        
        # Test data
        task_data = {
            "name": "API Task",
            "description": "Created via API test",
            "status": TaskStatus.TODO.value,  # Gửi giá trị enum dạng string cho API
            "priority": 0,  # 0=Normal
            "project_id": "project123",
            "due_date": (datetime.now() + timedelta(days=14)).isoformat(),
            "tags": ["api", "test"],
            "effort_estimate": 8.0,
            "task_type": TaskType.FEATURE.value,  # Gửi giá trị enum dạng string cho API
            "effort_unit": EffortUnit.HOURS.value  # Gửi giá trị enum dạng string cho API
        }
        
        # Make request
        response = client.post(
            "/api/v1/tasks/",
            json=task_data
        )
        
        # Check results
        assert response.status_code == 201
        mock_service.create_task.assert_called_once()
        assert response.json()["uid"] == mock_task.uid
        
    @patch('trm_api.api.v1.endpoints.task.get_task_service')
    def test_get_task(self, mock_get_service):
        """Test retrieving a task via API endpoint"""
        # Setup mock
        mock_task = Task(**get_mock_task())
        mock_service = MagicMock()
        mock_service.get_task_by_id.return_value = mock_task
        mock_get_service.return_value = mock_service
        
        # Make request
        response = client.get("/api/v1/tasks/task123")
        
        # Check results
        assert response.status_code == 200
        mock_service.get_task_by_id.assert_called_once_with(task_id="task123")
        assert response.json()["uid"] == "task123"
        
    @patch('trm_api.api.v1.endpoints.task.get_task_service')
    def test_get_task_not_found(self, mock_get_service):
        """Test retrieving a non-existent task"""
        # Setup mock
        mock_service = MagicMock()
        mock_service.get_task_by_id.return_value = None
        mock_get_service.return_value = mock_service
        
        # Make request
        response = client.get("/api/v1/tasks/nonexistent")
        
        # Check results
        assert response.status_code == 404
        mock_service.get_task_by_id.assert_called_once_with(task_id="nonexistent")
        
    @patch('trm_api.api.v1.endpoints.task.get_task_service')
    def test_update_task(self, mock_get_service):
        """Test updating a task via API endpoint"""
        # Setup mock
        updated_task = get_mock_task()
        updated_task["name"] = "Updated Task"
        updated_task["status"] = TaskStatus.IN_PROGRESS
        mock_task = Task(**updated_task)
        
        mock_service = MagicMock()
        mock_service.update_task.return_value = mock_task
        mock_get_service.return_value = mock_service
        
        # Test data
        update_data = {
            "name": "Updated Task",
            "status": TaskStatus.IN_PROGRESS.value  # Gửi giá trị enum dạng string cho API
        }
        
        # Make request
        response = client.put(
            "/api/v1/tasks/task123",
            json=update_data
        )
        
        # Check results
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Task"
        assert response.json()["status"] == "in_progress"
        
    @patch('trm_api.api.v1.endpoints.task.get_task_service')
    def test_delete_task(self, mock_get_service):
        """Test deleting a task via API endpoint"""
        # Setup mock
        mock_service = MagicMock()
        mock_service.delete_task.return_value = True
        mock_get_service.return_value = mock_service
        
        # Make request
        response = client.delete("/api/v1/tasks/task123")
        
        # Check results
        assert response.status_code == 204
        mock_service.delete_task.assert_called_once_with(task_id="task123")
        
    @patch('trm_api.api.v1.endpoints.task.get_task_service')
    def test_get_paginated_tasks(self, mock_get_service):
        """Test getting paginated tasks for a project"""
        # Setup mock
        mock_tasks = [Task(**get_mock_task())]
        mock_paginated = PaginatedResponse.create(
            items=mock_tasks,
            total_count=1,
            page=1,
            page_size=10
        )
        
        mock_service = MagicMock()
        mock_service.get_paginated_tasks_for_project.return_value = mock_paginated
        mock_get_service.return_value = mock_service
        
        # Make request
        response = client.get("/api/v1/tasks/?project_id=project123&page=1&page_size=10")
        
        # Check results
        assert response.status_code == 200
        result = response.json()
        assert "items" in result
        assert "metadata" in result
        assert result["metadata"]["total_count"] == 1
        assert result["metadata"]["page"] == 1
        assert result["metadata"]["page_size"] == 10
        assert len(result["items"]) == 1
        
    @patch('trm_api.api.v1.endpoints.task.get_task_service')
    def test_assign_task_to_user(self, mock_get_service):
        """Test assigning a task to a user"""
        # Setup mock
        mock_task = Task(**get_mock_task())
        mock_user = MagicMock()
        mock_user.uid = "user123"
        
        mock_service = MagicMock()
        mock_service.assign_task_to_user.return_value = (mock_task, mock_user)
        mock_get_service.return_value = mock_service
        
        # Make request
        response = client.post(
            "/api/v1/tasks/task123/assign/user/user123?assignment_type=Primary&priority_level=2"
        )
        
        # Check results
        assert response.status_code == 200
        assert response.json()["task_id"] == "task123"
        assert response.json()["user_id"] == "user123"
        assert response.json()["assignment_type"] == "Primary"
        assert response.json()["priority_level"] == 2
        
    @patch('trm_api.api.v1.endpoints.task.get_task_service')
    def test_assign_task_to_agent(self, mock_get_service):
        """Test assigning a task to an agent"""
        # Setup mock
        mock_task = Task(**get_mock_task())
        mock_agent = MagicMock()
        mock_agent.uid = "agent123"
        
        mock_service = MagicMock()
        mock_service.assign_task_to_agent.return_value = (mock_task, mock_agent)
        mock_get_service.return_value = mock_service
        
        # Make request
        response = client.post(
            "/api/v1/tasks/task123/assign/agent/agent123?assignment_type=Supporting&priority_level=3"
        )
        
        # Check results
        assert response.status_code == 200
        assert response.json()["task_id"] == "task123"
        assert response.json()["agent_id"] == "agent123"
        assert response.json()["assignment_type"] == "Supporting"
        assert response.json()["priority_level"] == 3
        
    @patch('trm_api.api.v1.endpoints.task.get_task_service')
    def test_get_task_assignees(self, mock_get_service):
        """Test getting task assignees"""
        # Setup mock
        mock_assignees = {
            "users": [{"id": "user123", "name": "Test User"}],
            "agents": [{"id": "agent123", "name": "Test Agent"}]
        }
        
        mock_service = MagicMock()
        mock_service.get_task_by_id.return_value = Task(**get_mock_task())
        mock_service.get_task_assignees.return_value = mock_assignees
        mock_get_service.return_value = mock_service
        
        # Make request
        response = client.get("/api/v1/tasks/task123/assignees?include_relationship_details=true")
        
        # Check results
        assert response.status_code == 200
        result = response.json()
        assert "users" in result
        assert "agents" in result
        assert len(result["users"]) == 1
        assert len(result["agents"]) == 1
        
    @patch('trm_api.api.v1.endpoints.task.get_task_service')
    def test_accept_task_assignment(self, mock_get_service):
        """Test accepting a task assignment"""
        # Setup mock
        mock_service = MagicMock()
        mock_service.accept_task_assignment.return_value = True
        mock_get_service.return_value = mock_service
        
        # Make request
        response = client.post(
            "/api/v1/tasks/task123/accept?assignee_id=user123&acceptance_notes=Accepted"
        )
        
        # Check results
        assert response.status_code == 200
        assert response.json()["task_id"] == "task123"
        assert response.json()["assignee_id"] == "user123"
        assert response.json()["accepted"] == True
        
    @patch('trm_api.api.v1.endpoints.task.get_task_service')
    def test_complete_task_assignment(self, mock_get_service):
        """Test completing a task assignment"""
        # Setup mock
        mock_service = MagicMock()
        mock_service.complete_task_assignment.return_value = True
        mock_get_service.return_value = mock_service
        
        # Make request
        response = client.post(
            "/api/v1/tasks/task123/complete?assignee_id=user123&actual_effort=5.5"
        )
        
        # Check results
        assert response.status_code == 200
        assert response.json()["task_id"] == "task123"
        assert response.json()["assignee_id"] == "user123"
        assert response.json()["completed"] == True
        
    @patch('trm_api.api.v1.endpoints.task.get_task_service')
    def test_remove_task_assignment(self, mock_get_service):
        """Test removing a task assignment"""
        # Setup mock
        mock_service = MagicMock()
        mock_service.remove_task_assignment.return_value = True
        mock_get_service.return_value = mock_service
        
        # Make request
        response = client.delete("/api/v1/tasks/task123/assignment/user123")
        
        # Check results
        assert response.status_code == 204
