from typing import Optional, List, Tuple
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
        # Chuyển đổi dữ liệu và ánh xạ summary -> title
        tension_dict = tension_data.model_dump(exclude={'project_id'})
        if 'summary' in tension_dict:
            tension_dict['title'] = tension_dict.pop('summary')  # Ánh xạ summary -> title
            
        new_tension = GraphTension(**tension_dict).save()

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
        
    @db.transaction
    def connect_tension_to_project(self, tension_uid: str, project_uid: str,
                            resolution_status: str = 'Proposed',
                            resolution_approach: str = None,
                            expected_outcome: str = None,
                            alignment_score: float = None,
                            priority: str = 'Medium',
                            start_date = None,
                            target_resolution_date = None,
                            actual_resolution_date = None,
                            notes: str = None) -> Optional[Tuple[GraphTension, GraphProject]]:
        """
        Establishes a RESOLVES_TENSION relationship from a Project to a Tension
        with all required properties according to the TRM Ontology V3.2.
        
        Args:
            tension_uid: UID of the tension
            project_uid: UID of the project
            resolution_status: Status of the resolution (e.g. 'Proposed', 'ResolutionInProgress')
            resolution_approach: Description of the approach to resolve the tension
            expected_outcome: Expected outcome after tension resolution
            alignment_score: Score (0.0-1.0) evaluating how well the project fits for resolving this tension
            priority: Priority level ('Critical', 'High', 'Medium', 'Low', 'Informational')
            start_date: Date when project started resolving this tension
            target_resolution_date: Target date for tension resolution
            actual_resolution_date: Actual date when tension was resolved
            notes: Additional notes about this relationship
        
        Returns:
            Tuple of (tension, project) if successful, None otherwise
        """
        import uuid
        from datetime import datetime
        
        # 1. Get both the tension and project nodes
        tension = self.get_tension_by_uid(tension_uid)
        if not tension:
            return None
            
        try:
            project = GraphProject.nodes.get(uid=project_uid)
        except GraphProject.DoesNotExist:
            return None
        
        # 2. Create the RESOLVES_TENSION relationship with all properties
        relationship_props = {
            'relationshipId': str(uuid.uuid4()),
            'resolutionStatus': resolution_status,
            'creationDate': datetime.now(),
            'lastModifiedDate': datetime.now()
        }
        
        # Add optional properties if provided
        if resolution_approach:
            relationship_props['resolutionApproach'] = resolution_approach
        if expected_outcome:
            relationship_props['expectedOutcome'] = expected_outcome
        if alignment_score is not None:
            relationship_props['alignmentScore'] = alignment_score
        if priority:
            relationship_props['priority'] = priority
        if start_date:
            relationship_props['startDate'] = start_date
        if target_resolution_date:
            relationship_props['targetResolutionDate'] = target_resolution_date
        if actual_resolution_date:
            relationship_props['actualResolutionDate'] = actual_resolution_date
        if notes:
            relationship_props['notes'] = notes
            
        # Connect with relationship properties
        project.resolves_tensions.connect(tension, relationship_props)
        
        return (tension, project)
        
    def get_projects_resolving_tension(self, tension_uid: str, skip: int = 0, limit: int = 100) -> List[GraphProject]:
        """
        Retrieves all Projects that are resolving a specific Tension.
        """
        tension = self.get_tension_by_uid(tension_uid)
        if not tension:
            return []
            
        # Get all projects connected with RESOLVES_TENSION relationship
        return list(tension.resolved_by.all()[skip:skip+limit])
        
    @db.transaction
    def disconnect_project_from_tension(self, tension_uid: str, project_uid: str) -> bool:
        """
        Removes the RESOLVES_TENSION relationship between a Project and a Tension.
        
        Returns True if disconnection was successful, False otherwise.
        """
        # 1. Get both the tension and project nodes
        tension = self.get_tension_by_uid(tension_uid)
        if not tension:
            return False
            
        try:
            project = GraphProject.nodes.get(uid=project_uid)
        except GraphProject.DoesNotExist:
            return False
            
        # 2. Remove the relationship
        project.resolves_tensions.disconnect(tension)
        
        return True
