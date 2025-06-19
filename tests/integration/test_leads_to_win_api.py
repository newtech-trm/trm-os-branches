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


class TestLeadsToWinAPI:
    """Integration tests for the LEADS_TO_WIN relationship API endpoints."""

    async def setup_method(self):
        """Setup test fixtures before each test method."""
        # Sample IDs for testing
        self.project_id = str(uuid.uuid4())
        self.event_id = str(uuid.uuid4())
        self.win_id = str(uuid.uuid4())
        
        # Sample relationship data
        self.project_win_relationship = {
            "source_id": self.project_id,
            "source_type": "Project",
            "target_id": self.win_id,
            "target_type": "Win",
            "type": "LEADS_TO_WIN",
            "relationshipId": f"leads_to_win_{self.project_id}_{self.win_id}_abcd1234",
            "contributionLevel": 3,
            "directContribution": True,
            "createdAt": datetime.now()
        }
        
        self.event_win_relationship = {
            "source_id": self.event_id,
            "source_type": "Event",
            "target_id": self.win_id,
            "target_type": "Win",
            "type": "LEADS_TO_WIN",
            "relationshipId": f"leads_to_win_{self.event_id}_{self.win_id}_abcd5678",
            "contributionLevel": 4,
            "directContribution": False,
            "createdAt": datetime.now()
        }
        
        # Tạo async client
        self.client = await get_test_client()
        
        # Sample relationship request data
        self.leads_to_win_request = {
            "direct_contribution": True,
            "contribution_level": 3,
            "impact_ratio": 0.75,
            "recognition_score": 85,
            "notes": "Test relationship"
        }
    
    @pytest.mark.asyncio
    @patch("trm_api.api.v1.endpoints.relationship.relationship_service")
    async def test_create_project_leads_to_win_relationship(self, mock_service):
        """Test creating a LEADS_TO_WIN relationship from Project to WIN."""
        # Set up mock
        mock_service.create_relationship.return_value = Relationship(**self.project_win_relationship)
        mock_service.create_relationship.side_effect = AsyncMock(return_value=Relationship(**self.project_win_relationship))
        
        # Call API with async client
        response = await self.client.post(
            f"/api/v1/relationships/leads-to-win?source_id={self.project_id}&source_type=Project&win_id={self.win_id}",
            json=self.leads_to_win_request
        )
        
        # Assertions
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["source_id"] == self.project_id
        assert data["source_type"] == "Project"
        assert data["target_id"] == self.win_id
        assert data["target_type"] == "Win"
        assert data["type"] == "LEADS_TO_WIN"
        
        # Verify service was called correctly
        mock_service.create_relationship.assert_called_once()
    
    @pytest.mark.asyncio
    @patch("trm_api.api.v1.endpoints.relationship.relationship_service")
    async def test_create_event_leads_to_win_relationship(self, mock_service):
        """Test creating a LEADS_TO_WIN relationship from Event to WIN."""
        # Set up mock
        mock_service.create_relationship.return_value = Relationship(**self.event_win_relationship)
        mock_service.create_relationship.side_effect = AsyncMock(return_value=Relationship(**self.event_win_relationship))
        
        # Call API with async client
        response = await self.client.post(
            f"/api/v1/relationships/leads-to-win?source_id={self.event_id}&source_type=Event&win_id={self.win_id}",
            json=self.leads_to_win_request
        )
        
        # Assertions
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["source_id"] == self.event_id
        assert data["source_type"] == "Event"
        assert data["target_id"] == self.win_id
        assert data["target_type"] == "Win"
        assert data["type"] == "LEADS_TO_WIN"
        
        # Verify service was called correctly
        mock_service.create_relationship.assert_called_once()
    
    @patch("trm_api.api.v1.endpoints.relationship.relationship_service")
    def test_create_leads_to_win_relationship_invalid_source_type(self, mock_service):
        """Test creating a LEADS_TO_WIN relationship with invalid source type."""
        # Call API with invalid source type
        response = client.post(
            f"/api/v1/relationships/leads-to-win?source_id={self.project_id}&source_type=InvalidType&win_id={self.win_id}",
            json=self.leads_to_win_request
        )
        
        # Assertions
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Verify service was not called
        mock_service.create_relationship.assert_not_called()
    
    @patch("trm_api.api.v1.endpoints.relationship.relationship_service")
    def test_create_leads_to_win_relationship_invalid_properties(self, mock_service):
        """Test creating a LEADS_TO_WIN relationship with invalid properties."""
        # Invalid request with impact_ratio > 1
        invalid_request = {
            "impact_ratio": 1.5  # Invalid: should be 0-1
        }
        
        # Call API
        response = client.post(
            f"/api/v1/relationships/leads-to-win?source_id={self.project_id}&source_type=Project&win_id={self.win_id}",
            json=invalid_request
        )
        
        # Assertions
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Verify service was not called
        mock_service.create_relationship.assert_not_called()
    
    @patch("trm_api.api.v1.endpoints.relationship.relationship_service")
    def test_get_wins_from_project(self, mock_service):
        """Test getting WINs led by a Project."""
        # Set up mock
        mock_service.get_relationships.return_value = [Relationship(**self.project_win_relationship)]
        
        # Call API
        response = client.get(f"/api/v1/relationships/projects/{self.project_id}/leads-to-wins")
        
        # Assertions
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["source_id"] == self.project_id
        assert data[0]["target_id"] == self.win_id
        assert data[0]["type"] == "LEADS_TO_WIN"
        
        # Verify service was called correctly
        mock_service.get_relationships.assert_called_once()
    
    @patch("trm_api.api.v1.endpoints.relationship.relationship_service")
    def test_get_wins_from_event(self, mock_service):
        """Test getting WINs led by an Event."""
        # Set up mock
        mock_service.get_relationships.return_value = [Relationship(**self.event_win_relationship)]
        
        # Call API
        response = client.get(f"/api/v1/relationships/events/{self.event_id}/leads-to-wins")
        
        # Assertions
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["source_id"] == self.event_id
        assert data[0]["target_id"] == self.win_id
        assert data[0]["type"] == "LEADS_TO_WIN"
        
        # Verify service was called correctly
        mock_service.get_relationships.assert_called_once()
    
    @patch("trm_api.api.v1.endpoints.relationship.relationship_service")
    def test_get_projects_events_leading_to_win(self, mock_service):
        """Test getting Projects and Events leading to a WIN."""
        # Set up mock
        mock_service.get_relationships.return_value = [
            Relationship(**self.project_win_relationship),
            Relationship(**self.event_win_relationship)
        ]
        
        # Call API
        response = client.get(f"/api/v1/relationships/wins/{self.win_id}/led-by")
        
        # Assertions
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        assert data[0]["source_id"] == self.project_id
        assert data[1]["source_id"] == self.event_id
        assert data[0]["target_id"] == self.win_id
        assert data[1]["target_id"] == self.win_id
        
        # Verify service was called correctly
        mock_service.get_relationships.assert_called_once()
    
    @patch("trm_api.api.v1.endpoints.relationship.relationship_service")
    def test_get_projects_leading_to_win_with_filter(self, mock_service):
        """Test getting only Projects leading to a WIN with source_type filter."""
        # Set up mock
        mock_service.get_relationships.return_value = [Relationship(**self.project_win_relationship)]
        
        # Call API with source_type filter
        response = client.get(f"/api/v1/relationships/wins/{self.win_id}/led-by?source_type=Project")
        
        # Assertions
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["source_id"] == self.project_id
        assert data[0]["source_type"] == "Project"
        
        # Verify service was called correctly
        mock_service.get_relationships.assert_called_once()
    
    @patch("trm_api.api.v1.endpoints.relationship.relationship_service")
    def test_delete_leads_to_win_relationship(self, mock_service):
        """Test deleting a LEADS_TO_WIN relationship."""
        # Set up mock
        mock_service.delete_relationship.return_value = True
        
        # Call API
        response = client.delete(
            f"/api/v1/relationships/leads-to-win?source_id={self.project_id}&source_type=Project&win_id={self.win_id}"
        )
        
        # Assertions
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify service was called correctly
        mock_service.delete_relationship.assert_called_once()
    
    @patch("trm_api.api.v1.endpoints.relationship.relationship_service")
    def test_delete_leads_to_win_relationship_not_found(self, mock_service):
        """Test deleting a non-existent LEADS_TO_WIN relationship."""
        # Set up mock
        mock_service.delete_relationship.return_value = False
        
        # Call API
        response = client.delete(
            f"/api/v1/relationships/leads-to-win?source_id={self.project_id}&source_type=Project&win_id={self.win_id}"
        )
        
        # Assertions
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Verify service was called correctly
        mock_service.delete_relationship.assert_called_once()
    
    @patch("trm_api.api.v1.endpoints.relationship.relationship_service")
    def test_delete_leads_to_win_relationship_invalid_source_type(self, mock_service):
        """Test deleting a LEADS_TO_WIN relationship with invalid source type."""
        # Call API with invalid source type
        response = client.delete(
            f"/api/v1/relationships/leads-to-win?source_id={self.project_id}&source_type=InvalidType&win_id={self.win_id}"
        )
        
        # Assertions
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Verify service was not called
        mock_service.delete_relationship.assert_not_called()
