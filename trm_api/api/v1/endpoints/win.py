from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import List, Optional, Dict, Any
from datetime import datetime

from trm_api.models.win import Win, WinCreate, WinUpdate
from trm_api.repositories.win_repository import WINRepository
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

# --- LEADS_TO_WIN Relationship Endpoints ---

@router.get("/{win_id}/sources", response_model=Dict[str, List])
def get_win_sources(
    win_id: str,
    repository: WINRepository = Depends(lambda: WINRepository())
):
    """
    Get the sources (Projects, RecognitionEvents) connected to a WIN via LEADS_TO_WIN relationship.
    """
    sources = repository.get_win_sources(uid=win_id)
    if not sources:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="WIN not found or no sources available")
    return sources

@router.post("/{win_id}/source-projects/{project_id}", status_code=status.HTTP_201_CREATED)
def connect_project_to_win(
    win_id: str,
    project_id: str,
    relationship_data: Dict[str, Any] = Body(...),
    repository: WINRepository = Depends(lambda: WINRepository())
):
    """
    Connect a Project to a WIN via LEADS_TO_WIN relationship.
    
    The relationship_data can include:
    - contribution_level (int): 1-5 (Minimal to Critical)
    - direct_contribution (bool): Whether the contribution was direct
    - impact_ratio (float): 0.0-1.0 for impact
    - recognition_score (int): 1-100 score
    - notes (str): Additional notes
    """
    # Extract relationship properties from request body
    contribution_level = relationship_data.get("contribution_level", 1)
    direct_contribution = relationship_data.get("direct_contribution", True)
    impact_ratio = relationship_data.get("impact_ratio")
    recognition_score = relationship_data.get("recognition_score")
    notes = relationship_data.get("notes")
    
    # Optional: verified_by and verification_date if supported
    verified_by = relationship_data.get("verified_by")
    verification_date = relationship_data.get("verification_date")
    
    result = repository.connect_project_to_win(
        project_uid=project_id,
        win_uid=win_id,
        contribution_level=contribution_level,
        direct_contribution=direct_contribution,
        impact_ratio=impact_ratio,
        recognition_score=recognition_score,
        verified_by=verified_by,
        verification_date=verification_date,
        notes=notes
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project or WIN not found or connection failed"
        )
    
    return {"status": "success", "message": f"Project {project_id} connected to WIN {win_id}"}

@router.delete("/{win_id}/source-projects/{project_id}")
def disconnect_project_from_win(
    win_id: str,
    project_id: str,
    repository: WINRepository = Depends(lambda: WINRepository())
):
    """
    Remove LEADS_TO_WIN relationship between a Project and a WIN.
    """
    result = repository.disconnect_project_from_win(
        project_uid=project_id,
        win_uid=win_id
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project or WIN not found or disconnection failed"
        )
    
    return {"status": "success", "message": f"Project {project_id} disconnected from WIN {win_id}"}
