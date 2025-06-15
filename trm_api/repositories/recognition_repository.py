from typing import Optional, List, Dict, Any
from neomodel import db

from trm_api.models.recognition import RecognitionCreate, RecognitionUpdate
from trm_api.graph_models.recognition import Recognition as GraphRecognition
from trm_api.graph_models.user import User as GraphUser
from trm_api.graph_models.win import WIN as GraphWIN

class RecognitionRepository:
    """
    Repository for handling all database operations related to Recognitions.
    """

    @db.transaction
    def create_recognition(self, recognition_data: RecognitionCreate) -> GraphRecognition:
        """
        Creates a new Recognition node and establishes relationships.
        """
        # Convert Pydantic model to dictionary for graph model
        data = recognition_data.model_dump(by_alias=True)
        
        # Create the Recognition node
        recognition = GraphRecognition(**data).save()
        
        # Establish relationship with granter user (GIVES_RECOGNITION)
        try:
            granter = GraphUser.nodes.get(uid=recognition_data.granter_user_id)
            granter.given_recognitions.connect(recognition)
        except GraphUser.DoesNotExist:
            # User doesn't exist, but we'll create the Recognition anyway
            pass
        
        # Establish relationships with recipient users (RECEIVES_RECOGNITION)
        for recipient_id in recognition_data.recipient_user_ids:
            try:
                recipient = GraphUser.nodes.get(uid=recipient_id)
                recognition.received_by.connect(recipient)
            except GraphUser.DoesNotExist:
                # User doesn't exist, skip this relationship
                continue
        
        # Establish relationship with WIN (RECOGNIZES)
        try:
            win = GraphWIN.nodes.get(uid=recognition_data.win_id)
            recognition.recognizes_win.connect(win)
        except GraphWIN.DoesNotExist:
            # WIN doesn't exist, but we'll create the Recognition anyway
            pass
        
        return recognition

    def get_recognition_by_uid(self, uid: str) -> Optional[GraphRecognition]:
        """
        Retrieves a Recognition node by its unique ID.
        """
        try:
            return GraphRecognition.nodes.get(uid=uid)
        except GraphRecognition.DoesNotExist:
            return None

    def list_recognitions(self, skip: int = 0, limit: int = 100) -> List[GraphRecognition]:
        """
        Lists all Recognition nodes with pagination.
        """
        return GraphRecognition.nodes.all()[skip:skip+limit]
    
    def list_recognitions_by_win(self, win_id: str, skip: int = 0, limit: int = 100) -> List[GraphRecognition]:
        """
        Lists all Recognition nodes for a specific WIN.
        """
        return GraphRecognition.nodes.filter(winId=win_id)[skip:skip+limit]
    
    def list_recognitions_by_granter(self, user_id: str, skip: int = 0, limit: int = 100) -> List[GraphRecognition]:
        """
        Lists all Recognition nodes given by a specific user.
        """
        return GraphRecognition.nodes.filter(granterUserId=user_id)[skip:skip+limit]
    
    def list_recognitions_for_recipient(self, user_id: str, skip: int = 0, limit: int = 100) -> List[GraphRecognition]:
        """
        Lists all Recognition nodes where a specific user is a recipient.
        This requires a custom Cypher query since we need to check an array property.
        """
        # Using Cypher query to check if user_id is in the recipientUserIds array
        query = """
        MATCH (r:Recognition)
        WHERE $user_id IN r.recipientUserIds
        RETURN r
        ORDER BY r.createdAt DESC
        SKIP $skip LIMIT $limit
        """
        results, meta = db.cypher_query(
            query, 
            {"user_id": user_id, "skip": skip, "limit": limit}
        )
        
        return [GraphRecognition.inflate(row[0]) for row in results]

    def update_recognition(self, uid: str, update_data: RecognitionUpdate) -> Optional[GraphRecognition]:
        """
        Updates an existing Recognition node.
        Since recognitions are mostly immutable, this only updates allowed fields like message.
        """
        recognition = self.get_recognition_by_uid(uid)
        if not recognition:
            return None

        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(recognition, key, value)
        
        recognition.save()
        return recognition

    def delete_recognition(self, uid: str) -> bool:
        """
        Deletes a Recognition node by its unique ID.
        """
        recognition = self.get_recognition_by_uid(uid)
        if not recognition:
            return False
        
        recognition.delete()
        return True
