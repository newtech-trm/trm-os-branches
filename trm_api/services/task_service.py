from neo4j import Driver
from typing import Optional, List
from datetime import datetime

from trm_api.db.session import get_driver
from trm_api.models.task import Task, TaskCreate, TaskUpdate, TaskInDB
from trm_api.models.relationships import Relationship, RelationshipType, TargetEntityTypeEnum

class TaskService:
    """
    Service layer for handling business logic related to Tasks.
    """

    def _get_db(self) -> Driver:
        return get_driver()

    def create_task_for_tension(self, task_create: TaskCreate) -> Optional[Task]:
        """
        Creates a new Task node and links it to an existing Tension.
        """
        task_db = TaskInDB(**task_create.model_dump(exclude={"tension_id"}))
        params = task_db.model_dump(by_alias=True)
        params['tensionId'] = task_create.tension_id

        with self._get_db().session() as session:
            result = session.write_transaction(self._create_task_tx, params)
            if result:
                return Task(**result)
            return None

    @staticmethod
    def _create_task_tx(tx, params: dict) -> Optional[dict]:
        """
        Transaction function to create a task and the relationship to its tension.
        """
        query = (
            "MATCH (ten:Tension {tensionId: $tensionId}) "
            "CREATE (task:Task { "
            "  taskId: $taskId, "
            "  name: $name, "
            "  description: $description, "
            "  status: $status, "
            "  effort: $effort, "
            "  createdAt: datetime($createdAt), "
            "  updatedAt: null, "
            "  completedAt: null "
            "}) "
            "CREATE (ten)-[:DECOMPOSED_INTO]->(task) "
            "RETURN task"
        )

        result = tx.run(query, params)
        record = result.single()
        return dict(record['task']) if record and record['task'] else None

    def list_tasks_for_tension(self, tension_id: str, skip: int = 0, limit: int = 100) -> List[Task]:
        """
        Retrieves a list of tasks for a specific tension.
        """
        with self._get_db().session() as session:
            results = session.read_transaction(self._list_tasks_tx, tension_id, skip, limit)
            return [Task(**result) for result in results]

    @staticmethod
    def _list_tasks_tx(tx, tension_id: str, skip: int, limit: int) -> List[dict]:
        query = (
            "MATCH (t:Tension {tensionId: $tensionId})-[:DECOMPOSED_INTO]->(task:Task) "
            "RETURN task "
            "ORDER BY task.status, task.createdAt DESC "
            "SKIP $skip LIMIT $limit"
        )
        result = tx.run(query, tensionId=tension_id, skip=skip, limit=limit)
        return [dict(record['task']) for record in result]

    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """
        Retrieves a single task by its unique ID.
        """
        with self._get_db().session() as session:
            result = session.read_transaction(self._get_task_by_id_tx, task_id)
            if result:
                return Task(**result)
            return None

    @staticmethod
    def _get_task_by_id_tx(tx, task_id: str) -> Optional[dict]:
        query = "MATCH (task:Task {taskId: $taskId}) RETURN task"
        result = tx.run(query, taskId=task_id)
        record = result.single()
        return dict(record['task']) if record and record['task'] else None

    def update_task(self, task_id: str, task_update: TaskUpdate) -> Optional[Task]:
        """
        Updates an existing task.
        """
        update_data = task_update.model_dump(exclude_unset=True)
        if not update_data:
            return self.get_task_by_id(task_id)

        update_data['updatedAt'] = datetime.utcnow()
        if update_data.get("status") == "done":
            update_data['completedAt'] = datetime.utcnow()

        with self._get_db().session() as session:
            result = session.write_transaction(self._update_task_tx, task_id, update_data)
            if result:
                return Task(**result)
            return None

    @staticmethod
    def _update_task_tx(tx, task_id: str, update_data: dict) -> Optional[dict]:
        set_clauses = [f"task.{key} = ${key}" for key in update_data.keys()]
        for key in ['updatedAt', 'completedAt']:
             if key in update_data:
                set_clauses.remove(f'task.{key} = ${key}')
                set_clauses.append(f'task.{key} = datetime(${key})')

        query = (
            f"MATCH (task:Task {{taskId: $taskId}}) "
            f"SET {', '.join(set_clauses)} "
            "RETURN task"
        )
        params = {'taskId': task_id, **update_data}
        result = tx.run(query, params)
        record = result.single()
        return dict(record['task']) if record and record['task'] else None

    def delete_task(self, task_id: str) -> bool:
        """
        Deletes a task by its ID.
        """
        with self._get_db().session() as session:
            result = session.write_transaction(self._delete_task_tx, task_id)
            return result

    @staticmethod
    def _delete_task_tx(tx, task_id: str) -> bool:
        query = "MATCH (task:Task {taskId: $taskId}) DETACH DELETE task"
        result = tx.run(query, taskId=task_id)
        return result.consume().counters.nodes_deleted > 0

    def assign_task_to_user(self, task_id: str, user_id: str) -> Optional[Relationship]:
        """Assigns a task to a user, creating a PERFORMS relationship."""
        with self._get_db().session() as session:
            result = session.write_transaction(self._assign_task_to_user_tx, task_id, user_id)
            return Relationship(**result) if result else None

    @staticmethod
    def _assign_task_to_user_tx(tx, task_id: str, user_id: str) -> Optional[dict]:
        query = (
            "MATCH (u:User {userId: $userId}) "
            "MATCH (t:Task {taskId: $taskId}) "
            "MERGE (u)-[r:PERFORMS]->(t) "
            "ON CREATE SET r.createdAt = datetime() "
            "RETURN "
            "    u.userId AS source_id, "
            "    labels(u)[0] AS source_type, "
            "    t.taskId AS target_id, "
            "    labels(t)[0] AS target_type, "
            "    type(r) AS type, "
            "    r.createdAt as createdAt"
        )
        result = tx.run(query, userId=user_id, taskId=task_id)
        record = result.single()
        return dict(record) if record else None

# Singleton instance of the service
task_service = TaskService()
