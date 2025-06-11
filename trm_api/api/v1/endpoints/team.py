from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from trm_api.models.team import Team, TeamCreate, TeamUpdate
from trm_api.models.relationships import Relationship
from trm_api.services.team_service import team_service, TeamService

router = APIRouter()

@router.post("/", response_model=Team, status_code=status.HTTP_201_CREATED)
def create_team(
    team_in: TeamCreate,
    service: TeamService = Depends(lambda: team_service)
):
    """
    Create a new Team.
    """
    return service.create_team(team_create=team_in)

@router.get("/{team_id}", response_model=Team)
def get_team(
    team_id: str,
    service: TeamService = Depends(lambda: team_service)
):
    """
    Get a specific Team by its ID.
    """
    db_team = service.get_team_by_id(team_id=team_id)
    if db_team is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    return db_team

@router.get("/", response_model=List[Team])
def list_teams(
    skip: int = 0,
    limit: int = 100,
    service: TeamService = Depends(lambda: team_service)
):
    """
    Retrieve a list of Teams.
    """
    return service.list_teams(skip=skip, limit=limit)

@router.put("/{team_id}", response_model=Team)
def update_team(
    team_id: str,
    team_in: TeamUpdate,
    service: TeamService = Depends(lambda: team_service)
):
    """
    Update an existing Team.
    """
    updated_team = service.update_team(team_id=team_id, team_update=team_in)
    if updated_team is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    return updated_team

@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(
    team_id: str,
    service: TeamService = Depends(lambda: team_service)
):
    """
    Delete a Team.
    """
    deleted = service.delete_team(team_id=team_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    return

@router.post("/{team_id}/add-member/{user_id}", response_model=Relationship, status_code=status.HTTP_201_CREATED)
def add_member_to_team(
    team_id: str,
    user_id: str,
    service: TeamService = Depends(lambda: team_service)
):
    """
    Adds a User to a Team, creating a HAS_MEMBER relationship.
    """
    relationship = service.add_member_to_team(team_id=team_id, user_id=user_id)
    if relationship is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team or User not found, or relationship could not be created"
        )
    return relationship
