from typing import Optional, List
from neomodel import db

from trm_api.models.team import TeamCreate, TeamUpdate
from trm_api.graph_models.team import Team as GraphTeam
from trm_api.graph_models.user import User as GraphUser

class TeamRepository:
    """
    Repository for handling all database operations related to Teams.
    """

    @db.transaction
    def create_team(self, team_data: TeamCreate) -> GraphTeam:
        """
        Creates a new Team node.
        """
        team = GraphTeam(**team_data.model_dump()).save()
        return team

    def get_team_by_uid(self, uid: str) -> Optional[GraphTeam]:
        """
        Retrieves a Team node by its unique ID.
        """
        try:
            return GraphTeam.nodes.get(uid=uid)
        except GraphTeam.DoesNotExist:
            return None

    def list_teams(self, skip: int = 0, limit: int = 100) -> List[GraphTeam]:
        """
        Lists all Team nodes with pagination.
        """
        return GraphTeam.nodes.all()[skip:skip+limit]

    def update_team(self, uid: str, team_data: TeamUpdate) -> Optional[GraphTeam]:
        """
        Updates an existing Team node.
        """
        team = self.get_team_by_uid(uid)
        if not team:
            return None

        update_data = team_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(team, key, value)
        
        team.save()
        return team

    def delete_team(self, uid: str) -> bool:
        """
        Deletes a Team node by its unique ID.
        """
        team = self.get_team_by_uid(uid)
        if not team:
            return False
        
        team.delete()
        return True

    @db.transaction
    def add_member_to_team(self, team_uid: str, user_uid: str) -> Optional[GraphTeam]:
        """
        Adds a user as a member to a team.
        """
        team = self.get_team_by_uid(team_uid)
        if not team:
            return None
        
        try:
            user = GraphUser.nodes.get(uid=user_uid)
        except GraphUser.DoesNotExist:
            return None
            
        team.members.connect(user)
        return team

    def list_team_members(self, team_uid: str, skip: int = 0, limit: int = 100) -> List[GraphUser]:
        """
        Lists all members of a specific team.
        """
        team = self.get_team_by_uid(team_uid)
        if not team:
            return []
        
        return team.members.all()[skip:skip+limit]
