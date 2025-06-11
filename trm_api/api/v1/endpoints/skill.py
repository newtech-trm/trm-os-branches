from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from trm_api.models.skill import Skill, SkillCreate, SkillUpdate
from trm_api.services.skill_service import skill_service, SkillService

router = APIRouter()

@router.post("/", response_model=Skill, status_code=status.HTTP_201_CREATED)
def create_skill(
    skill_in: SkillCreate,
    service: SkillService = Depends(lambda: skill_service)
):
    """
    Create a new skill.
    """
    return service.create_skill(skill_create=skill_in)

@router.get("/{skill_id}", response_model=Skill)
def get_skill(
    skill_id: str,
    service: SkillService = Depends(lambda: skill_service)
):
    """
    Get a specific skill by its ID.
    """
    db_skill = service.get_skill_by_id(skill_id=skill_id)
    if db_skill is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
    return db_skill

@router.get("/", response_model=List[Skill])
def list_skills(
    skip: int = 0,
    limit: int = 100,
    service: SkillService = Depends(lambda: skill_service)
):
    """
    Retrieve a list of skills.
    """
    return service.list_skills(skip=skip, limit=limit)

@router.put("/{skill_id}", response_model=Skill)
def update_skill(
    skill_id: str,
    skill_in: SkillUpdate,
    service: SkillService = Depends(lambda: skill_service)
):
    """
    Update an existing skill.
    """
    updated_skill = service.update_skill(skill_id=skill_id, skill_update=skill_in)
    if updated_skill is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
    return updated_skill

@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_skill(
    skill_id: str,
    service: SkillService = Depends(lambda: skill_service)
):
    """
    Delete a skill.
    """
    deleted = service.delete_skill(skill_id=skill_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
    return
