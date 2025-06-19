import pytest
import uuid
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from trm_api.models.relationships import Relationship, RelationshipType, TargetEntityTypeEnum
from trm_api.services.relationship_service import RelationshipService


class TestGivenByRelationship:
    """Unit tests for the GIVEN_BY relationship service methods."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.service = RelationshipService()
        
        # Sample IDs for testing
        self.agent_id = str(uuid.uuid4())
        self.recognition_id = str(uuid.uuid4())
        
        # Sample relationship data for Agent -> Recognition
        self.agent_recognition_relationship = {
            "source_id": self.agent_id,
            "source_type": "Agent",
            "target_id": self.recognition_id,
            "target_type": "Recognition",
            "type": "GIVEN_BY",
            "relationshipId": f"given_by_{self.agent_id}_{self.recognition_id}_abcd1234",
            "notes": "Test note for given recognition",
            "createdAt": datetime.utcnow()
        }
    
    @patch('trm_api.services.relationship_service.RelationshipService._get_db')
    def test_create_given_by_relationship(self, mock_get_db):
        """Test creating a GIVEN_BY relationship from Agent to Recognition."""
        # Mock setup
        mock_session = MagicMock()
        mock_tx = MagicMock()
        mock_result = MagicMock()
        mock_record = MagicMock()
        
        mock_record.__getitem__.side_effect = lambda key: self.agent_recognition_relationship.get(key)
        mock_result.single.return_value = mock_record
        mock_tx.run.return_value = mock_result
        
        mock_session.execute_write = Mock(return_value=Relationship(**self.agent_recognition_relationship))
        mock_get_db.return_value.session.return_value.__enter__.return_value = mock_session
        
        # Create relationship properties
        rel_props = {
            "relationshipId": self.agent_recognition_relationship["relationshipId"],
            "notes": self.agent_recognition_relationship["notes"]
        }
        
        # Execute test
        result = self.service.create_relationship(
            source_id=self.agent_id,
            source_type=TargetEntityTypeEnum.AGENT,
            target_id=self.recognition_id,
            target_type=TargetEntityTypeEnum.RECOGNITION,
            relationship_type="GIVEN_BY",
            relationship_properties=rel_props
        )
        
        # Assertions
        assert result is not None
        assert result.source_id == self.agent_id
        assert result.source_type == "Agent"
        assert result.target_id == self.recognition_id
        assert result.target_type == "Recognition"
        assert result.type == "GIVEN_BY"
        
        # Verify mock was called correctly
        mock_session.execute_write.assert_called_once()
    
    @patch('trm_api.services.relationship_service.RelationshipService._get_db')
    def test_get_recognitions_given_by_agent(self, mock_get_db):
        """Test getting Recognitions given by an Agent."""
        # Mock setup
        mock_session = MagicMock()
        mock_relationships = [Relationship(**self.agent_recognition_relationship)]
        
        mock_session.read_transaction = Mock(return_value=mock_relationships)
        mock_get_db.return_value.session.return_value.__enter__.return_value = mock_session
        
        # Execute test
        results = self.service.get_relationships(
            entity_id=self.agent_id,
            entity_type=TargetEntityTypeEnum.AGENT,
            direction="outgoing",
            relationship_type="GIVEN_BY",
            related_entity_type=TargetEntityTypeEnum.RECOGNITION
        )
        
        # Assertions
        assert len(results) == 1
        assert results[0].source_id == self.agent_id
        assert results[0].target_id == self.recognition_id
        assert results[0].type == "GIVEN_BY"
        
        # Verify mock was called correctly
        mock_session.read_transaction.assert_called_once()
    
    @patch('trm_api.services.relationship_service.RelationshipService._get_db')
    def test_get_agents_giving_recognition(self, mock_get_db):
        """Test getting Agents that gave a Recognition."""
        # Mock setup
        mock_session = MagicMock()
        mock_relationships = [Relationship(**self.agent_recognition_relationship)]
        
        mock_session.read_transaction = Mock(return_value=mock_relationships)
        mock_get_db.return_value.session.return_value.__enter__.return_value = mock_session
        
        # Execute test
        results = self.service.get_relationships(
            entity_id=self.recognition_id,
            entity_type=TargetEntityTypeEnum.RECOGNITION,
            direction="incoming",
            relationship_type="GIVEN_BY",
            related_entity_type=TargetEntityTypeEnum.AGENT
        )
        
        # Assertions
        assert len(results) == 1
        assert results[0].source_id == self.agent_id
        assert results[0].target_id == self.recognition_id
        assert results[0].type == "GIVEN_BY"
        
        # Verify mock was called correctly
        mock_session.read_transaction.assert_called_once()
    
    @patch('trm_api.services.relationship_service.RelationshipService._get_db')
    def test_delete_given_by_relationship(self, mock_get_db):
        """Test deleting a GIVEN_BY relationship."""
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
            source_id=self.agent_id,
            source_type=TargetEntityTypeEnum.AGENT,
            target_id=self.recognition_id,
            target_type=TargetEntityTypeEnum.RECOGNITION,
            relationship_type="GIVEN_BY"
        )
        
        # Assertions
        assert result is True
        
        # Verify mock was called correctly
        mock_session.execute_write.assert_called_once()
    
    @patch('trm_api.services.relationship_service.RelationshipService._get_db')
    def test_delete_given_by_relationship_not_found(self, mock_get_db):
        """Test deleting a non-existent GIVEN_BY relationship."""
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
            source_id=self.agent_id,
            source_type=TargetEntityTypeEnum.AGENT,
            target_id=self.recognition_id,
            target_type=TargetEntityTypeEnum.RECOGNITION,
            relationship_type="GIVEN_BY"
        )
        
        # Assertions
        assert result is False
        
        # Verify mock was called correctly
        mock_session.execute_write.assert_called_once()
