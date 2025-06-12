from typing import Optional, List, Tuple, Dict, Any
from neomodel import db
from datetime import datetime
import uuid

from trm_api.graph_models.win import WIN as GraphWIN
from trm_api.graph_models.project import Project as GraphProject
from trm_api.graph_models.event import Event as GraphEvent
from trm_api.models.win import WinCreate, WinUpdate  # Pydantic model for API data

class WINRepository:
    def create_win(self, win_data: WinCreate) -> GraphWIN:
        """
        Creates a new WIN (Wisdom-Infused Narrative).
        """
        # Map từ WinCreate (summary, description, winType, relatedEntityIds) sang GraphWIN (title, narrative, impact_level)
        impact_level = 1  # Default impact level
        if win_data.win_type == "Critical" or win_data.win_type == "Major":
            impact_level = 3
        elif win_data.win_type == "Moderate":
            impact_level = 2
        
        win = GraphWIN(
            title=win_data.summary,
            narrative=win_data.description,
            impact_level=impact_level
        ).save()
        return win

    def get_win_by_uid(self, uid: str) -> Optional[GraphWIN]:
        """
        Retrieves a WIN by its unique ID.
        """
        try:
            return GraphWIN.nodes.get(uid=uid)
        except GraphWIN.DoesNotExist:
            return None

    def list_wins(self, skip: int = 0, limit: int = 100) -> List[GraphWIN]:
        """
        Retrieves a list of all WINs with pagination.
        """
        return GraphWIN.nodes.all()[skip:skip + limit]

    def update_win(self, uid: str, win_data: WinUpdate) -> Optional[GraphWIN]:
        """
        Updates an existing WIN.
        """
        win = self.get_win_by_uid(uid)
        if not win:
            return None

        update_data = win_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(win, key, value)
        
        win.save()
        return win

    def delete_win(self, uid: str) -> bool:
        """
        Deletes a WIN by its unique ID.
        Returns True if deletion was successful, False otherwise.
        """
        win = self.get_win_by_uid(uid)
        if not win:
            return False
        
        win.delete()
        return True

    @db.transaction
    def connect_project_to_win(self, project_uid: str, win_uid: str,
                            contribution_level: int = 1,
                            direct_contribution: bool = True,
                            impact_ratio: float = None,
                            recognition_score: int = None,
                            verified_by: str = None,
                            verification_date: datetime = None,
                            notes: str = None) -> Optional[Tuple[GraphProject, GraphWIN]]:
        """
        Establishes a LEADS_TO_WIN relationship from a Project to a WIN
        with all required properties according to the TRM Ontology V3.2.
        
        Args:
            project_uid: UID of the project
            win_uid: UID of the WIN
            contribution_level: Level of contribution (1-5)
                1: Minimal
                2: Minor
                3: Moderate
                4: Significant
                5: Critical
            direct_contribution: Whether the contribution was direct
            impact_ratio: Impact ratio (0.0-1.0) for this contribution
            recognition_score: Recognition score (1-100)
            verified_by: UID of the user/agent who verified this relationship
            verification_date: DateTime when this relationship was verified
            notes: Additional notes about this relationship
            
        Returns:
            Tuple of (project, win) if successful, None otherwise
        """
        # 1. Get both the project and WIN nodes
        try:
            project = GraphProject.nodes.get(uid=project_uid)
        except GraphProject.DoesNotExist:
            return None
            
        try:
            win = GraphWIN.nodes.get(uid=win_uid)
        except GraphWIN.DoesNotExist:
            return None
        
        # 2. Create the LEADS_TO_WIN relationship with all properties
        relationship_props = {
            'relationshipId': str(uuid.uuid4()),
            'contributionLevel': contribution_level,
            'creationDate': datetime.now(),
            'lastModifiedDate': datetime.now(),
            'directContribution': direct_contribution
        }
        
        # Add optional properties if provided
        if impact_ratio is not None:
            relationship_props['impactRatio'] = impact_ratio
        if recognition_score is not None:
            relationship_props['recognitionScore'] = recognition_score
        if verified_by:
            relationship_props['verifiedBy'] = verified_by
        if verification_date:
            relationship_props['verificationDate'] = verification_date
        if notes:
            relationship_props['notes'] = notes
        
        # Connect with relationship properties
        project.leads_to_wins.connect(win, relationship_props)
        
        return (project, win)

    @db.transaction
    def connect_recognition_event_to_win(self, event_uid: str, win_uid: str,
                                    contribution_level: int = 1,
                                    direct_contribution: bool = True,
                                    impact_ratio: float = None,
                                    recognition_score: int = None,
                                    verified_by: str = None,
                                    verification_date: datetime = None,
                                    notes: str = None) -> Optional[Tuple[GraphEvent, GraphWIN]]:
        """
        Establishes a LEADS_TO_WIN relationship from a RecognitionEvent to a WIN
        with all required properties according to the TRM Ontology V3.2.
        
        Args:
            event_uid: UID of the RecognitionEvent
            win_uid: UID of the WIN
            contribution_level: Level of contribution (1-5)
                1: Minimal
                2: Minor
                3: Moderate
                4: Significant
                5: Critical
            direct_contribution: Whether the contribution was direct
            impact_ratio: Impact ratio (0.0-1.0) for this contribution
            recognition_score: Recognition score (1-100)
            verified_by: UID of the user/agent who verified this relationship
            verification_date: DateTime when this relationship was verified
            notes: Additional notes about this relationship
            
        Returns:
            Tuple of (event, win) if successful, None otherwise
        """
        # 1. Get both the RecognitionEvent and WIN nodes
        try:
            event = GraphEvent.nodes.get(uid=event_uid)
            # Verify this is actually a RecognitionEvent
            if event.event_type != 'RecognitionEvent':
                return None
        except GraphEvent.DoesNotExist:
            return None
            
        try:
            win = GraphWIN.nodes.get(uid=win_uid)
        except GraphWIN.DoesNotExist:
            return None
        
        # 2. Create the LEADS_TO_WIN relationship with all properties
        relationship_props = {
            'relationshipId': str(uuid.uuid4()),
            'contributionLevel': contribution_level,
            'creationDate': datetime.now(),
            'lastModifiedDate': datetime.now(),
            'directContribution': direct_contribution
        }
        
        # Add optional properties if provided
        if impact_ratio is not None:
            relationship_props['impactRatio'] = impact_ratio
        if recognition_score is not None:
            relationship_props['recognitionScore'] = recognition_score
        if verified_by:
            relationship_props['verifiedBy'] = verified_by
        if verification_date:
            relationship_props['verificationDate'] = verification_date
        if notes:
            relationship_props['notes'] = notes
        
        # Connect with relationship properties - note we need to use the same method as in WIN model
        # which connects in the opposite direction (from WIN to source)
        win.source_recognition_events.connect(event, relationship_props)
        
        return (event, win)
        
    def get_win_sources(self, win_uid: str) -> Dict[str, List]:
        """
        Retrieves all Projects and RecognitionEvents that led to a specific WIN.
        
        Returns:
            Dictionary with keys 'projects', 'recognition_events' and corresponding lists of entities.
        """
        win = self.get_win_by_uid(win_uid)
        if not win:
            return {'projects': [], 'recognition_events': []}
            
        # Get all connected Projects
        projects = list(win.source_projects.all())
        
        # Get all connected RecognitionEvents (filtering Event nodes by event_type)
        all_events = win.source_recognition_events.all()
        recognition_events = [event for event in all_events if event.event_type == 'RecognitionEvent']
        
        return {
            'projects': projects,
            'recognition_events': recognition_events
        }
        
    @db.transaction
    def disconnect_project_from_win(self, project_uid: str, win_uid: str) -> bool:
        """
        Removes the LEADS_TO_WIN relationship between a Project and a WIN.
        
        Returns True if disconnection was successful, False otherwise.
        """
        # 1. Get both the project and win nodes
        try:
            project = GraphProject.nodes.get(uid=project_uid)
        except GraphProject.DoesNotExist:
            return False
            
        try:
            win = GraphWIN.nodes.get(uid=win_uid)
        except GraphWIN.DoesNotExist:
            return False
            
        # 2. Remove the relationship
        project.leads_to_wins.disconnect(win)
        
        return True
        
    @db.transaction
    def disconnect_recognition_event_from_win(self, event_uid: str, win_uid: str) -> bool:
        """
        Removes the LEADS_TO_WIN relationship between a RecognitionEvent and a WIN.
        
        Returns True if disconnection was successful, False otherwise.
        """
        # 1. Get both the event and win nodes
        try:
            event = GraphEvent.nodes.get(uid=event_uid)
            if event.event_type != 'RecognitionEvent':
                return False
        except GraphEvent.DoesNotExist:
            return False
            
        try:
            win = GraphWIN.nodes.get(uid=win_uid)
        except GraphWIN.DoesNotExist:
            return False
            
        # 2. Remove the relationship - note we need to use the same method as in WIN model
        win.source_recognition_events.disconnect(event)
        
        return True
