from neo4j import Driver
from typing import List, Optional
from datetime import datetime

from trm_api.db.session import get_driver
from trm_api.models.project import Project, ProjectCreate, ProjectUpdate, ProjectInDB
from trm_api.services.utils import process_record, process_records, process_relationship_record
from trm_api.models.relationships import Relationship

class ProjectService:
    """
    Service layer for handling business logic related to Projects.
    It encapsulates the Cypher queries for CRUD operations.
    """

    def _get_db(self) -> Driver:
        """Utility to get the database driver."""
        return get_driver()

    def create_project(self, project_create: ProjectCreate) -> Project:
        """
        Creates a new Project node in the Neo4j database.

        Args:
            project_create: A Pydantic model with the data for the new project.

        Returns:
            The newly created project, including system-generated fields.
        """
        # Create an instance of the database model, which includes generating uuid and timestamps
        project_db = ProjectInDB(**project_create.model_dump())
        
        # Convert the Pydantic model to a dictionary for the Cypher query
        # We use `by_alias=True` to get the camelCase keys for the database
        params = project_db.model_dump(by_alias=True)

        with self._get_db().session() as session:
            result = session.write_transaction(self._create_project_tx, params)
            return Project(**result) if result else None

    @staticmethod
    def _create_project_tx(tx, params: dict) -> dict:
        """
        The actual transaction function to create a project.
        """
        query = (
            "CREATE (p:Project { "
            "  projectId: $projectId, "
            "  title: $title, "
            "  description: $description, "
            "  status: $status, "
            "  createdAt: datetime($createdAt), "
            "  updatedAt: $updatedAt "
            "}) "
            "RETURN p"
        )
        
        # Parameters need to have their datetime objects converted to ISO format strings
        # if they are not already, but our model handles it.
        # The `datetime()` function in Cypher will parse the ISO 8601 string.
        
        result = tx.run(query, params)
        record = result.single()
        return process_record(record)

    def get_project_by_id(self, project_id: str) -> Optional[Project]:
        """
        Retrieves a single project by its unique ID.
        """
        with self._get_db().session() as session:
            result = session.read_transaction(self._get_project_by_id_tx, project_id)
            if result:
                return Project(**result)
            return None

    @staticmethod
    def _get_project_by_id_tx(tx, project_id: str) -> Optional[dict]:
        """
        Transaction function to get a project by ID.
        """
        query = "MATCH (p:Project {projectId: $projectId}) RETURN p"
        result = tx.run(query, projectId=project_id)
        record = result.single()
        return process_record(record)

    def list_projects(self, skip: int = 0, limit: int = 100) -> List[Project]:
        """
        Retrieves a list of projects with pagination.
        """
        with self._get_db().session() as session:
            results = session.read_transaction(self._list_projects_tx, skip, limit)
            return [Project(**result) for result in results if result]

    @staticmethod
    def _list_projects_tx(tx, skip: int, limit: int) -> List[dict]:
        """
        Transaction function to list projects.
        """
        query = (
            "MATCH (p:Project) "
            "RETURN p "
            "ORDER BY p.createdAt DESC "
            "SKIP $skip LIMIT $limit"
        )
        result = tx.run(query, skip=skip, limit=limit)
        # process_records will handle the conversion for each record in the list
        return [process_record(record) for record in result]

    def update_project(self, project_id: str, project_update: ProjectUpdate) -> Optional[Project]:
        """
        Updates an existing project.
        """
        # Get the fields to update from the Pydantic model
        update_data = project_update.model_dump(exclude_unset=True)
        if not update_data:
            # If there's nothing to update, we can return the existing project
            return self.get_project_by_id(project_id)

        # Add the updatedAt timestamp
        update_data['updatedAt'] = datetime.utcnow()

        with self._get_db().session() as session:
            result = session.write_transaction(self._update_project_tx, project_id, update_data)
            if result:
                return Project(**result)
            return None

    @staticmethod
    def _update_project_tx(tx, project_id: str, update_data: dict) -> Optional[dict]:
        """
        Transaction function to update a project.
        """
        # Build the SET part of the query dynamically
        set_clauses = [f"p.{key} = ${key}" for key in update_data.keys()]
        # Special handling for datetime
        if 'updatedAt' in update_data:
            set_clauses.remove('p.updatedAt = $updatedAt')
            set_clauses.append('p.updatedAt = datetime($updatedAt)')

        query = (
            f"MATCH (p:Project {{projectId: $projectId}}) "
            f"SET {', '.join(set_clauses)} "
            "RETURN p"
        )
        
        params = {'projectId': project_id, **update_data}
        
        result = tx.run(query, params)
        record = result.single()
        return process_record(record)

    def delete_project(self, project_id: str) -> bool:
        """
        Deletes a project by its ID.
        Returns True if deleted, False otherwise.
        """
        with self._get_db().session() as session:
            result = session.write_transaction(self._delete_project_tx, project_id)
            return result

    @staticmethod
    def _delete_project_tx(tx, project_id: str) -> bool:
        """
        Transaction function to delete a project.
        """
        query = "MATCH (p:Project {projectId: $projectId}) DETACH DELETE p"
        result = tx.run(query, projectId=project_id)
        summary = result.consume()
        return summary.counters.nodes_deleted > 0

    def add_participant_to_project(self, project_id: str, user_id: str) -> Optional[Relationship]:
        """Adds a user as a participant to a project, creating a HAS_PARTICIPANT relationship."""
        with self._get_db().session() as session:
            result = session.write_transaction(self._add_participant_to_project_tx, project_id, user_id)
            return Relationship(**result) if result else None

    @staticmethod
    def _add_participant_to_project_tx(tx, project_id: str, user_id: str) -> Optional[dict]:
        query = (
            "MATCH (p:Project {projectId: $projectId}) "
            "MATCH (u:User {userId: $userId}) "
            "MERGE (p)-[r:HAS_PARTICIPANT]->(u) "
            "ON CREATE SET r.createdAt = datetime() "
            "RETURN "
            "    p.projectId AS source_id, "
            "    labels(p)[0] AS source_type, "
            "    u.userId AS target_id, "
            "    labels(u)[0] AS target_type, "
            "    type(r) AS type, "
            "    r.createdAt as createdAt"
        )
        result = tx.run(query, projectId=project_id, userId=user_id)
        record = result.single()
        return process_relationship_record(record)

# Singleton instance of the service
project_service = ProjectService()
