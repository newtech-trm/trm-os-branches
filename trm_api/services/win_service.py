from neo4j import Driver
from typing import List, Optional
from datetime import datetime

from trm_api.db.session import get_driver
from trm_api.models.win import Win, WinCreate, WinUpdate, WinInDB

class WinService:
    """
    Service layer for handling business logic related to WINs.
    """

    def _get_db(self) -> Driver:
        return get_driver()

    def create_win(self, win_create: WinCreate) -> Win:
        """Creates a new WIN node."""
        win_db = WinInDB(**win_create.model_dump())
        params = win_db.model_dump(by_alias=True)

        with self._get_db().session() as session:
            result = session.write_transaction(self._create_win_tx, params)
            return Win(**result)

    @staticmethod
    def _create_win_tx(tx, params: dict) -> dict:
        query = (
            "CREATE (w:WIN { "
            "  winId: $winId, "
            "  summary: $summary, "
            "  description: $description, "
            "  winType: $winType, "
            "  relatedEntityIds: $relatedEntityIds, "
            "  createdAt: datetime($createdAt), "
            "  updatedAt: null "
            "}) "
            "RETURN w"
        )
        result = tx.run(query, params)
        record = result.single()
        return dict(record['w']) if record and record['w'] else None

    def get_win_by_id(self, win_id: str) -> Optional[Win]:
        """Retrieves a single WIN by its unique ID."""
        with self._get_db().session() as session:
            result = session.read_transaction(self._get_win_by_id_tx, win_id)
            return Win(**result) if result else None

    @staticmethod
    def _get_win_by_id_tx(tx, win_id: str) -> Optional[dict]:
        query = "MATCH (w:WIN {winId: $winId}) RETURN w"
        result = tx.run(query, winId=win_id)
        record = result.single()
        return dict(record['w']) if record and record['w'] else None

    def list_wins(self, skip: int = 0, limit: int = 25) -> List[Win]:
        """Retrieves a list of WINs with pagination."""
        with self._get_db().session() as session:
            results = session.read_transaction(self._list_wins_tx, skip, limit)
            return [Win(**result) for result in results]

    @staticmethod
    def _list_wins_tx(tx, skip: int, limit: int) -> List[dict]:
        query = (
            "MATCH (w:WIN) "
            "RETURN w "
            "ORDER BY w.createdAt DESC "
            "SKIP $skip LIMIT $limit"
        )
        result = tx.run(query, skip=skip, limit=limit)
        return [dict(record['w']) for record in result]

    def update_win(self, win_id: str, win_update: WinUpdate) -> Optional[Win]:
        """Updates an existing WIN."""
        update_data = win_update.model_dump(exclude_unset=True, by_alias=True)
        if not update_data:
            return self.get_win_by_id(win_id)

        update_data['updatedAt'] = datetime.utcnow()

        with self._get_db().session() as session:
            result = session.write_transaction(self._update_win_tx, win_id, update_data)
            return Win(**result) if result else None

    @staticmethod
    def _update_win_tx(tx, win_id: str, update_data: dict) -> Optional[dict]:
        set_clauses = [f"w.{key} = ${key}" for key in update_data.keys()]
        if 'updatedAt' in update_data:
            set_clauses.remove('w.updatedAt = $updatedAt')
            set_clauses.append('w.updatedAt = datetime($updatedAt)')

        query = (
            f"MATCH (w:WIN {{winId: $winId}}) "
            f"SET {', '.join(set_clauses)} "
            "RETURN w"
        )
        params = {'winId': win_id, **update_data}
        result = tx.run(query, params)
        record = result.single()
        return dict(record['w']) if record and record['w'] else None

    def delete_win(self, win_id: str) -> bool:
        """Deletes a WIN by its ID."""
        with self._get_db().session() as session:
            result = session.write_transaction(self._delete_win_tx, win_id)
            return result

    @staticmethod
    def _delete_win_tx(tx, win_id: str) -> bool:
        query = "MATCH (w:WIN {winId: $winId}) DETACH DELETE w"
        result = tx.run(query, winId=win_id)
        summary = result.consume()
        return summary.counters.nodes_deleted > 0

# Singleton instance of the service
win_service = WinService()
