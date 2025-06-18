from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from enum import Enum

from trm_api.models.relationships import Relationship, RelationshipType, TargetEntityTypeEnum
from trm_api.services.relationship_service import relationship_service, RelationshipService

router = APIRouter()

class DirectionEnum(str, Enum):
    OUTGOING = "outgoing"
    INCOMING = "incoming"
    BOTH = "both"

@router.post("/", response_model=Relationship, status_code=status.HTTP_201_CREATED)
def create_relationship(
    source_id: str,
    source_type: TargetEntityTypeEnum,
    target_id: str,
    target_type: TargetEntityTypeEnum,
    relationship_type: RelationshipType,
    service: RelationshipService = Depends(lambda: relationship_service)
):
    """
    Create a new relationship between two entities.
    
    Parameters:
    - source_id: The ID of the source entity
    - source_type: The type of the source entity
    - target_id: The ID of the target entity
    - target_type: The type of the target entity
    - relationship_type: The type of relationship to create
    
    Returns:
    - The created relationship
    """
    relationship = service.create_relationship(
        source_id=source_id,
        source_type=source_type,
        target_id=target_id,
        target_type=target_type,
        relationship_type=relationship_type
    )
    
    if not relationship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not create relationship. One or both entities may not exist."
        )
        
    return relationship

@router.get("/", response_model=List[Relationship])
def get_relationships(
    entity_id: Optional[str] = None,
    entity_type: Optional[str] = None,
    direction: DirectionEnum = DirectionEnum.OUTGOING,
    relationship_type: Optional[RelationshipType] = None,
    related_entity_type: Optional[TargetEntityTypeEnum] = None,
    service: RelationshipService = Depends(lambda: relationship_service)
):
    """
    Get relationships for an entity.
    
    Parameters:
    - entity_id: The ID of the entity
    - entity_type: The type of the entity
    - direction: The direction of the relationships (outgoing, incoming, both)
    - relationship_type: Optional filter for a specific relationship type
    - related_entity_type: Optional filter for a specific related entity type
    
    Returns:
    - A list of relationships
    """
    # Khi cả hai tham số entity_id và entity_type là None, trả về danh sách rỗng thay vì gọi service
    if entity_id is None or entity_type is None:
        print("WARNING: entity_id hoặc entity_type là None, trả về danh sách rỗng")
        return []
    
    try:
        return service.get_relationships(
            entity_id=entity_id,
            entity_type=entity_type,
            direction=direction,
            relationship_type=relationship_type,
            related_entity_type=related_entity_type
        )
    except Exception as e:
        print(f"Lỗi khi lấy relationships: {str(e)}")
        # Trong trường hợp có lỗi, trả về danh sách rỗng thay vì là lỗi
        return []

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_relationship(
    source_id: str,
    source_type: TargetEntityTypeEnum,
    target_id: str,
    target_type: TargetEntityTypeEnum,
    relationship_type: RelationshipType,
    service: RelationshipService = Depends(lambda: relationship_service)
):
    """
    Delete a relationship between two entities.
    
    Parameters:
    - source_id: The ID of the source entity
    - source_type: The type of the source entity
    - target_id: The ID of the target entity
    - target_type: The type of the target entity
    - relationship_type: The type of relationship to delete
    
    Returns:
    - 204 No Content if successful
    """
    success = service.delete_relationship(
        source_id=source_id,
        source_type=source_type,
        target_id=target_id,
        target_type=target_type,
        relationship_type=relationship_type
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relationship not found or could not be deleted."
        )

# --- Specific Named Relationship Endpoints ---

@router.post("/creates-knowledge", response_model=Relationship)
def create_creates_knowledge_relationship(
    source_id: str,
    source_type: TargetEntityTypeEnum,
    knowledge_id: str,
    service: RelationshipService = Depends(lambda: relationship_service)
):
    """
    Create a CREATES_KNOWLEDGE relationship from an entity (User/Agent/Task) to a KnowledgeSnippet.
    
    Parameters:
    - source_id: The ID of the entity creating the knowledge
    - source_type: The type of entity (User, Agent, or Task)
    - knowledge_id: The ID of the KnowledgeSnippet
    
    Returns:
    - The created relationship
    """
    if source_type not in [TargetEntityTypeEnum.USER, TargetEntityTypeEnum.AGENT, TargetEntityTypeEnum.TASK]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid source type. Must be one of: User, Agent, Task."
        )
    
    relationship = service.create_relationship(
        source_id=source_id,
        source_type=source_type,
        target_id=knowledge_id,
        target_type=TargetEntityTypeEnum.KNOWLEDGE_SNIPPET,
        relationship_type=RelationshipType.CREATES_KNOWLEDGE
    )
    
    if not relationship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not create relationship. Source or KnowledgeSnippet may not exist."
        )
        
    return relationship

