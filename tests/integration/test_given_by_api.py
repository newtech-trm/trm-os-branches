import pytest
import pytest_asyncio
import uuid
from unittest.mock import patch, AsyncMock
from datetime import datetime
from httpx import AsyncClient
from fastapi import status

from trm_api.main import app
from trm_api.models.relationships import Relationship, RelationshipType, TargetEntityTypeEnum
from tests.conftest import get_test_client


class TestGivenByAPI:
    """Integration tests for the GIVEN_BY relationship API endpoints."""

    async def setup_method(self):
        """Setup test fixtures before each test method."""
        # Sample IDs for testing
        self.agent_id = str(uuid.uuid4())
        self.recognition_id = str(uuid.uuid4())
        
        # Sample relationship data
        self.agent_recognition_relationship = {
            "source_id": self.agent_id,
            "source_type": "Agent",
            "target_id": self.recognition_id,
            "target_type": "Recognition",
            "type": "GIVEN_BY",
            "relationshipId": f"given_by_{self.agent_id}_{self.recognition_id}_abcd1234",
            "notes": "Test note for given recognition",
            "createdAt": datetime.now()
        }
        
        # Sample relationship request data
        self.given_by_request = {
            "notes": "Agent recognizing outstanding achievements"
        }
        
        # Tạo async client
        self.client = await get_test_client()
    
    @pytest.mark.asyncio
    @patch("trm_api.api.v1.endpoints.relationship.relationship_service")
    async def test_create_given_by_relationship(self, mock_service):
        """Test creating a GIVEN_BY relationship from Agent to Recognition."""
        # Set up mock - sử dụng async_return_value thay vì return_value cho các coroutine
        mock_service.create_relationship = AsyncMock(return_value=Relationship(**self.agent_recognition_relationship))
        
        # Call API with async client
        response = await self.client.post(
            f"/api/v1/relationships/given-by?agent_id={self.agent_id}&recognition_id={self.recognition_id}",
            json=self.given_by_request
        )
        
        # Assertions
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["source_id"] == self.agent_id
        assert data["source_type"] == "Agent"
        assert data["target_id"] == self.recognition_id
        assert data["target_type"] == "Recognition"
        assert data["type"] == "GIVEN_BY"
        
        # Verify service was called correctly
        mock_service.create_relationship.assert_called_once()
    
    @patch("trm_api.api.v1.endpoints.relationship.relationship_service")
    def test_create_given_by_relationship_entities_not_found(self, mock_service):
        """Test creating a GIVEN_BY relationship when entities don't exist."""
        # Set up mock
        mock_service.create_relationship.return_value = None
        
        # Call API
        response = client.post(
            f"/api/v1/relationships/given-by?agent_id={self.agent_id}&recognition_id={self.recognition_id}",
            json=self.given_by_request
        )
        
        # Assertions
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Verify service was called correctly
        mock_service.create_relationship.assert_called_once()
    
    @patch("trm_api.api.v1.endpoints.relationship.relationship_service")
    def test_get_recognitions_given_by_agent(self, mock_service):
        """Test getting Recognitions given by an Agent."""
        # Set up mock
        mock_service.get_relationships.return_value = [Relationship(**self.agent_recognition_relationship)]
        
        # Call API
        response = client.get(f"/api/v1/relationships/agents/{self.agent_id}/gives-recognitions")
        
        # Assertions
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["source_id"] == self.agent_id
        assert data[0]["target_id"] == self.recognition_id
        assert data[0]["type"] == "GIVEN_BY"
        
        # Verify service was called correctly
        mock_service.get_relationships.assert_called_once()
    
    @pytest.mark.asyncio
    @patch("trm_api.api.v1.endpoints.relationship.relationship_service")
    async def test_get_agents_giving_recognition(self, mock_service):
        """Test getting Agents that gave a Recognition."""
        # Set up mock
        mock_service.get_relationships = AsyncMock(return_value=[Relationship(**self.agent_recognition_relationship)])
        
        # Call API using AsyncClient
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/api/v1/relationships/recognitions/{self.recognition_id}/given-by")
        
        # Assertions
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["source_id"] == self.agent_id
        assert data[0]["target_id"] == self.recognition_id
        assert data[0]["type"] == "GIVEN_BY"
        
        # Verify service was called correctly
        mock_service.get_relationships.assert_called_once()
    
    @pytest.mark.asyncio
    @patch("trm_api.api.v1.endpoints.relationship.relationship_service")
    async def test_get_empty_recognitions_given_by_agent(self, mock_service):
        """Test getting Recognitions when Agent has no relationships."""
        # Set up mock
        mock_service.get_relationships = AsyncMock(return_value=[])
        
        # Call API using AsyncClient
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/api/v1/relationships/agents/{self.agent_id}/gives-recognitions")
        
        # Assertions
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 0
        
        # Verify service was called correctly
        mock_service.get_relationships.assert_called_once()
    
    @pytest.mark.asyncio
    @patch("trm_api.api.v1.endpoints.relationship.relationship_service")
    async def test_delete_given_by_relationship(self, mock_service):
        """Test deleting a GIVEN_BY relationship."""
        # Set up mock
        mock_service.delete_relationship = AsyncMock(return_value=True)
        
        # Call API using AsyncClient
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.delete(
                f"/api/v1/relationships/given-by?agent_id={self.agent_id}&recognition_id={self.recognition_id}"
        )
        
        # Assertions
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify service was called correctly
        mock_service.delete_relationship.assert_called_once()
    
    @patch("trm_api.api.v1.endpoints.relationship.relationship_service")
    def test_delete_given_by_relationship_not_found(self, mock_service):
        """Test deleting a non-existent GIVEN_BY relationship."""
        # Set up mock
        mock_service.delete_relationship.return_value = False
        
        # Call API
        response = client.delete(
            f"/api/v1/relationships/given-by?agent_id={self.agent_id}&recognition_id={self.recognition_id}"
        )
        
        # Assertions
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Verify service was called correctly
        mock_service.delete_relationship.assert_called_once()
