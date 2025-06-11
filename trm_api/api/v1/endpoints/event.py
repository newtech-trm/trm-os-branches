from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from trm_api.models.event import Event, EventCreate
from trm_api.services.event_service import event_service, EventService

router = APIRouter()

@router.post("/", response_model=Event, status_code=status.HTTP_201_CREATED)
def create_event(
    event_in: EventCreate,
    service: EventService = Depends(lambda: event_service)
):
    """
    Create a new Event. Events are immutable.
    """
    return service.create_event(event_create=event_in)

@router.get("/{event_id}", response_model=Event)
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
    return db_event

@router.get("/", response_model=List[Event])
def list_events(
    skip: int = 0,
    limit: int = 100,
    service: EventService = Depends(lambda: event_service)
):
    """
    Retrieve a list of Events.
    """
    return service.list_events(skip=skip, limit=limit)
