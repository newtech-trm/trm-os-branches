from neo4j import Driver
from typing import List, Optional
from datetime import datetime

from trm_api.db.session import get_driver
from trm_api.models.skill import Skill, SkillCreate, SkillUpdate, SkillInDB

class SkillService:
    """
    Service layer for handling business logic related to Skills.
    """

    def _get_db(self) -> Driver:
        return get_driver()

    def create_skill(self, skill_create: SkillCreate) -> Skill:
        """Creates a new Skill node."""
        skill_db = SkillInDB(**skill_create.model_dump())
        params = skill_db.model_dump(by_alias=True)

        with self._get_db().session() as session:
            result = session.write_transaction(self._create_skill_tx, params)
            return Skill(**result)

    @staticmethod
    def _create_skill_tx(tx, params: dict) -> dict:
        query = (
            "CREATE (s:Skill { "
            "  skillId: $skillId, "
            "  name: $name, "
            "  description: $description, "
            "  category: $category, "
            "  createdAt: datetime($createdAt), "
            "  updatedAt: null "
            "}) "
            "RETURN s"
        )
        result = tx.run(query, params)
        record = result.single()
        return dict(record['s']) if record and record['s'] else None

    def get_skill_by_id(self, skill_id: str) -> Optional[Skill]:
        """Retrieves a single skill by its unique ID."""
        with self._get_db().session() as session:
            result = session.read_transaction(self._get_skill_by_id_tx, skill_id)
            return Skill(**result) if result else None

    @staticmethod
    def _get_skill_by_id_tx(tx, skill_id: str) -> Optional[dict]:
        query = "MATCH (s:Skill {skillId: $skillId}) RETURN s"
        result = tx.run(query, skillId=skill_id)
        record = result.single()
        return dict(record['s']) if record and record['s'] else None

    def list_skills(self, skip: int = 0, limit: int = 100) -> List[Skill]:
        """Retrieves a list of skills with pagination."""
        with self._get_db().session() as session:
            results = session.read_transaction(self._list_skills_tx, skip, limit)
            return [Skill(**result) for result in results]

    @staticmethod
    def _list_skills_tx(tx, skip: int, limit: int) -> List[dict]:
        query = (
            "MATCH (s:Skill) "
            "RETURN s "
            "ORDER BY s.name ASC "
            "SKIP $skip LIMIT $limit"
        )
        result = tx.run(query, skip=skip, limit=limit)
        return [dict(record['s']) for record in result]

    def update_skill(self, skill_id: str, skill_update: SkillUpdate) -> Optional[Skill]:
        """Updates an existing skill."""
        update_data = skill_update.model_dump(exclude_unset=True, by_alias=True)
        if not update_data:
            return self.get_skill_by_id(skill_id)

        update_data['updatedAt'] = datetime.utcnow()

        with self._get_db().session() as session:
            result = session.write_transaction(self._update_skill_tx, skill_id, update_data)
            return Skill(**result) if result else None

    @staticmethod
    def _update_skill_tx(tx, skill_id: str, update_data: dict) -> Optional[dict]:
        set_clauses = [f"s.{key} = ${key}" for key in update_data.keys()]
        if 'updatedAt' in update_data:
            set_clauses.remove('s.updatedAt = $updatedAt')
            set_clauses.append('s.updatedAt = datetime($updatedAt)')

        query = (
            f"MATCH (s:Skill {{skillId: $skillId}}) "
            f"SET {', '.join(set_clauses)} "
            "RETURN s"
        )
        params = {'skillId': skill_id, **update_data}
        result = tx.run(query, params)
        record = result.single()
        return dict(record['s']) if record and record['s'] else None

    def delete_skill(self, skill_id: str) -> bool:
        """Deletes a skill by its ID."""
        with self._get_db().session() as session:
            result = session.write_transaction(self._delete_skill_tx, skill_id)
            return result

    @staticmethod
    def _delete_skill_tx(tx, skill_id: str) -> bool:
        # Note: We use DETACH DELETE to also remove any relationships connected to the skill.
        query = "MATCH (s:Skill {skillId: $skillId}) DETACH DELETE s"
        result = tx.run(query, skillId=skill_id)
        summary = result.consume()
        return summary.counters.nodes_deleted > 0

# Singleton instance of the service
skill_service = SkillService()
