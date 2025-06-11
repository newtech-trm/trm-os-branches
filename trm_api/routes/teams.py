from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from trm_api.models.team import Team, TeamCreate, TeamUpdate
from trm_api.models.user import User
from trm_api.repositories.team_repository import TeamRepository

router = APIRouter()

def get_team_repository() -> TeamRepository:
    return TeamRepository()

@router.post("/", response_model=Team, status_code=status.HTTP_201_CREATED)
def create_team(
    team: TeamCreate,
    repo: TeamRepository = Depends(get_team_repository)
):
    """
    Create a new team.
    """
    db_team = repo.create_team(team_data=team)
    return db_team

@router.get("/", response_model=List[Team])
def list_teams(
    skip: int = 0,
    limit: int = 100,
    repo: TeamRepository = Depends(get_team_repository)
):
    """
    Retrieve a list of teams.
    """
    teams = repo.list_teams(skip=skip, limit=limit)
    return teams

@router.get("/{uid}", response_model=Team)
def get_team(
    uid: str,
    repo: TeamRepository = Depends(get_team_repository)
):
    """
    Get a specific team by its UID.
    """
    team = repo.get_team_by_uid(uid)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    return team

@router.put("/{uid}", response_model=Team)
def update_team(
    uid: str,
    team_update: TeamUpdate,
    repo: TeamRepository = Depends(get_team_repository)
):
    """
    Update a team's details.
    """
    updated_team = repo.update_team(uid=uid, team_data=team_update)
    if not updated_team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    return updated_team

@router.delete("/{uid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(
    uid: str,
    repo: TeamRepository = Depends(get_team_repository)
):
    """
    Delete a team.
    """
    success = repo.delete_team(uid)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    return

# --- Member Management Endpoints ---

@router.post("/{team_uid}/members/{user_uid}", response_model=Team)
def add_member_to_team(
    team_uid: str,
    user_uid: str,
    repo: TeamRepository = Depends(get_team_repository)
):
    """
    Add a user to a team.
    """
    team = repo.add_member_to_team(team_uid=team_uid, user_uid=user_uid)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team or User not found")
    return team

@router.get("/{team_uid}/members", response_model=List[User])
def list_team_members(
    team_uid: str,
    skip: int = 0,
    limit: int = 100,
    repo: TeamRepository = Depends(get_team_repository)
):
    """
    List all members of a team.
    """
    team = repo.get_team_by_uid(team_uid)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    
    members = repo.list_team_members(team_uid=team_uid, skip=skip, limit=limit)
    return members
