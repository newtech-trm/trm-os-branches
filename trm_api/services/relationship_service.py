from neo4j import Driver
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import traceback

from trm_api.db.session import get_driver
from trm_api.models.relationships import Relationship, RelationshipType, TargetEntityTypeEnum
from trm_api.services.utils import process_relationship_record


class RelationshipService:
    """
    Service layer for handling business logic related to Relationships.
    This service handles creation, querying, and management of all relationship types.
    """

    def _get_db(self) -> Driver:
        return get_driver()

    def create_relationship(
        self,
        source_id: str,
        source_type: TargetEntityTypeEnum,
        target_id: str,
        target_type: TargetEntityTypeEnum,
        relationship_type: RelationshipType,
    ) -> Optional[Relationship]:
        """
        Creates a relationship between two entities.
        
        Args:
            source_id: The ID of the source entity
            source_type: The type of the source entity
            target_id: The ID of the target entity
            target_type: The type of the target entity
            relationship_type: The type of relationship to create
            
        Returns:
            The created relationship or None if creation failed
        """
        with self._get_db().session() as session:
            result = session.execute_write(
                self._create_relationship_tx,
                source_id,
                source_type,
                target_id,
                target_type,
                relationship_type
            )
            return result

    @staticmethod
    def _create_relationship_tx(
        tx,
        source_id: str,
        source_type: TargetEntityTypeEnum,
        target_id: str,
        target_type: TargetEntityTypeEnum,
        relationship_type: RelationshipType,
    ) -> Optional[Relationship]:
        """
        Transaction function for creating a relationship.
        Uses dynamic labels based on the entity types.
        """
        query = (
            "MATCH (source) "
            "WHERE (source:{source_type}) AND "
            "(source.{source_id_field} = $source_id OR source.uid = $source_id) "
            "MATCH (target) "
            "WHERE (target:{target_type}) AND "
            "(target.{target_id_field} = $target_id OR target.uid = $target_id) "
            "MERGE (source)-[rel:{rel_type}]->(target) "
            "ON CREATE SET rel.createdAt = datetime() "
            "RETURN "
            "    source.uid AS source_id, "
            "    '{source_type}' AS source_type, "
            "    target.uid AS target_id, "
            "    '{target_type}' AS target_type, "
            "    type(rel) AS type, "
            "    rel.createdAt as createdAt"
        )

        # Map entity types to their ID field names (based on convention)
        id_field_map = {
            "User": "userId",
            "Team": "teamId",
            "Project": "projectId",
            "Task": "taskId",
            "Tension": "tensionId",
            "Win": "winId",
            "KnowledgeSnippet": "snippetId",
            "Skill": "skillId",
            "Recognition": "recognitionId",
            "Resource": "resourceId",
            "Agent": "agentId",
            "Event": "eventId",
            "Tool": "toolId"
        }

        # Format query with the right labels and ID fields
        source_type_value = source_type.value if isinstance(source_type, TargetEntityTypeEnum) else source_type
        target_type_value = target_type.value if isinstance(target_type, TargetEntityTypeEnum) else target_type
        rel_type_value = relationship_type.value if isinstance(relationship_type, RelationshipType) else relationship_type

        source_id_field = id_field_map.get(source_type_value, "uid")
        target_id_field = id_field_map.get(target_type_value, "uid")

        formatted_query = query.format(
            source_type=source_type_value,
            source_id_field=source_id_field,
            target_type=target_type_value,
            target_id_field=target_id_field,
            rel_type=rel_type_value
        )

        result = tx.run(
            formatted_query,
            source_id=source_id,
            target_id=target_id,
        )
        record = result.single()
        
        if record:
            return Relationship(
                source_id=record["source_id"],
                source_type=record["source_type"],
                target_id=record["target_id"],
                target_type=record["target_type"],
                type=record["type"],
                createdAt=record["createdAt"]
            )
        return None

    def get_relationships(
        self,
        entity_id: Optional[str] = None,
        entity_type: Optional[str] = None,
        direction: str = "outgoing",
        relationship_type: Optional[RelationshipType] = None,
        related_entity_type: Optional[TargetEntityTypeEnum] = None
    ) -> List[Relationship]:
        """Lấy các mối quan hệ của một thực thể. Được thiết kế để xử lý linh hoạt mọi đầu vào."""
        """
        Gets all relationships for a specific entity.
        
        Args:
            entity_id: The ID of the entity, if None returns all relationships
            entity_type: The type of the entity, if None returns all relationships
            direction: "outgoing" for relationships where the entity is the source,
                       "incoming" for relationships where the entity is the target,
                       "both" for relationships in both directions
            relationship_type: Optional filter for a specific relationship type
            related_entity_type: Optional filter for a specific related entity type
            
        Returns:
            A list of relationships for the entity
        """
        # Ghi log chi tiết các tham số
        print(f"\n===== GET RELATIONSHIPS PARAMS =====")
        print(f"entity_id: {entity_id}")
        print(f"entity_type: {entity_type}")
        print(f"direction: {direction}")
        print(f"relationship_type: {relationship_type}")
        print(f"related_entity_type: {related_entity_type}")
        print(f"==================================\n")
        
        # Nếu không có entity_id hoặc entity_type, trả về danh sách rỗng ngay lập tức
        if not entity_id or not entity_type:
            print(f"Trả về danh sách rỗng vì entity_id hoặc entity_type bị thiếu")
            return []

        # Chuyển đổi entity_type thành định dạng nội bộ, hỗ trợ cả string và enum
        try:
            # Xử lý entity_type dưới dạng string
            if isinstance(entity_type, str):
                entity_type_mapped = EntityTypeKindMapping.get(entity_type, entity_type)
            else:
                # Nếu là enum hoặc kiểu khác, thử chuyển thành string
                entity_type_str = str(entity_type)
                entity_type_mapped = EntityTypeKindMapping.get(entity_type_str, entity_type_str)
                
            print(f"Đã chuyển đổi entity_type: {entity_type} -> {entity_type_mapped}")
        except Exception as e:
            print(f"Lỗi khi chuyển đổi entity_type: {str(e)}")
            entity_type_mapped = str(entity_type) if entity_type else "Unknown"
        
        try:  
            with self._get_db().session() as session:
                print(f"Thực thi truy vấn Neo4j cho entity_id={entity_id}, entity_type={entity_type_mapped}")
                result = session.read_transaction(
                    self._get_relationships_tx, 
                    entity_id,
                    entity_type_mapped,
                    direction,
                    relationship_type,
                    related_entity_type
                )
                print(f"Đã tìm thấy {len(result)} mối quan hệ")
                return result
        except Exception as e:
            print(f"===== LỖI KHI LẤY RELATIONSHIPS =====\n{str(e)}\n{traceback.format_exc()}\n=============================")
            # Trả về danh sách rỗng thay vì lỗi
            return []

    @staticmethod
    def _get_relationships_tx(
        tx,
        entity_id: str,
        entity_type: str,
        direction: str,
        relationship_type: Optional[RelationshipType],
        related_entity_type: Optional[TargetEntityTypeEnum]
    ) -> List[Relationship]:
        """
        Transaction function for getting relationships.
        """
        # Map entity types to their ID field names
        id_field_map = {
            "User": "userId",
            "Team": "teamId",
            "Project": "projectId",
            "Task": "taskId",
            "Tension": "tensionId",
            "Win": "winId",
            "KnowledgeSnippet": "snippetId",
            "Skill": "skillId",
            "Recognition": "recognitionId",
            "Resource": "resourceId",
            "Agent": "agentId",
            "Event": "eventId",
            "Tool": "toolId"
        }

        entity_type_value = entity_type.value if isinstance(entity_type, TargetEntityTypeEnum) else entity_type
        entity_id_field = id_field_map.get(entity_type_value, "uid")
        rel_type = relationship_type.value if relationship_type else None
        related_type = related_entity_type.value if related_entity_type else None

        # Build the query based on direction and filters
        if direction == "outgoing":
            query_template = (
                "MATCH (entity:{entity_type})-[rel{rel_filter}]->(related{related_filter}) "
                "WHERE entity.{id_field} = $entity_id OR entity.uid = $entity_id "
                "RETURN "
                "    entity.uid AS source_id, "
                "    '{entity_type}' AS source_type, "
                "    related.uid AS target_id, "
                "    labels(related)[0] AS target_type, "
                "    type(rel) AS type, "
                "    CASE WHEN rel.createdAt IS NOT NULL THEN rel.createdAt ELSE datetime() END AS createdAt"
            )
        elif direction == "incoming":
            query_template = (
                "MATCH (related{related_filter})-[rel{rel_filter}]->(entity:{entity_type}) "
                "WHERE entity.{id_field} = $entity_id OR entity.uid = $entity_id "
                "RETURN "
                "    related.uid AS source_id, "
                "    labels(related)[0] AS source_type, "
                "    entity.uid AS target_id, "
                "    '{entity_type}' AS target_type, "
                "    type(rel) AS type, "
                "    CASE WHEN rel.createdAt IS NOT NULL THEN rel.createdAt ELSE datetime() END AS createdAt"
            )
        else:  # both
            query_template = (
                "MATCH (entity:{entity_type})-[rel{rel_filter}]-(related{related_filter}) "
                "WHERE entity.{id_field} = $entity_id OR entity.uid = $entity_id "
                "RETURN "
                "    CASE WHEN startNode(rel) = entity THEN entity.uid ELSE related.uid END AS source_id, "
                "    CASE WHEN startNode(rel) = entity THEN '{entity_type}' ELSE labels(related)[0] END AS source_type, "
                "    CASE WHEN endNode(rel) = entity THEN entity.uid ELSE related.uid END AS target_id, "
                "    CASE WHEN endNode(rel) = entity THEN '{entity_type}' ELSE labels(related)[0] END AS target_type, "
                "    type(rel) AS type, "
                "    CASE WHEN rel.createdAt IS NOT NULL THEN rel.createdAt ELSE datetime() END AS createdAt"
            )

        # Add filters if specified
        rel_filter = f":{rel_type}" if rel_type else ""
        related_filter = f":{related_type}" if related_type else ""

        query = query_template.format(
            entity_type=entity_type_value,
            id_field=entity_id_field,
            rel_filter=rel_filter,
            related_filter=related_filter
        )

        result = tx.run(query, entity_id=entity_id)
        relationships = []

        for record in result:
            relationships.append(
                Relationship(
                    source_id=record["source_id"],
                    source_type=record["source_type"],
                    target_id=record["target_id"],
                    target_type=record["target_type"],
                    type=record["type"],
                    createdAt=record["createdAt"]
                )
            )
        
        return relationships

    def delete_relationship(
        self,
        source_id: str,
        source_type: TargetEntityTypeEnum,
        target_id: str,
        target_type: TargetEntityTypeEnum,
        relationship_type: RelationshipType
    ) -> bool:
        """
        Deletes a relationship between two entities.
        
        Args:
            source_id: The ID of the source entity
            source_type: The type of the source entity
            target_id: The ID of the target entity
            target_type: The type of the target entity
            relationship_type: The type of relationship to delete
            
        Returns:
            True if the relationship was deleted, False otherwise
        """
        with self._get_db().session() as session:
            result = session.execute_write(
                self._delete_relationship_tx,
                source_id,
                source_type,
                target_id,
                target_type,
                relationship_type
            )
            return result

    @staticmethod
    def _delete_relationship_tx(
        tx,
        source_id: str,
        source_type: TargetEntityTypeEnum,
        target_id: str,
        target_type: TargetEntityTypeEnum,
        relationship_type: RelationshipType
    ) -> bool:
        """
        Transaction function for deleting a relationship.
        """
        # Map entity types to their ID field names
        id_field_map = {
            "User": "userId",
            "Team": "teamId",
            "Project": "projectId",
            "Task": "taskId",
            "Tension": "tensionId",
            "Win": "winId",
            "KnowledgeSnippet": "snippetId",
            "Skill": "skillId",
            "Recognition": "recognitionId",
            "Resource": "resourceId",
            "Agent": "agentId",
            "Event": "eventId",
            "Tool": "toolId"
        }

        source_type_value = source_type.value if isinstance(source_type, TargetEntityTypeEnum) else source_type
        target_type_value = target_type.value if isinstance(target_type, TargetEntityTypeEnum) else target_type
        rel_type_value = relationship_type.value if isinstance(relationship_type, RelationshipType) else relationship_type

        source_id_field = id_field_map.get(source_type_value, "uid")
        target_id_field = id_field_map.get(target_type_value, "uid")

        query = (
            f"MATCH (source:{source_type_value})-[rel:{rel_type_value}]->(target:{target_type_value}) "
            f"WHERE (source.{source_id_field} = $source_id OR source.uid = $source_id) "
            f"AND (target.{target_id_field} = $target_id OR target.uid = $target_id) "
            f"DELETE rel"
        )

        result = tx.run(
            query,
            source_id=source_id,
            target_id=target_id
        )
        summary = result.consume()
        return summary.counters.relationships_deleted > 0


# Singleton instance of the service
relationship_service = RelationshipService()
