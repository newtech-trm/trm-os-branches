from neo4j import Driver
from typing import List, Optional
from datetime import datetime

from trm_api.db.session import get_driver
from trm_api.models.agent import Agent, AgentCreate, AgentUpdate, AgentInDB

class AgentService:
    """
    Service layer for handling business logic related to Agents.
    """

    def _get_db(self) -> Driver:
        return get_driver()

    def create_agent(self, agent_create: AgentCreate) -> Agent:
        """Creates a new Agent node."""
        agent_db = AgentInDB(**agent_create.model_dump())
        params = agent_db.model_dump(by_alias=True)

        with self._get_db().session() as session:
            result = session.write_transaction(self._create_agent_tx, params)
            return Agent(**result)

    @staticmethod
    def _create_agent_tx(tx, params: dict) -> dict:
        query = (
            "CREATE (a:Agent { "
            "  agentId: $agentId, "
            "  name: $name, "
            "  description: $description, "
            "  version: $version, "
            "  type: $type, "
            "  status: $status, "
            "  createdAt: datetime($createdAt), "
            "  updatedAt: null "
            "}) "
            "RETURN a"
        )
        result = tx.run(query, params)
        record = result.single()
        return dict(record['a']) if record and record['a'] else None

    def get_agent_by_id(self, agent_id: str) -> Optional[Agent]:
        """Retrieves a single agent by its unique ID."""
        with self._get_db().session() as session:
            result = session.read_transaction(self._get_agent_by_id_tx, agent_id)
            return Agent(**result) if result else None

    @staticmethod
    def _get_agent_by_id_tx(tx, agent_id: str) -> Optional[dict]:
        query = "MATCH (a:Agent {agentId: $agentId}) RETURN a"
        result = tx.run(query, agentId=agent_id)
        record = result.single()
        return dict(record['a']) if record and record['a'] else None

    def list_agents(self, skip: int = 0, limit: int = 100) -> List[Agent]:
        """Retrieves a list of agents with pagination."""
        with self._get_db().session() as session:
            results = session.read_transaction(self._list_agents_tx, skip, limit)
            return [Agent(**result) for result in results]

    @staticmethod
    def _list_agents_tx(tx, skip: int, limit: int) -> List[dict]:
        query = (
            "MATCH (a:Agent) "
            "RETURN a "
            "ORDER BY a.name ASC "
            "SKIP $skip LIMIT $limit"
        )
        result = tx.run(query, skip=skip, limit=limit)
        return [dict(record['a']) for record in result]

    def update_agent(self, agent_id: str, agent_update: AgentUpdate) -> Optional[Agent]:
        """Updates an existing agent."""
        update_data = agent_update.model_dump(exclude_unset=True, by_alias=True)
        if not update_data:
            return self.get_agent_by_id(agent_id)

        update_data['updatedAt'] = datetime.utcnow()

        with self._get_db().session() as session:
            result = session.write_transaction(self._update_agent_tx, agent_id, update_data)
            return Agent(**result) if result else None

    @staticmethod
    def _update_agent_tx(tx, agent_id: str, update_data: dict) -> Optional[dict]:
        set_clauses = [f"a.{key} = ${key}" for key in update_data.keys()]
        if 'updatedAt' in update_data:
            set_clauses.remove('a.updatedAt = $updatedAt')
            set_clauses.append('a.updatedAt = datetime($updatedAt)')

        query = (
            f"MATCH (a:Agent {{agentId: $agentId}}) "
            f"SET {', '.join(set_clauses)} "
            "RETURN a"
        )
        params = {'agentId': agent_id, **update_data}
        result = tx.run(query, params)
        record = result.single()
        return dict(record['a']) if record and record['a'] else None

    def delete_agent(self, agent_id: str) -> bool:
        """Deletes an agent by its ID."""
        with self._get_db().session() as session:
            result = session.write_transaction(self._delete_agent_tx, agent_id)
            return result

    @staticmethod
    def _delete_agent_tx(tx, agent_id: str) -> bool:
        query = "MATCH (a:Agent {agentId: $agentId}) DETACH DELETE a"
        result = tx.run(query, agentId=agent_id)
        summary = result.consume()
        return summary.counters.nodes_deleted > 0

# Singleton instance of the service
agent_service = AgentService()