@router.post("/uses-knowledge", response_model=Relationship)
def create_uses_knowledge_relationship(
    source_id: str,
    source_type: TargetEntityTypeEnum,
    knowledge_id: str,
    service: RelationshipService = Depends(lambda: relationship_service)
):
    """
    Create a USES_KNOWLEDGE relationship from an entity (User/Agent/Task) to a KnowledgeSnippet.
    
    Parameters:
    - source_id: The ID of the entity using the knowledge
    - source_type: The type of entity (User, Agent, or Task)
    - knowledge_id: The ID of the KnowledgeSnippet
    
    Returns:
    - The created relationship
    """
    if source_type not in [TargetEntityTypeEnum.USER, TargetEntityTypeEnum.AGENT, TargetEntityTypeEnum.TASK]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid source type. Must be one of: User, Agent, Task."
        )
    
    relationship = service.create_relationship(
        source_id=source_id,
        source_type=source_type,
        target_id=knowledge_id,
        target_type=TargetEntityTypeEnum.KNOWLEDGE_SNIPPET,
        relationship_type=RelationshipType.USES_KNOWLEDGE
    )
    
    if not relationship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not create relationship. Source or KnowledgeSnippet may not exist."
        )
        
    return relationship

@router.post("/triggered-by", response_model=Relationship)
def create_triggered_by_relationship(
    source_id: str,
    source_type: TargetEntityTypeEnum,
    trigger_id: str,
    trigger_type: TargetEntityTypeEnum,
    service: RelationshipService = Depends(lambda: relationship_service)
):
    """
    Create a TRIGGERED_BY relationship to indicate what triggered an entity.
    
    Parameters:
    - source_id: The ID of the entity that was triggered
    - source_type: The type of entity (e.g., Event, Task, Tension)
    - trigger_id: The ID of the entity that triggered it
    - trigger_type: The type of the trigger entity (e.g., Event, Task, User)
    
    Returns:
    - The created relationship
    """
    valid_source_types = [TargetEntityTypeEnum.EVENT, TargetEntityTypeEnum.TASK, TargetEntityTypeEnum.TENSION]
    valid_trigger_types = [TargetEntityTypeEnum.EVENT, TargetEntityTypeEnum.TASK, TargetEntityTypeEnum.USER]
    
    if source_type not in valid_source_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid source type. Must be one of: Event, Task, Tension."
        )
        
    if trigger_type not in valid_trigger_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid trigger type. Must be one of: Event, Task, User."
        )
    
    relationship = service.create_relationship(
        source_id=source_id,
        source_type=source_type,
        target_id=trigger_id,
        target_type=trigger_type,
        relationship_type=RelationshipType.TRIGGERED_BY
    )
    
    if not relationship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not create relationship. Source or trigger entity may not exist."
        )
        
    return relationship

@router.post("/triggers", response_model=Relationship)
def create_triggers_relationship(
    source_id: str,
    source_type: TargetEntityTypeEnum,
    target_id: str,
    target_type: TargetEntityTypeEnum,
    service: RelationshipService = Depends(lambda: relationship_service)
):
    """
    Create a TRIGGERS relationship to indicate what an entity triggers.
    
    Parameters:
    - source_id: The ID of the entity that triggers
    - source_type: The type of entity (e.g., Event, Task, User)
    - target_id: The ID of the entity that is triggered
    - target_type: The type of the triggered entity (e.g., Event, Task, Tension)
    
    Returns:
    - The created relationship
    """
    valid_source_types = [TargetEntityTypeEnum.EVENT, TargetEntityTypeEnum.TASK, TargetEntityTypeEnum.USER]
    valid_target_types = [TargetEntityTypeEnum.EVENT, TargetEntityTypeEnum.TASK, TargetEntityTypeEnum.TENSION]
    
    if source_type not in valid_source_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid source type. Must be one of: Event, Task, User."
        )
        
    if target_type not in valid_target_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid target type. Must be one of: Event, Task, Tension."
        )
    
    relationship = service.create_relationship(
        source_id=source_id,
        source_type=source_type,
        target_id=target_id,
        target_type=target_type,
        relationship_type=RelationshipType.TRIGGERS
    )
    
    if not relationship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not create relationship. Source or target entity may not exist."
        )
        
    return relationship

@router.post("/related-to", response_model=Relationship)
def create_related_to_relationship(
    source_id: str,
    source_type: TargetEntityTypeEnum,
    related_id: str,
    related_type: TargetEntityTypeEnum,
    service: RelationshipService = Depends(lambda: relationship_service)
):
    """
    Create a RELATED_TO relationship between any two entities.
    
    Parameters:
    - source_id: The ID of the source entity
    - source_type: The type of the source entity
    - related_id: The ID of the related entity
    - related_type: The type of the related entity
    
    Returns:
    - The created relationship
    """
    relationship = service.create_relationship(
        source_id=source_id,
        source_type=source_type,
        target_id=related_id,
        target_type=related_type,
        relationship_type=RelationshipType.RELATED_TO
    )
    
    if not relationship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not create relationship. One or both entities may not exist."
        )
        
    return relationship
