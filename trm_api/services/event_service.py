from neo4j import Driver
from typing import List, Optional, Dict, Any
from datetime import datetime

from trm_api.db.session import get_driver
from trm_api.models.event import Event, EventCreate, EventInDB

class EventService:
    """
    Service layer for handling business logic related to Events.
    Events are immutable; they can only be created and retrieved.
    """

    def _get_db(self) -> Driver:
        return get_driver()

    def create_event(self, event_create: EventCreate) -> Event:
        """Creates a new Event node."""
        event_db = EventInDB(**event_create.model_dump())
        params = event_db.model_dump(by_alias=True)

        with self._get_db().session() as session:
            result = session.write_transaction(self._create_event_tx, params)
            return Event(**result)

    @staticmethod
    def _create_event_tx(tx, params: dict) -> dict:
        # The payload can have a variable structure, so we pass it as a JSON string
        query = (
            "CREATE (e:Event { "
            "  eventId: $eventId, "
            "  eventType: $eventType, "
            "  source: $source, "
            "  payload: apoc.convert.toJson($payload), "
            "  createdAt: datetime($createdAt) "
            "}) "
            "RETURN e"
        )
        result = tx.run(query, params)
        record = result.single()
        if record and record['e']:
            node_data = dict(record['e'])
            # The payload is stored as a string, so we need to parse it back if needed by the model
            # Pydantic should handle this automatically if the field type is Dict
            return node_data
        return None

    def get_event_by_id(self, event_id: str) -> Optional[Event]:
        """Retrieves a single event by its unique ID."""
        with self._get_db().session() as session:
            result = session.read_transaction(self._get_event_by_id_tx, event_id)
            return Event(**result) if result else None

    @staticmethod
    def _get_event_by_id_tx(tx, event_id: str) -> Optional[dict]:
        query = "MATCH (e:Event {eventId: $eventId}) RETURN e"
        result = tx.run(query, eventId=event_id)
        record = result.single()
        if record and record['e']:
            return dict(record['e'])
        return None

    def list_events(self, skip: int = 0, limit: int = 100) -> List[Event]:
        """Retrieves a list of events with pagination."""
        with self._get_db().session() as session:
            results = session.read_transaction(self._list_events_tx, skip, limit)
            return [Event(**result) for result in results]

    @staticmethod
    def _list_events_tx(tx, skip: int, limit: int) -> List[dict]:
        query = (
            "MATCH (e:Event) "
            "RETURN e "
            "ORDER BY e.createdAt DESC "
            "SKIP $skip LIMIT $limit"
        )
        result = tx.run(query, skip=skip, limit=limit)
        return [dict(record['e']) for record in result]

# Singleton instance of the service
event_service = EventService()
