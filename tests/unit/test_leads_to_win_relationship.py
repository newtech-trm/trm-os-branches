import pytest
import uuid
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from trm_api.models.relationships import Relationship, RelationshipType, TargetEntityTypeEnum
from trm_api.services.relationship_service import RelationshipService


class TestLeadsToWinRelationship:
    """Unit tests for the LEADS_TO_WIN relationship service methods."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.service = RelationshipService()
        
        # Sample IDs for testing
        self.project_id = str(uuid.uuid4())
        self.event_id = str(uuid.uuid4())
        self.win_id = str(uuid.uuid4())
        
        # Sample relationship data for Project -> WIN
        self.project_win_relationship = {
            "source_id": self.project_id,
            "source_type": "Project",
            "target_id": self.win_id,
            "target_type": "Win",
            "type": "LEADS_TO_WIN",
            "relationshipId": f"leads_to_win_{self.project_id}_{self.win_id}_abcd1234",
            "contributionLevel": 3,
            "directContribution": True,
            "createdAt": datetime.utcnow()
        }
        
        # Sample relationship data for Event -> WIN
        self.event_win_relationship = {
            "source_id": self.event_id,
            "source_type": "Event",
            "target_id": self.win_id,
            "target_type": "Win",
            "type": "LEADS_TO_WIN",
            "relationshipId": f"leads_to_win_{self.event_id}_{self.win_id}_abcd5678",
            "contributionLevel": 4,
            "directContribution": False,
            "createdAt": datetime.utcnow()
        }
    
    @patch('trm_api.services.relationship_service.RelationshipService._get_db')
    def test_create_project_leads_to_win_relationship(self, mock_get_db):
        """Test creating a LEADS_TO_WIN relationship from Project to WIN."""
        # Mock setup
        mock_session = MagicMock()
        mock_tx = MagicMock()
        mock_result = MagicMock()
        mock_record = MagicMock()
        
        mock_record.__getitem__.side_effect = lambda key: self.project_win_relationship.get(key)
        mock_result.single.return_value = mock_record
        mock_tx.run.return_value = mock_result
        
        mock_session.execute_write = Mock(return_value=Relationship(**self.project_win_relationship))
        mock_get_db.return_value.session.return_value.__enter__.return_value = mock_session
        
        # Create relationship properties
        rel_props = {
            "relationshipId": self.project_win_relationship["relationshipId"],
            "contributionLevel": self.project_win_relationship["contributionLevel"],
            "directContribution": self.project_win_relationship["directContribution"]
        }
        
        # Execute test
        result = self.service.create_relationship(
            source_id=self.project_id,
            source_type=TargetEntityTypeEnum.PROJECT,
            target_id=self.win_id,
            target_type=TargetEntityTypeEnum.WIN,
            relationship_type="LEADS_TO_WIN",
            relationship_properties=rel_props
        )
        
        # Assertions
        assert result is not None
        assert result.source_id == self.project_id
        assert result.source_type == "Project"
        assert result.target_id == self.win_id
        assert result.target_type == "Win"
        assert result.type == "LEADS_TO_WIN"
        
        # Verify mock was called correctly
        mock_session.execute_write.assert_called_once()
    
    @patch('trm_api.services.relationship_service.RelationshipService._get_db')
    def test_create_event_leads_to_win_relationship(self, mock_get_db):
        """Test creating a LEADS_TO_WIN relationship from Event to WIN."""
        # Mock setup
        mock_session = MagicMock()
        mock_tx = MagicMock()
        mock_result = MagicMock()
        mock_record = MagicMock()
        
        mock_record.__getitem__.side_effect = lambda key: self.event_win_relationship.get(key)
        mock_result.single.return_value = mock_record
        mock_tx.run.return_value = mock_result
        
        mock_session.execute_write = Mock(return_value=Relationship(**self.event_win_relationship))
        mock_get_db.return_value.session.return_value.__enter__.return_value = mock_session
        
        # Create relationship properties
        rel_props = {
            "relationshipId": self.event_win_relationship["relationshipId"],
            "contributionLevel": self.event_win_relationship["contributionLevel"],
            "directContribution": self.event_win_relationship["directContribution"]
        }
        
        # Execute test
        result = self.service.create_relationship(
            source_id=self.event_id,
            source_type=TargetEntityTypeEnum.EVENT,
            target_id=self.win_id,
            target_type=TargetEntityTypeEnum.WIN,
            relationship_type="LEADS_TO_WIN",
            relationship_properties=rel_props
        )
        
        # Assertions
        assert result is not None
        assert result.source_id == self.event_id
        assert result.source_type == "Event"
        assert result.target_id == self.win_id
        assert result.target_type == "Win"
        assert result.type == "LEADS_TO_WIN"
        
        # Verify mock was called correctly
        mock_session.execute_write.assert_called_once()
    
    @patch('trm_api.services.relationship_service.RelationshipService._get_db')
    def test_get_wins_from_project(self, mock_get_db):
        """Test getting WINs led by a Project."""
        # Mock setup
        mock_session = MagicMock()
        mock_relationships = [Relationship(**self.project_win_relationship)]
        
        mock_session.read_transaction = Mock(return_value=mock_relationships)
        mock_get_db.return_value.session.return_value.__enter__.return_value = mock_session
        
        # Execute test
        results = self.service.get_relationships(
            entity_id=self.project_id,
            entity_type=TargetEntityTypeEnum.PROJECT,
            direction="outgoing",
            relationship_type="LEADS_TO_WIN",
            related_entity_type=TargetEntityTypeEnum.WIN
        )
        
        # Assertions
        assert len(results) == 1
        assert results[0].source_id == self.project_id
        assert results[0].target_id == self.win_id
        assert results[0].type == "LEADS_TO_WIN"
        
        # Verify mock was called correctly
        mock_session.read_transaction.assert_called_once()
    
    @patch('trm_api.services.relationship_service.RelationshipService._get_db')
    def test_get_wins_from_event(self, mock_get_db):
        """Test getting WINs led by an Event."""
        # Mock setup
        mock_session = MagicMock()
        mock_relationships = [Relationship(**self.event_win_relationship)]
        
        mock_session.read_transaction = Mock(return_value=mock_relationships)
        mock_get_db.return_value.session.return_value.__enter__.return_value = mock_session
        
        # Execute test
        results = self.service.get_relationships(
            entity_id=self.event_id,
            entity_type=TargetEntityTypeEnum.EVENT,
            direction="outgoing",
            relationship_type="LEADS_TO_WIN",
            related_entity_type=TargetEntityTypeEnum.WIN
        )
        
        # Assertions
        assert len(results) == 1
        assert results[0].source_id == self.event_id
        assert results[0].target_id == self.win_id
        assert results[0].type == "LEADS_TO_WIN"
        
        # Verify mock was called correctly
        mock_session.read_transaction.assert_called_once()
    
    @patch('trm_api.services.relationship_service.RelationshipService._get_db')
    def test_get_projects_events_leading_to_win(self, mock_get_db):
        """Test getting Projects and Events leading to a WIN."""
        # Mock setup
        mock_session = MagicMock()
        mock_relationships = [
            Relationship(**self.project_win_relationship), 
            Relationship(**self.event_win_relationship)
        ]
        
        mock_session.read_transaction = Mock(return_value=mock_relationships)
        mock_get_db.return_value.session.return_value.__enter__.return_value = mock_session
        
        # Execute test
        results = self.service.get_relationships(
            entity_id=self.win_id,
            entity_type=TargetEntityTypeEnum.WIN,
            direction="incoming",
            relationship_type="LEADS_TO_WIN"
        )
        
        # Assertions
        assert len(results) == 2
        assert results[0].source_id == self.project_id
        assert results[1].source_id == self.event_id
        assert results[0].target_id == self.win_id
        assert results[1].target_id == self.win_id
        assert results[0].type == "LEADS_TO_WIN"
        assert results[1].type == "LEADS_TO_WIN"
        
        # Verify mock was called correctly
        mock_session.read_transaction.assert_called_once()
    
    @patch('trm_api.services.relationship_service.RelationshipService._get_db')
    def test_delete_leads_to_win_relationship(self, mock_get_db):
        """Test deleting a LEADS_TO_WIN relationship."""
        # Mock setup
        mock_session = MagicMock()
        mock_summary = MagicMock()
        mock_summary.counters.relationships_deleted = 1
        
        mock_result = MagicMock()
        mock_result.consume.return_value = mock_summary
        
        mock_tx = MagicMock()
        mock_tx.run.return_value = mock_result
        
        mock_session.execute_write = Mock(return_value=True)
        mock_get_db.return_value.session.return_value.__enter__.return_value = mock_session
        
        # Execute test
        result = self.service.delete_relationship(
            source_id=self.project_id,
            source_type=TargetEntityTypeEnum.PROJECT,
            target_id=self.win_id,
            target_type=TargetEntityTypeEnum.WIN,
            relationship_type="LEADS_TO_WIN"
        )
        
        # Assertions
        assert result is True
        
        # Verify mock was called correctly
        mock_session.execute_write.assert_called_once()
    
    @patch('trm_api.services.relationship_service.RelationshipService._get_db')
    def test_delete_leads_to_win_relationship_not_found(self, mock_get_db):
        """Test deleting a non-existent LEADS_TO_WIN relationship."""
        # Mock setup
        mock_session = MagicMock()
        mock_summary = MagicMock()
        mock_summary.counters.relationships_deleted = 0
        
        mock_result = MagicMock()
        mock_result.consume.return_value = mock_summary
        
        mock_tx = MagicMock()
        mock_tx.run.return_value = mock_result
        
        mock_session.execute_write = Mock(return_value=False)
        mock_get_db.return_value.session.return_value.__enter__.return_value = mock_session
        
        # Execute test
        result = self.service.delete_relationship(
            source_id=self.project_id,
            source_type=TargetEntityTypeEnum.PROJECT,
            target_id=self.win_id,
            target_type=TargetEntityTypeEnum.WIN,
            relationship_type="LEADS_TO_WIN"
        )
        
        # Assertions
        assert result is False
        
        # Verify mock was called correctly
        mock_session.execute_write.assert_called_once()
