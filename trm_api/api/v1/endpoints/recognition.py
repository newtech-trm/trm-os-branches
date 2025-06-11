from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from trm_api.models.recognition import Recognition, RecognitionCreate, RecognitionUpdate
from trm_api.services.recognition_service import recognition_service, RecognitionService

router = APIRouter()

@router.post("/", response_model=Recognition, status_code=status.HTTP_201_CREATED)
def create_recognition(
    recognition_in: RecognitionCreate,
    service: RecognitionService = Depends(lambda: recognition_service)
):
    """
    Create a new Recognition.
    """
    return service.create_recognition(recognition_create=recognition_in)

@router.get("/{recognition_id}", response_model=Recognition)
def get_recognition(
    recognition_id: str,
    service: RecognitionService = Depends(lambda: recognition_service)
):
    """
    Get a specific Recognition by its ID.
    """
    db_recognition = service.get_recognition_by_id(recognition_id=recognition_id)
    if db_recognition is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recognition not found")
    return db_recognition

@router.get("/", response_model=List[Recognition])
def list_recognitions(
    skip: int = 0,
    limit: int = 100,
    service: RecognitionService = Depends(lambda: recognition_service)
):
    """
    Retrieve a list of Recognitions.
    """
    return service.list_recognitions(skip=skip, limit=limit)

@router.put("/{recognition_id}", response_model=Recognition)
def update_recognition(
    recognition_id: str,
    recognition_in: RecognitionUpdate,
    service: RecognitionService = Depends(lambda: recognition_service)
):
    """
    Update an existing Recognition.
    """
    updated_recognition = service.update_recognition(recognition_id=recognition_id, recognition_update=recognition_in)
    if updated_recognition is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recognition not found")
    return updated_recognition

@router.delete("/{recognition_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recognition(
    recognition_id: str,
    service: RecognitionService = Depends(lambda: recognition_service)
):
    """
    Delete a Recognition.
    """
    deleted = service.delete_recognition(recognition_id=recognition_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recognition not found")
    return
