from neo4j import Driver
from typing import List, Optional
from datetime import datetime

from trm_api.db.session import get_driver
from trm_api.models.recognition import Recognition, RecognitionCreate, RecognitionUpdate, RecognitionInDB

class RecognitionService:
    """
    Service layer for handling business logic related to Recognitions.
    This service also handles the creation of relationships associated with a recognition event.
    """

    def _get_db(self) -> Driver:
        return get_driver()

    def create_recognition(self, recognition_create: RecognitionCreate) -> Optional[Recognition]:
        """
        Creates a new Recognition node and its relationships to the WIN, Granter, and Recipients.
        """
        recognition_db = RecognitionInDB(**recognition_create.model_dump())
        params = recognition_db.model_dump(by_alias=True)

        with self._get_db().session() as session:
            result = session.write_transaction(self._create_recognition_tx, params)
            return Recognition(**result) if result else None

    @staticmethod
    def _create_recognition_tx(tx, params: dict) -> Optional[dict]:
        # This query creates a node and multiple relationships in one atomic transaction.
        query = (
            # 1. Find the WIN and the User who is granting the recognition
            "MATCH (w:WIN {winId: $winId}) "
            "MATCH (granter:User {userId: $granterUserId}) "
            
            # 2. Create the Recognition node itself
            "CREATE (r:Recognition {" 
            "  recognitionId: $recognitionId, "
            "  winId: $winId, "
            "  granterUserId: $granterUserId, "
            "  recipientUserIds: $recipientUserIds, "
            "  message: $message, "
            "  recognitionType: $recognitionType, "
            "  createdAt: datetime($createdAt)" 
            "}) "
            
            # 3. Create relationships from the Recognition to the WIN and the Granter
            "CREATE (granter)-[:GAVE_RECOGNITION]->(r) "
            "CREATE (r)-[:RECOGNIZES]->(w) "
            
            # 4. Find all recipient users and create relationships to them
            "WITH r "
            "UNWIND $recipientUserIds AS recipientId "
            "MATCH (recipient:User {userId: recipientId}) "
            "CREATE (r)-[:FOR_USER]->(recipient) "
            
            # 5. Return the created recognition node
            "RETURN r"
        )
        
        result = tx.run(query, params)
        record = result.single()
        
        # If any MATCH fails (e.g., winId or userId not found), the creation is rolled back.
        return dict(record['r']) if record and record['r'] else None

    def get_recognition_by_id(self, recognition_id: str) -> Optional[Recognition]:
        """Retrieves a single recognition by its unique ID."""
        with self._get_db().session() as session:
            result = session.read_transaction(self._get_recognition_by_id_tx, recognition_id)
            return Recognition(**result) if result else None

    @staticmethod
    def _get_recognition_by_id_tx(tx, recognition_id: str) -> Optional[dict]:
        query = "MATCH (r:Recognition {recognitionId: $recognitionId}) RETURN r"
        result = tx.run(query, recognitionId=recognition_id)
        record = result.single()
        return dict(record['r']) if record and record['r'] else None

    def list_recognitions_for_win(self, win_id: str, skip: int = 0, limit: int = 25) -> List[Recognition]:
        """Retrieves a list of recognitions for a specific WIN."""
        with self._get_db().session() as session:
            results = session.read_transaction(self._list_recognitions_for_win_tx, win_id, skip, limit)
            return [Recognition(**result) for result in results]

    @staticmethod
    def _list_recognitions_for_win_tx(tx, win_id: str, skip: int, limit: int) -> List[dict]:
        query = (
            "MATCH (r:Recognition {winId: $winId}) "
            "RETURN r "
            "ORDER BY r.createdAt DESC "
            "SKIP $skip LIMIT $limit"
        )
        result = tx.run(query, winId=win_id, skip=skip, limit=limit)
        return [dict(record['r']) for record in result]

    def update_recognition(self, recognition_id: str, recognition_update: RecognitionUpdate) -> Optional[Recognition]:
        """Updates an existing recognition (e.g., the message)."""
        update_data = recognition_update.model_dump(exclude_unset=True, by_alias=True)
        if not update_data:
            return self.get_recognition_by_id(recognition_id)

        with self._get_db().session() as session:
            result = session.write_transaction(self._update_recognition_tx, recognition_id, update_data)
            return Recognition(**result) if result else None

    @staticmethod
    def _update_recognition_tx(tx, recognition_id: str, update_data: dict) -> Optional[dict]:
        set_clauses = [f"r.{key} = ${key}" for key in update_data.keys()]
        query = (
            f"MATCH (r:Recognition {{recognitionId: $recognitionId}}) "
            f"SET {', '.join(set_clauses)} "
            "RETURN r"
        )
        params = {'recognitionId': recognition_id, **update_data}
        result = tx.run(query, params)
        record = result.single()
        return dict(record['r']) if record and record['r'] else None

    def delete_recognition(self, recognition_id: str) -> bool:
        """Deletes a recognition by its ID."""
        with self._get_db().session() as session:
            result = session.write_transaction(self._delete_recognition_tx, recognition_id)
            return result

    @staticmethod
    def _delete_recognition_tx(tx, recognition_id: str) -> bool:
        query = "MATCH (r:Recognition {recognitionId: $recognitionId}) DETACH DELETE r"
        result = tx.run(query, recognitionId=recognition_id)
        summary = result.consume()
        return summary.counters.nodes_deleted > 0

# Singleton instance of the service
recognition_service = RecognitionService()
