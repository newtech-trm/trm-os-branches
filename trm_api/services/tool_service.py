from neo4j import Driver
from typing import List, Optional
from datetime import datetime

from trm_api.db.session import get_driver
from trm_api.models.tool import Tool, ToolCreate, ToolUpdate, ToolInDB

class ToolService:
    """
    Service layer for handling business logic related to Tools.
    """

    def _get_db(self) -> Driver:
        return get_driver()

    def create_tool(self, tool_create: ToolCreate) -> Tool:
        """Creates a new Tool node."""
        tool_db = ToolInDB(**tool_create.model_dump())
        params = tool_db.model_dump(by_alias=True)
        
        # Convert dict to JSON string for storage
        params['invocationDetails'] = str(params.get('invocationDetails', '{}'))

        with self._get_db().session() as session:
            result = session.write_transaction(self._create_tool_tx, params)
            return Tool(**result)

    @staticmethod
    def _create_tool_tx(tx, params: dict) -> dict:
        query = (
            "CREATE (t:Tool { "
            "  toolId: $toolId, "
            "  name: $name, "
            "  description: $description, "
            "  type: $type, "
            "  invocationDetails: $invocationDetails, "
            "  createdAt: datetime($createdAt), "
            "  updatedAt: null "
            "}) "
            "RETURN t"
        )
        result = tx.run(query, params)
        record = result.single()
        return dict(record['t']) if record and record['t'] else None

    def get_tool_by_id(self, tool_id: str) -> Optional[Tool]:
        """Retrieves a single tool by its unique ID."""
        with self._get_db().session() as session:
            result = session.read_transaction(self._get_tool_by_id_tx, tool_id)
            return Tool(**result) if result else None

    @staticmethod
    def _get_tool_by_id_tx(tx, tool_id: str) -> Optional[dict]:
        query = "MATCH (t:Tool {toolId: $toolId}) RETURN t"
        result = tx.run(query, toolId=tool_id)
        record = result.single()
        return dict(record['t']) if record and record['t'] else None

    def list_tools(self, skip: int = 0, limit: int = 100) -> List[Tool]:
        """Retrieves a list of tools with pagination."""
        with self._get_db().session() as session:
            results = session.read_transaction(self._list_tools_tx, skip, limit)
            return [Tool(**result) for result in results]

    @staticmethod
    def _list_tools_tx(tx, skip: int, limit: int) -> List[dict]:
        query = (
            "MATCH (t:Tool) "
            "RETURN t "
            "ORDER BY t.name ASC "
            "SKIP $skip LIMIT $limit"
        )
        result = tx.run(query, skip=skip, limit=limit)
        return [dict(record['t']) for record in result]

    def update_tool(self, tool_id: str, tool_update: ToolUpdate) -> Optional[Tool]:
        """Updates an existing tool."""
        update_data = tool_update.model_dump(exclude_unset=True, by_alias=True)
        if not update_data:
            return self.get_tool_by_id(tool_id)

        update_data['updatedAt'] = datetime.utcnow()
        if 'invocationDetails' in update_data:
            update_data['invocationDetails'] = str(update_data['invocationDetails'])

        with self._get_db().session() as session:
            result = session.write_transaction(self._update_tool_tx, tool_id, update_data)
            return Tool(**result) if result else None

    @staticmethod
    def _update_tool_tx(tx, tool_id: str, update_data: dict) -> Optional[dict]:
        set_clauses = [f"t.{key} = ${key}" for key in update_data.keys()]
        if 'updatedAt' in update_data:
            set_clauses.remove('t.updatedAt = $updatedAt')
            set_clauses.append('t.updatedAt = datetime($updatedAt)')

        query = (
            f"MATCH (t:Tool {{toolId: $toolId}}) "
            f"SET {', '.join(set_clauses)} "
            "RETURN t"
        )
        params = {'toolId': tool_id, **update_data}
        result = tx.run(query, params)
        record = result.single()
        return dict(record['t']) if record and record['t'] else None

    def delete_tool(self, tool_id: str) -> bool:
        """Deletes a tool by its ID."""
        with self._get_db().session() as session:
            result = session.write_transaction(self._delete_tool_tx, tool_id)
            return result

    @staticmethod
    def _delete_tool_tx(tx, tool_id: str) -> bool:
        query = "MATCH (t:Tool {toolId: $toolId}) DETACH DELETE t"
        result = tx.run(query, toolId=tool_id)
        summary = result.consume()
        return summary.counters.nodes_deleted > 0

# Singleton instance of the service
tool_service = ToolService()
