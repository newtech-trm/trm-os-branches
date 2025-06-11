from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from trm_api.models.win import Win, WinCreate, WinUpdate
from trm_api.services.win_service import win_service, WinService

router = APIRouter()

@router.post("/", response_model=Win, status_code=status.HTTP_201_CREATED)
def create_win(
    win_in: WinCreate,
    service: WinService = Depends(lambda: win_service)
):
    """
    Create a new WIN.
    """
    return service.create_win(win_create=win_in)

@router.get("/{win_id}", response_model=Win)
def get_win(
    win_id: str,
    service: WinService = Depends(lambda: win_service)
):
    """
    Get a specific WIN by its ID.
    """
    db_win = service.get_win_by_id(win_id=win_id)
    if db_win is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="WIN not found")
    return db_win

@router.get("/", response_model=List[Win])
def list_wins(
    skip: int = 0,
    limit: int = 25,
    service: WinService = Depends(lambda: win_service)
):
    """
    Retrieve a list of WINs.
    """
    return service.list_wins(skip=skip, limit=limit)

@router.put("/{win_id}", response_model=Win)
def update_win(
    win_id: str,
    win_in: WinUpdate,
    service: WinService = Depends(lambda: win_service)
):
    """
    Update an existing WIN.
    """
    updated_win = service.update_win(win_id=win_id, win_update=win_in)
    if updated_win is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="WIN not found")
    return updated_win

@router.delete("/{win_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_win(
    win_id: str,
    service: WinService = Depends(lambda: win_service)
):
    """
    Delete a WIN.
    """
    deleted = service.delete_win(win_id=win_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="WIN not found")
    return
