from typing import Optional, List
from neomodel import db

from trm_api.models.tension import TensionCreate, TensionUpdate
from trm_api.graph_models.tension import Tension as GraphTension
from trm_api.graph_models.project import Project as GraphProject

class TensionRepository:
    """
    Repository for handling all database operations related to Tensions.
    """

    @db.transaction
    def create_tension(self, tension_data: TensionCreate) -> Optional[GraphTension]:
        """
        Creates a new Tension and connects it to its Project context.
        """
        # 1. Find the project context for the tension.
        try:
            project = GraphProject.nodes.get(uid=tension_data.project_id)
        except GraphProject.DoesNotExist:
            # Can't create a tension for a non-existent project.
            return None

        # 2. Create the new tension node.
        new_tension = GraphTension(**tension_data.model_dump(exclude={'project_id'})).save()

        # 3. Connect the tension to its project context.
        new_tension.context.connect(project)

        return new_tension

    def get_tension_by_uid(self, uid: str) -> Optional[GraphTension]:
        """
        Retrieves a Tension node by its unique ID.
        """
        try:
            return GraphTension.nodes.get(uid=uid)
        except GraphTension.DoesNotExist:
            return None

    def list_tensions_for_project(self, project_id: str, skip: int = 0, limit: int = 100) -> List[GraphTension]:
        """
        Lists all tensions that are part of a specific project.
        """
        try:
            project = GraphProject.nodes.get(uid=project_id)
            # 'tensions' is the reverse relationship from Project to Tension
            tensions = project.tensions.all()
            return tensions[skip:skip+limit]
        except GraphProject.DoesNotExist:
            return []

    def update_tension(self, uid: str, tension_data: TensionUpdate) -> Optional[GraphTension]:
        """
        Updates an existing tension.
        """
        tension = self.get_tension_by_uid(uid)
        if not tension:
            return None

        update_data = tension_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(tension, key, value)
        
        tension.save()
        return tension

    def delete_tension(self, uid: str) -> bool:
        """
        Deletes a tension by its unique ID.
        """
        tension = self.get_tension_by_uid(uid)
        if not tension:
            return False
        
        tension.delete()
        return True
