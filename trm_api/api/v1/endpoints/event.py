from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any, Optional

from trm_api.schemas.event import Event as EventResponseSchema, EventCreate as EventCreateSchema
from trm_api.services.event_service import event_service, EventService
from trm_api.graph_models.event import Event as EventGraphModel
from trm_api.utils.datetime_adapter import adapt_model_to_schema, adapt_model_list_to_schema

router = APIRouter()

# Using the central datetime adapter module now

@router.post("/", response_model=EventResponseSchema, status_code=status.HTTP_201_CREATED)
def create_event(
    event_in: EventCreateSchema,
    service: EventService = Depends(lambda: event_service)
):
    """
    Create a new Event. Events are immutable.
    """
    # The service now expects event_data as the parameter name
    db_event = service.create_event(event_data=event_in)
    # Convert Neo4j model to Pydantic schema-compatible dict using the adapter
    return adapt_model_to_schema(db_event, id_field_name="uid", target_id_name="id")

@router.get("/{event_id}", response_model=EventResponseSchema)
def get_event(
    event_id: str,
    service: EventService = Depends(lambda: event_service)
):
    """
    Get a specific Event by its ID.
    """
    db_event = service.get_event_by_id(event_id=event_id)
    if db_event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    # Convert Neo4j model to Pydantic schema-compatible dict using the adapter
    return adapt_model_to_schema(db_event, id_field_name="uid", target_id_name="id")

@router.get("/", response_model=List[EventResponseSchema])
def list_events(
    skip: int = 0,
    limit: int = 100,
    service: EventService = Depends(lambda: event_service)
):
    """
    Retrieve a list of Events.
    """
    db_events = service.list_events(skip=skip, limit=limit)
    # Convert each Neo4j model to Pydantic schema-compatible dict using the adapter
    return adapt_model_list_to_schema(db_events, id_field_name="uid", target_id_name="id")
