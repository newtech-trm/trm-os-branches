from fastapi import APIRouter, HTTPException, status
from typing import List

from trm_api.api.v1.models.skill import Skill, SkillCreate, SkillUpdate
from trm_api.repositories.skill import SkillRepository

router = APIRouter()
repository = SkillRepository()

@router.post("/", response_model=Skill, status_code=status.HTTP_201_CREATED)
def create_skill(skill_in: SkillCreate):
    """
    Create a new skill.
    """
    return repository.create_skill(skill_data=skill_in)

@router.get("/{skill_uid}", response_model=Skill)
def get_skill(skill_uid: str):
    """
    Get a specific skill by its UID.
    """
    db_skill = repository.get_skill_by_uid(uid=skill_uid)
    if db_skill is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
    return db_skill

@router.get("/", response_model=List[Skill])
def list_skills():
    """
    Retrieve a list of all skills.
    """
    return repository.list_all_skills()

@router.put("/{skill_uid}", response_model=Skill)
def update_skill(skill_uid: str, skill_in: SkillUpdate):
    """
    Update an existing skill.
    """
    updated_skill = repository.update_skill(uid=skill_uid, skill_data=skill_in)
    if updated_skill is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
    return updated_skill

@router.delete("/{skill_uid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_skill(skill_uid: str):
    """
    Delete a skill.
    """
    deleted = repository.delete_skill(uid=skill_uid)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
    return
