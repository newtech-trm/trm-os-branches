from neo4j import Driver
from typing import Optional, List
from datetime import datetime

from trm_api.db.session import get_driver
from trm_api.models.tension import Tension, TensionCreate, TensionUpdate, TensionInDB
from trm_api.models.relationships import Relationship

class TensionService:
    """
    Service layer for handling business logic related to Tensions.
    """

    def _get_db(self) -> Driver:
        return get_driver()

    def create_tension_for_project(self, tension_create: TensionCreate) -> Optional[Tension]:
        """
        Creates a new Tension node and links it to an existing Project.

        Args:
            tension_create: Pydantic model with tension data and the project_id.

        Returns:
            The newly created tension, or None if the project doesn't exist.
        """
        tension_db = TensionInDB(**tension_create.model_dump(exclude={"project_id"}))
        params = tension_db.model_dump(by_alias=True)
        params['projectId'] = tension_create.project_id

        with self._get_db().session() as session:
            result = session.write_transaction(self._create_tension_tx, params)
            if result:
                return Tension(**result)
            return None

    @staticmethod
    def _create_tension_tx(tx, params: dict) -> Optional[dict]:
        """
        Transaction function to create a tension and the relationship to its project.
        """
        query = (
            "MATCH (proj:Project {projectId: $projectId}) "
            "CREATE (t:Tension { "
            "  tensionId: $tensionId, "
            "  summary: $summary, "
            "  description: $description, "
            "  status: $status, "
            "  priority: $priority, "
            "  createdAt: datetime($createdAt), "
            "  updatedAt: null "
            "}) "
            "CREATE (proj)-[:RAISES]->(t) "
            "RETURN t"
        )

        result = tx.run(query, params)
        record = result.single()
        if record and record['t']:
            return dict(record['t'])
        return None # This will happen if the project is not found

    def list_tensions_for_project(self, project_id: str, skip: int = 0, limit: int = 100) -> List[Tension]:
        """
        Retrieves a list of tensions for a specific project.
        """
        with self._get_db().session() as session:
            results = session.read_transaction(self._list_tensions_tx, project_id, skip, limit)
            return [Tension(**result) for result in results]

    @staticmethod
    def _list_tensions_tx(tx, project_id: str, skip: int, limit: int) -> List[dict]:
        """
        Transaction function to list tensions for a project.
        """
        query = (
            "MATCH (p:Project {projectId: $projectId})-[:RAISES]->(t:Tension) "
            "RETURN t "
            "ORDER BY t.priority, t.createdAt DESC "
            "SKIP $skip LIMIT $limit"
        )
        result = tx.run(query, projectId=project_id, skip=skip, limit=limit)
        return [dict(record['t']) for record in result]

    def get_tension_by_id(self, tension_id: str) -> Optional[Tension]:
        """
        Retrieves a single tension by its unique ID.
        """
        with self._get_db().session() as session:
            result = session.read_transaction(self._get_tension_by_id_tx, tension_id)
            if result:
                return Tension(**result)
            return None

    @staticmethod
    def _get_tension_by_id_tx(tx, tension_id: str) -> Optional[dict]:
        query = "MATCH (t:Tension {tensionId: $tensionId}) RETURN t"
        result = tx.run(query, tensionId=tension_id)
        record = result.single()
        return dict(record['t']) if record and record['t'] else None

    def update_tension(self, tension_id: str, tension_update: TensionUpdate) -> Optional[Tension]:
        """
        Updates an existing tension.
        """
        update_data = tension_update.model_dump(exclude_unset=True)
        if not update_data:
            return self.get_tension_by_id(tension_id)

        update_data['updatedAt'] = datetime.utcnow()

        with self._get_db().session() as session:
            result = session.write_transaction(self._update_tension_tx, tension_id, update_data)
            if result:
                return Tension(**result)
            return None

    @staticmethod
    def _update_tension_tx(tx, tension_id: str, update_data: dict) -> Optional[dict]:
        set_clauses = [f"t.{key} = ${key}" for key in update_data.keys()]
        if 'updatedAt' in update_data:
            set_clauses.remove('t.updatedAt = $updatedAt')
            set_clauses.append('t.updatedAt = datetime($updatedAt)')

        query = (
            f"MATCH (t:Tension {{tensionId: $tensionId}}) "
            f"SET {', '.join(set_clauses)} "
            "RETURN t"
        )
        params = {'tensionId': tension_id, **update_data}
        result = tx.run(query, params)
        record = result.single()
        return dict(record['t']) if record and record['t'] else None

    def delete_tension(self, tension_id: str) -> bool:
        """
        Deletes a tension by its ID.
        """
        with self._get_db().session() as session:
            result = session.write_transaction(self._delete_tension_tx, tension_id)
            return result

    @staticmethod
    def _delete_tension_tx(tx, tension_id: str) -> bool:
        query = "MATCH (t:Tension {tensionId: $tensionId}) DETACH DELETE t"
        result = tx.run(query, tensionId=tension_id)
        return result.consume().counters.nodes_deleted > 0

    def identify_tension_by_user(self, tension_id: str, user_id: str) -> Optional[Relationship]:
        """Creates an IDENTIFIED relationship from a User to a Tension."""
        with self._get_db().session() as session:
            result = session.write_transaction(self._identify_tension_by_user_tx, tension_id, user_id)
            return Relationship(**result) if result else None

    @staticmethod
    def _identify_tension_by_user_tx(tx, tension_id: str, user_id: str) -> Optional[dict]:
        query = (
            "MATCH (u:User {userId: $userId}) "
            "MATCH (t:Tension {tensionId: $tensionId}) "
            "MERGE (u)-[r:IDENTIFIED]->(t) "
            "ON CREATE SET r.createdAt = datetime() "
            "RETURN "
            "    u.userId AS source_id, "
            "    labels(u)[0] AS source_type, "
            "    t.tensionId AS target_id, "
            "    labels(t)[0] AS target_type, "
            "    type(r) AS type, "
            "    r.createdAt as createdAt"
        )
        result = tx.run(query, userId=user_id, tensionId=tension_id)
        record = result.single()
        return dict(record) if record else None

# Singleton instance of the service
tension_service = TensionService()
