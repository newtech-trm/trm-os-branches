from neo4j import Driver
from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import HTTPException, status
from trm_api.graph_models.event import Event as EventGraphModel
from trm_api.graph_models.agent import Agent as AgentGraphModel
from trm_api.graph_models.project import Project as ProjectGraphModel # Example, add others as needed
from trm_api.graph_models.task import Task as TaskGraphModel       # Example, add others as needed
from trm_api.graph_models.base import BaseNode # For type hinting context_node
from trm_api.schemas.event import EventCreate as EventCreateSchema, Event as EventResponseSchema

# Map for resolving context node labels to their neomodel classes
NODE_MODEL_MAP = {
    "Agent": AgentGraphModel,
    "Project": ProjectGraphModel,
    "Task": TaskGraphModel,
    # Add other models that can be an event context here
}

class EventService:
    # Note: _get_db and direct neo4j.Driver usage will be phased out for neomodel ORM methods.
    """
    Service layer for handling business logic related to Events.
    Events are immutable; they can only be created and retrieved.
    """

    def _get_db(self) -> Driver:
        return get_driver()

    def create_event(self, event_data: EventCreateSchema) -> EventGraphModel:
        """Creates a new Event node and its relationships using neomodel."""
        actor_node = AgentGraphModel.nodes.get_or_none(uid=event_data.actor_uid)
        if not actor_node:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Actor with UID {event_data.actor_uid} not found.")

        context_node: Optional[BaseNode] = None
        if event_data.context_uid and event_data.context_node_label:
            ContextModelClass = NODE_MODEL_MAP.get(event_data.context_node_label)
            if not ContextModelClass:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid context node label: {event_data.context_node_label}. Supported labels are: {list(NODE_MODEL_MAP.keys())}"
                )
            context_node = ContextModelClass.nodes.get_or_none(uid=event_data.context_uid)
            if not context_node:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"{event_data.context_node_label} context node with UID {event_data.context_uid} not found."
                )
        elif event_data.context_uid or event_data.context_node_label: # XOR condition: if one is provided, the other must be too
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Both context_uid and context_node_label must be provided if one is present."
            )

        # Create the Event node
        new_event = EventGraphModel(
            name=event_data.name,
            description=event_data.description,
            payload=event_data.payload,
            tags=event_data.tags
        ).save()

        # Connect relationships
        actor_node.triggered_events.connect(new_event)

        if context_node:
            # Kết nối với relationship thích hợp dựa trên loại node context
            if event_data.context_node_label == "Agent":
                new_event.primary_context_agent.connect(context_node)
            elif event_data.context_node_label == "Project":
                new_event.primary_context_project.connect(context_node)
            elif event_data.context_node_label == "Task":
                new_event.primary_context_task.connect(context_node)
            elif event_data.context_node_label == "Resource":
                new_event.primary_context_resource.connect(context_node)
            else:
                # Nếu có thêm loại node khác, cần bổ sung thêm ở đây và trong event.py
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported context node type for relationship: {event_data.context_node_label}"
                )
        
        return new_event

    # _create_event_tx is no longer needed as we use neomodel ORM directly.


    def get_event_by_id(self, event_id: str) -> Optional[EventGraphModel]: # Changed return type
        """Retrieves a single event by its unique ID using neomodel."""
        # TODO: Refactor to use neomodel directly if desired, or keep existing for now if it works with EventGraphModel
        # For direct neomodel: return EventGraphModel.nodes.get_or_none(uid=event_id)
        # The current implementation below might need adjustment if Event(**result) expects a dict from raw cypher
        # and EventGraphModel expects direct attribute access or a different constructor. 
        # For now, assuming it might still work or will be refactored later.
        try:
            return EventGraphModel.nodes.get(uid=event_id)
        except EventGraphModel.DoesNotExist:
            return None
        # Original code below, for reference or if neomodel direct fetch fails/is not preferred yet
        # with self._get_db().session() as session:
        #     result = session.read_transaction(self._get_event_by_id_tx, event_id)
        #     # This part needs to be compatible with EventGraphModel if EventGraphModel is returned
        #     # return EventGraphModel(**result) if result else None # This might not work directly

    # _get_event_by_id_tx might be deprecated if get_event_by_id fully moves to neomodel.
    # @staticmethod
    # def _get_event_by_id_tx(tx, event_id: str) -> Optional[dict]:
    #     query = "MATCH (e:Event {uid: $uid}) RETURN e" # Assuming uid is the property in graph
    #     result = tx.run(query, uid=event_id)
    #     record = result.single()
    #     if record and record['e']:
    #         return dict(record['e'])
    #     return None

    def list_events(self, skip: int = 0, limit: int = 100) -> List[EventGraphModel]: # Changed return type
        """Retrieves a list of events with pagination using neomodel."""
        # TODO: Refactor to use neomodel directly
        # return EventGraphModel.nodes.all()[skip:skip+limit]
        # Current implementation might need adjustment for EventGraphModel
        return list(EventGraphModel.nodes.all()[skip:skip+limit])
        # Original code below:
        # with self._get_db().session() as session:
        #     results = session.read_transaction(self._list_events_tx, skip, limit)
        #     return [EventGraphModel(**result) for result in results] # This might not work directly

    # _list_events_tx might be deprecated if list_events fully moves to neomodel.
    # @staticmethod
    # def _list_events_tx(tx, skip: int, limit: int) -> List[dict]:
    #     query = (
    #         "MATCH (e:Event) "
    #         "RETURN e "
    #         "ORDER BY e.created_at DESC " # Assuming created_at is the property
    #         "SKIP $skip LIMIT $limit"
    #     )
    #     result = tx.run(query, skip=skip, limit=limit)
    #     return [dict(record['e']) for record in result]

# Singleton instance of the service
event_service = EventService()
