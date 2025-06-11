from neo4j import Driver
from typing import List, Optional
from datetime import datetime

from trm_api.db.session import get_driver
from trm_api.models.knowledge_snippet import KnowledgeSnippet, KnowledgeSnippetCreate, KnowledgeSnippetUpdate, KnowledgeSnippetInDB

class KnowledgeSnippetService:
    """
    Service layer for handling business logic related to Knowledge Snippets.
    Includes versioning logic for updates.
    """

    def _get_db(self) -> Driver:
        return get_driver()

    def create_snippet(self, snippet_create: KnowledgeSnippetCreate) -> KnowledgeSnippet:
        """Creates a new KnowledgeSnippet node."""
        snippet_db = KnowledgeSnippetInDB(**snippet_create.model_dump())
        params = snippet_db.model_dump(by_alias=True)

        with self._get_db().session() as session:
            result = session.write_transaction(self._create_snippet_tx, params)
            return KnowledgeSnippet(**result)

    @staticmethod
    def _create_snippet_tx(tx, params: dict) -> dict:
        query = (
            "CREATE (ks:KnowledgeSnippet { "
            "  snippetId: $snippetId, "
            "  content: $content, "
            "  snippetType: $snippetType, "
            "  sourceEntityId: $sourceEntityId, "
            "  tags: $tags, "
            "  version: 1, " # Initial version is 1
            "  createdAt: datetime($createdAt), "
            "  updatedAt: null "
            "}) "
            "RETURN ks"
        )
        result = tx.run(query, params)
        record = result.single()
        return dict(record['ks']) if record and record['ks'] else None

    def get_snippet_by_id(self, snippet_id: str) -> Optional[KnowledgeSnippet]:
        """Retrieves a single snippet by its unique ID."""
        with self._get_db().session() as session:
            result = session.read_transaction(self._get_snippet_by_id_tx, snippet_id)
            return KnowledgeSnippet(**result) if result else None

    @staticmethod
    def _get_snippet_by_id_tx(tx, snippet_id: str) -> Optional[dict]:
        query = "MATCH (ks:KnowledgeSnippet {snippetId: $snippetId}) RETURN ks"
        result = tx.run(query, snippetId=snippet_id)
        record = result.single()
        return dict(record['ks']) if record and record['ks'] else None

    def list_snippets(self, skip: int = 0, limit: int = 100) -> List[KnowledgeSnippet]:
        """Retrieves a list of snippets with pagination."""
        with self._get_db().session() as session:
            results = session.read_transaction(self._list_snippets_tx, skip, limit)
            return [KnowledgeSnippet(**result) for result in results]

    @staticmethod
    def _list_snippets_tx(tx, skip: int, limit: int) -> List[dict]:
        query = (
            "MATCH (ks:KnowledgeSnippet) "
            "RETURN ks "
            "ORDER BY ks.createdAt DESC "
            "SKIP $skip LIMIT $limit"
        )
        result = tx.run(query, skip=skip, limit=limit)
        return [dict(record['ks']) for record in result]

    def update_snippet(self, snippet_id: str, snippet_update: KnowledgeSnippetUpdate) -> Optional[KnowledgeSnippet]:
        """Updates an existing snippet and increments its version."""
        update_data = snippet_update.model_dump(exclude_unset=True, by_alias=True)
        if not update_data:
            return self.get_snippet_by_id(snippet_id)

        update_data['updatedAt'] = datetime.utcnow()

        with self._get_db().session() as session:
            result = session.write_transaction(self._update_snippet_tx, snippet_id, update_data)
            return KnowledgeSnippet(**result) if result else None

    @staticmethod
    def _update_snippet_tx(tx, snippet_id: str, update_data: dict) -> Optional[dict]:
        set_clauses = [f"ks.{key} = ${key}" for key in update_data.keys()]
        if 'updatedAt' in update_data:
            set_clauses.remove('ks.updatedAt = $updatedAt')
            set_clauses.append('ks.updatedAt = datetime($updatedAt)')

        # Increment the version number on every update
        set_clauses.append('ks.version = ks.version + 1')

        query = (
            f"MATCH (ks:KnowledgeSnippet {{snippetId: $snippetId}}) "
            f"SET {', '.join(set_clauses)} "
            "RETURN ks"
        )
        params = {'snippetId': snippet_id, **update_data}
        result = tx.run(query, params)
        record = result.single()
        return dict(record['ks']) if record and record['ks'] else None

    def delete_snippet(self, snippet_id: str) -> bool:
        """Deletes a snippet by its ID."""
        with self._get_db().session() as session:
            result = session.write_transaction(self._delete_snippet_tx, snippet_id)
            return result

    @staticmethod
    def _delete_snippet_tx(tx, snippet_id: str) -> bool:
        query = "MATCH (ks:KnowledgeSnippet {snippetId: $snippetId}) DETACH DELETE ks"
        result = tx.run(query, snippetId=snippet_id)
        summary = result.consume()
        return summary.counters.nodes_deleted > 0

# Singleton instance of the service
knowledge_snippet_service = KnowledgeSnippetService()
