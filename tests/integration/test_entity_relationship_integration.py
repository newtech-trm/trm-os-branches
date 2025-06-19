import pytest
import pytest_asyncio
import uuid
from unittest.mock import patch, AsyncMock
from datetime import datetime
from httpx import AsyncClient
from fastapi import status

from trm_api.main import app
from trm_api.models.relationships import Relationship, RelationshipType, TargetEntityTypeEnum
from trm_api.models.agent import AgentCreate, Agent
from tests.conftest import async_test_client


class TestCompleteEntityRelationshipFlow:
    """Integration tests for a complete flow of entity creation and relationship management."""
    
    # Sử dụng async fixture để khởi tạo ID cho tất cả các test
    @pytest_asyncio.fixture(autouse=True)
    async def setup_test(self, async_test_client):
        """Setup test fixtures before each test method with pytest async fixture."""
        # Tạo các ID mới cho mỗi test
        self.agent_id = str(uuid.uuid4())
        self.recognition_id = str(uuid.uuid4())
        self.win_id = str(uuid.uuid4())
        self.project_id = str(uuid.uuid4())
        self.task_id = str(uuid.uuid4())
        self.resource_id = str(uuid.uuid4())
        self.knowledge_snippet_id = str(uuid.uuid4())
        
        # Sử dụng client từ fixture
        self.client = async_test_client
        
        # Dữ liệu mẫu cho các entity - tuân thủ chính xác model AgentCreate
        self.agent_data = {
            # Không có trường uid trong AgentCreate
            "name": "Test Agent",
            "agentType": "InternalAgent",  # Phải là một trong các loại hợp lệ: InternalAgent, ExternalAgent, AIAgent, AGE
            "purpose": "Testing the API integration",
            "description": "Test agent for integration testing",
            "status": "active",
            "capabilities": ["testing", "integration"],
            "jobTitle": "Tester",
            "department": "QA",
            "isFounder": False,
            "founderRecognitionAuthority": False,  # Thêm trường bắt buộc theo AgentBase
            "contactInfo": {"email": "agent@test.com"},
            "toolIds": []  # Thêm trường từ AgentCreate
        }
        
        self.project_data = {
            "uid": self.project_id,
            "name": "Test Project",
            "description": "A test project for integration testing",
            "status": "Active"
        }
        
        self.task_data = {
            "uid": self.task_id,
            "title": "Test Task",
            "description": "A test task for integration testing",
            "status": "New",
            "project_id": self.project_id
        }
        
        self.resource_data = {
            "uid": self.resource_id,
            "name": "Test Resource",
            "resourceType": "Document",
            "description": "A test resource for integration testing"
        }
        
        self.win_data = {
            "uid": self.win_id,
            "title": "Test WIN",
            "description": "A test WIN for integration testing",
            "status": "Completed",
            "winType": "Achievement"
        }
        
        self.recognition_data = {
            "uid": self.recognition_id,
            "title": "Test Recognition",
            "description": "A test recognition for integration testing",
            "recognitionType": "Appreciation",
            "status": "Active"
        }
        
        self.knowledge_snippet_data = {
            "uid": self.knowledge_snippet_id,
            "content": "Test Knowledge Content",
            "snippetType": "Learning",
            "tags": ["test", "integration"]
        }

    @pytest.mark.asyncio
    @patch("trm_api.api.v1.endpoints.agent.agent_service")
    async def test_create_agent(self, mock_service):
        """Test creating an Agent."""
        import json
        import traceback
        
        try:
            # Dữ liệu AgentCreate đã được chuẩn bị đúng từ setup_test
            agent_model_data = self.agent_data
                
            print(f"\nModel data: {json.dumps(agent_model_data, indent=2, default=str)}")
            agent_create = AgentCreate(**agent_model_data)
            print(f"\nValid AgentCreate model: {json.dumps(agent_create.model_dump(), indent=2, default=str)}")
            
            # Kiểm tra endpoint cụ thể
            print(f"\nTesting endpoint: /api/v1/agents/")
            
            # Tạo mock response với dữ liệu Agent đầy đủ
            agent_response_data = agent_model_data.copy()
            agent_response_data["agentId"] = self.agent_id
            agent_response_data["creationDate"] = datetime.now()
            
            mock_service.create_agent = AsyncMock(return_value=agent_response_data)
            
            # In ra chi tiết mock để debug
            print(f"\nMock service setup: {mock_service}")
            print(f"Mock return value: {json.dumps(agent_response_data, indent=2, default=str)}")
            
            # Gọi API với dữ liệu AgentCreate hợp lệ
            print(f"\nSending API request to /api/v1/agents/ with data: {json.dumps(agent_model_data, indent=2, default=str)}")
            
            try:
                response = await self.client.post("/api/v1/agents/", json=agent_model_data)
                print(f"Response status: {response.status_code}")
                print(f"Response headers: {response.headers}")
                print(f"Response body: {response.text}")
                
                # Kiểm tra kết quả
                assert response.status_code == status.HTTP_201_CREATED
                data = response.json()
                assert data["name"] == "Test Agent"
                
                # Kiểm tra mock service được gọi với dữ liệu đúng
                mock_service.create_agent.assert_called_once()
                
            except Exception as e:
                print(f"\nError when calling API: {str(e)}")
                if hasattr(e, "response") and e.response:
                    print(f"Response status: {e.response.status_code}")
                    print(f"Response body: {e.response.text}")
                raise
                
        except Exception as e:
            print(f"\nGeneral Error: {str(e)}")
            print(traceback.format_exc())
            raise
    
    @pytest.mark.asyncio
    @patch("trm_api.api.v1.endpoints.project.project_service")
    async def test_create_project(self, mock_service):
        """Test creating a Project."""
        mock_service.create_project = AsyncMock(return_value=self.project_data)
        
        response = await self.client.post("/api/v1/projects/", json=self.project_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["uid"] == self.project_id
        assert data["name"] == "Test Project"
        
        mock_service.create_project.assert_called_once()
    
    @pytest.mark.asyncio
    @patch("trm_api.api.v1.endpoints.task.task_service")
    async def test_create_task(self, mock_service):
        """Test creating a Task."""
        mock_service.create_task = AsyncMock(return_value=self.task_data)
        
        response = await self.client.post("/api/v1/tasks/", json=self.task_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["uid"] == self.task_id
        assert data["title"] == "Test Task"
        assert data["project_id"] == self.project_id
        
        mock_service.create_task.assert_called_once()
    
    @pytest.mark.asyncio
    @patch("trm_api.api.v1.endpoints.resource.resource_service")
    async def test_create_resource(self, mock_service):
        """Test creating a Resource."""
        mock_service.create_resource = AsyncMock(return_value=self.resource_data)
        
        response = await self.client.post("/api/v1/resources/", json=self.resource_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["uid"] == self.resource_id
        assert data["name"] == "Test Resource"
        
        mock_service.create_resource.assert_called_once()
    
    @pytest.mark.asyncio
    @patch("trm_api.api.v1.endpoints.win.win_service")
    async def test_create_win(self, mock_service):
        """Test creating a WIN."""
        mock_service.create_win = AsyncMock(return_value=self.win_data)
        
        response = await self.client.post("/api/v1/wins/", json=self.win_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["uid"] == self.win_id
        assert data["title"] == "Test WIN"
        
        mock_service.create_win.assert_called_once()
    
    @pytest.mark.asyncio
    @patch("trm_api.api.v1.endpoints.recognition.recognition_service")
    async def test_create_recognition(self, mock_service):
        """Test creating a Recognition."""
        mock_service.create_recognition = AsyncMock(return_value=self.recognition_data)
        
        response = await self.client.post("/api/v1/recognitions/", json=self.recognition_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["uid"] == self.recognition_id
        assert data["title"] == "Test Recognition"
        
        mock_service.create_recognition.assert_called_once()
    
    @pytest.mark.asyncio
    @patch("trm_api.api.v1.endpoints.knowledge_snippet.knowledge_snippet_service")
    async def test_create_knowledge_snippet(self, mock_service):
        """Test creating a Knowledge Snippet."""
        mock_service.create_snippet = AsyncMock(return_value=self.knowledge_snippet_data)
        
        response = await self.client.post("/api/v1/knowledge-snippets/", json=self.knowledge_snippet_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["uid"] == self.knowledge_snippet_id
        assert data["content"] == "Test Knowledge Content"
        
        mock_service.create_snippet.assert_called_once()
    
    @pytest.mark.asyncio
    @patch("trm_api.api.v1.endpoints.relationship.relationship_service")
    async def test_complex_relationship_flow(self, mock_service):
        """Test a complex flow of relationships between multiple entities."""
        # 1. Tạo relationship LEADS_TO_WIN (Project → WIN)
        project_win_relationship = {
            "source_id": self.project_id,
            "source_type": "Project",
            "target_id": self.win_id,
            "target_type": "WIN",
            "type": "LEADS_TO_WIN",
            "relationshipId": f"leads_to_win_{self.project_id}_{self.win_id}",
            "contributionLevel": "High",
            "directContribution": True,
            "impactRatio": 0.8,
            "createdAt": datetime.now()
        }
        mock_service.create_relationship = AsyncMock(return_value=Relationship(**project_win_relationship))
        
        response = await self.client.post(
            f"/api/v1/relationships/leads-to-win?project_id={self.project_id}&win_id={self.win_id}",
            json={"contributionLevel": "High", "directContribution": True, "impactRatio": 0.8}
        )
        
        if response.status_code != status.HTTP_200_OK:
            print(f"\nERROR RESPONSE: {response.text}\n")
            
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["source_id"] == self.project_id
        assert data["target_id"] == self.win_id
        assert data["type"] == "LEADS_TO_WIN"
        
        # 2. Tạo relationship RECOGNIZES_WIN (Recognition → WIN)
        recognition_win_relationship = {
            "source_id": self.recognition_id,
            "source_type": "Recognition",
            "target_id": self.win_id,
            "target_type": "WIN",
            "type": "RECOGNIZES_WIN",
            "relationshipId": f"recognizes_win_{self.recognition_id}_{self.win_id}",
            "recognitionLevel": "Outstanding",
            "impactMeasurement": "High",
            "notes": "Excellent achievement",
            "createdAt": datetime.now()
        }
        mock_service.create_relationship = AsyncMock(return_value=Relationship(**recognition_win_relationship))
        
        response = await self.client.post(
            f"/api/v1/relationships/recognizes-win?recognition_id={self.recognition_id}&win_id={self.win_id}",
            json={"recognitionLevel": "Outstanding", "impactMeasurement": "High", "notes": "Excellent achievement"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["source_id"] == self.recognition_id
        assert data["target_id"] == self.win_id
        assert data["type"] == "RECOGNIZES_WIN"
        
        # 3. Tạo relationship GIVEN_BY (Recognition → Agent)
        given_by_relationship = {
            "source_id": self.recognition_id,
            "source_type": "Recognition",
            "target_id": self.agent_id,
            "target_type": "Agent",
            "type": "GIVEN_BY",
            "relationshipId": f"given_by_{self.recognition_id}_{self.agent_id}",
            "notes": "Recognition given by this agent",
            "createdAt": datetime.now()
        }
        mock_service.create_relationship = AsyncMock(return_value=Relationship(**given_by_relationship))
        
        response = await self.client.post(
            f"/api/v1/relationships/given-by?recognition_id={self.recognition_id}&agent_id={self.agent_id}",
            json={"notes": "Recognition given by this agent"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["source_id"] == self.recognition_id
        assert data["target_id"] == self.agent_id
        assert data["type"] == "GIVEN_BY"
        
        # 4. Tạo relationship RECEIVED_BY (Recognition → Agent, nhưng là agent khác)
        received_by_relationship = {
            "source_id": self.recognition_id,
            "source_type": "Recognition",
            "target_id": self.agent_id,  # Trong thực tế đây sẽ là agent ID khác
            "target_type": "Agent",
            "type": "RECEIVED_BY",
            "relationshipId": f"received_by_{self.recognition_id}_{self.agent_id}",
            "notes": "Recognition received by this agent"
        }
        mock_service.create_relationship = AsyncMock(return_value=Relationship(**received_by_relationship))
        
        response = await self.client.post(
            f"/api/v1/relationships/received-by?recognition_id={self.recognition_id}&agent_id={self.agent_id}",
            json={"notes": "Recognition received by this agent"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["source_id"] == self.recognition_id
        assert data["target_id"] == self.agent_id
        assert data["type"] == "RECEIVED_BY"
        
        # 5. Tạo relationship GENERATES_KNOWLEDGE (WIN → KnowledgeSnippet)
        generates_knowledge_relationship = {
            "source_id": self.win_id,
            "source_type": "WIN",
            "target_id": self.knowledge_snippet_id,
            "target_type": "KnowledgeSnippet",
            "type": "GENERATES_KNOWLEDGE",
            "relationshipId": f"generates_knowledge_{self.win_id}_{self.knowledge_snippet_id}",
            "knowledgeCategory": "LessonsLearned",
            "relevanceLevel": "High"
        }
        mock_service.create_relationship = AsyncMock(return_value=Relationship(**generates_knowledge_relationship))
        
        response = await self.client.post(
            f"/api/v1/relationships/generates-knowledge?win_id={self.win_id}&snippet_id={self.knowledge_snippet_id}",
            json={"knowledgeCategory": "LessonsLearned", "relevanceLevel": "High"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["source_id"] == self.win_id
        assert data["target_id"] == self.knowledge_snippet_id
        assert data["type"] == "GENERATES_KNOWLEDGE"
        
        # 6. Tạo relationship RECOGNIZES_CONTRIBUTION_TO (Recognition → Project)
        recognizes_contribution_relationship = {
            "source_id": self.recognition_id,
            "source_type": "Recognition",
            "target_id": self.project_id,
            "target_type": "Project",
            "type": "RECOGNIZES_CONTRIBUTION_TO",
            "relationshipId": f"recognizes_contribution_{self.recognition_id}_{self.project_id}",
            "contribution_type": "Leadership",
            "contribution_level": "High",
            "impact_notes": "Significant project leadership"
        }
        mock_service.create_relationship = AsyncMock(return_value=Relationship(**recognizes_contribution_relationship))
        
        response = await self.client.post(
            f"/api/v1/relationships/recognizes-contribution-to?recognition_id={self.recognition_id}&target_id={self.project_id}&target_type=Project",
            json={"contribution_type": "Leadership", "contribution_level": "High", "impact_notes": "Significant project leadership"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["source_id"] == self.recognition_id
        assert data["target_id"] == self.project_id
        assert data["type"] == "RECOGNIZES_CONTRIBUTION_TO"
        
        # Reset mock để kiểm tra các lệnh gọi tiếp theo
        mock_service.get_relationships.reset_mock()
        
        # 7. Lấy tất cả WINs được ghi nhận bởi một Recognition
        mock_service.get_relationships = AsyncMock(return_value=[Relationship(**recognition_win_relationship)])
        
        response = await self.client.get(f"/api/v1/relationships/recognitions/{self.recognition_id}/recognizes-wins")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["source_id"] == self.recognition_id
        assert data[0]["target_id"] == self.win_id
        assert data[0]["type"] == "RECOGNIZES_WIN"
        
        # 8. Lấy tất cả Recognition ghi nhận một WIN
        mock_service.get_relationships.reset_mock()
        mock_service.get_relationships = AsyncMock(return_value=[Relationship(**recognition_win_relationship)])
        
        response = await self.client.get(f"/api/v1/relationships/wins/{self.win_id}/recognized-by")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["source_id"] == self.recognition_id
        assert data[0]["target_id"] == self.win_id
        
        # 9. Lấy tất cả Knowledge được tạo ra từ một WIN
        mock_service.get_relationships.reset_mock()
        mock_service.get_relationships = AsyncMock(return_value=[Relationship(**generates_knowledge_relationship)])
        
        response = await self.client.get(f"/api/v1/relationships/wins/{self.win_id}/generates-knowledge")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["source_id"] == self.win_id
        assert data[0]["target_id"] == self.knowledge_snippet_id
        
        # 10. Xóa tất cả relationships và kiểm tra
        mock_service.delete_relationship.return_value = True
        
        # Xóa LEADS_TO_WIN
        response = client.delete(
            f"/api/v1/relationships/leads-to-win?project_id={self.project_id}&win_id={self.win_id}"
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Xóa RECOGNIZES_WIN
        response = client.delete(
            f"/api/v1/relationships/recognizes-win?recognition_id={self.recognition_id}&win_id={self.win_id}"
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Xóa GIVEN_BY
        response = client.delete(
            f"/api/v1/relationships/given-by?recognition_id={self.recognition_id}&agent_id={self.agent_id}"
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Xóa RECEIVED_BY
        response = client.delete(
            f"/api/v1/relationships/received-by?recognition_id={self.recognition_id}&agent_id={self.agent_id}"
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Xóa GENERATES_KNOWLEDGE
        response = client.delete(
            f"/api/v1/relationships/generates-knowledge?win_id={self.win_id}&snippet_id={self.knowledge_snippet_id}"
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Xóa RECOGNIZES_CONTRIBUTION_TO
        response = client.delete(
            f"/api/v1/relationships/recognizes-contribution-to?recognition_id={self.recognition_id}&target_id={self.project_id}&target_type=Project"
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify total number of delete calls
        assert mock_service.delete_relationship.call_count == 6
