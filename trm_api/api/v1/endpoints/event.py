from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any, Optional

from trm_api.schemas.event import Event as EventResponseSchema, EventCreate as EventCreateSchema
from trm_api.services.event_service import event_service, EventService
from trm_api.graph_models.event import Event as EventGraphModel

router = APIRouter()

# Adapter function to convert Neo4j Event model to Pydantic schema
def convert_event_to_schema(event: EventGraphModel) -> Dict[str, Any]:
    """
    Convert Neo4j Event model to a dictionary compatible with Pydantic schema,
    ensuring datetime objects are converted to ISO format strings.
    """
    # Convert model to dict and handle any Neo4j-specific types
    event_dict = {
        "uid": event.uid,
        "name": event.name,
        "description": event.description,
        "payload": event.payload,
        "tags": event.tags,
        # Convert datetime objects to ISO format strings
        "created_at": event.created_at.isoformat() if event.created_at else None,
        "updated_at": event.updated_at.isoformat() if event.updated_at else None,
    }
    
    # Filter out None values for optional fields that weren't set
    return {k: v for k, v in event_dict.items() if v is not None}

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
    # Convert Neo4j model to Pydantic schema-compatible dict
    return convert_event_to_schema(db_event)

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
    # Convert Neo4j model to Pydantic schema-compatible dict
    return convert_event_to_schema(db_event)

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
    # Convert each Neo4j model to Pydantic schema-compatible dict
    return [convert_event_to_schema(event) for event in db_events]
