from neo4j import Driver
from typing import List, Optional
from datetime import datetime

from trm_api.db.session import get_driver
from trm_api.models.user import User, UserCreate, UserUpdate, UserInDB
from trm_api.services.utils import process_record, process_records

class UserService:
    """
    Service layer for handling business logic related to Users.
    """

    def _get_db(self) -> Driver:
        return get_driver()

    def create_user(self, user_create: UserCreate) -> User:
        """Creates a new User node."""
        # In a real app, you'd hash the password here before saving.
        user_db = UserInDB(**user_create.model_dump())
        params = user_db.model_dump(by_alias=True)

        with self._get_db().session() as session:
            result = session.write_transaction(self._create_user_tx, params)
            return User(**result) if result else None

    @staticmethod
    def _create_user_tx(tx, params: dict) -> dict:
        query = (
            "CREATE (u:User { "
            "  userId: $userId, "
            "  email: $email, "
            "  fullName: $fullName, "
            "  isActive: $isActive, "
            "  createdAt: datetime($createdAt), "
            "  updatedAt: datetime($updatedAt) "
            "}) "
            "RETURN u"
        )
        result = tx.run(query, params)
        record = result.single()
        return process_record(record)

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Retrieves a single user by its unique ID."""
        with self._get_db().session() as session:
            result = session.read_transaction(self._get_user_by_id_tx, user_id)
            return User(**result) if result else None

    @staticmethod
    def _get_user_by_id_tx(tx, user_id: str) -> Optional[dict]:
        query = "MATCH (u:User {userId: $userId}) RETURN u"
        result = tx.run(query, userId=user_id)
        record = result.single()
        return process_record(record)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Retrieves a single user by their email address."""
        with self._get_db().session() as session:
            result = session.read_transaction(self._get_user_by_email_tx, email)
            return User(**result) if result else None

    @staticmethod
    def _get_user_by_email_tx(tx, email: str) -> Optional[dict]:
        query = "MATCH (u:User {email: $email}) RETURN u"
        result = tx.run(query, email=email)
        record = result.single()
        return process_record(record)

    def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Retrieves a list of users with pagination."""
        with self._get_db().session() as session:
            results = session.read_transaction(self._list_users_tx, skip, limit)
            return [User(**result) for result in results if result]

    @staticmethod
    def _list_users_tx(tx, skip: int, limit: int) -> List[dict]:
        query = (
            "MATCH (u:User) "
            "RETURN u "
            "ORDER BY u.fullName ASC "
            "SKIP $skip LIMIT $limit"
        )
        result = tx.run(query, skip=skip, limit=limit)
        return [process_record(record) for record in result]

    def update_user(self, user_id: str, user_update: UserUpdate) -> Optional[User]:
        """Updates an existing user."""
        update_data = user_update.model_dump(exclude_unset=True, by_alias=True)
        if not update_data:
            return self.get_user_by_id(user_id)

        update_data['updatedAt'] = datetime.utcnow()

        with self._get_db().session() as session:
            result = session.write_transaction(self._update_user_tx, user_id, update_data)
            return User(**result) if result else None

    @staticmethod
    def _update_user_tx(tx, user_id: str, update_data: dict) -> Optional[dict]:
        set_clauses = [f"u.{key} = ${key}" for key in update_data.keys()]
        if 'updatedAt' in update_data:
            set_clauses.remove('u.updatedAt = $updatedAt')
            set_clauses.append('u.updatedAt = datetime($updatedAt)')

        query = (
            f"MATCH (u:User {{userId: $userId}}) "
            f"SET {', '.join(set_clauses)} "
            "RETURN u"
        )
        params = {'userId': user_id, **update_data}
        result = tx.run(query, params)
        record = result.single()
        return process_record(record)

    def delete_user(self, user_id: str) -> bool:
        """Deletes a user by their ID."""
        with self._get_db().session() as session:
            result = session.write_transaction(self._delete_user_tx, user_id)
            return result

    @staticmethod
    def _delete_user_tx(tx, user_id: str) -> bool:
        query = "MATCH (u:User {userId: $userId}) DETACH DELETE u"
        result = tx.run(query, userId=user_id)
        summary = result.consume()
        return summary.counters.nodes_deleted > 0

# Singleton instance of the service
user_service = UserService()
