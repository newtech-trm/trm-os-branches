#!/usr/bin/env python
"""
Script for migrating and standardizing legacy Neo4j data to match TRM-OS Ontology V3.2.
This script performs data migration and standardization to ensure data consistency:
1. Standardizes enum values (RecognitionType, RecognitionStatus, WinType, WinStatus, etc.)
2. Converts datetime formats to ISO 8601
3. Fills in missing required fields with default values where appropriate
4. Validates data integrity and relationships
"""

import os
import logging
import sys
import json
from datetime import datetime
from neo4j import GraphDatabase
from dotenv import load_dotenv
from enum import Enum

# Thêm thư mục gốc vào sys.path để import từ các modules của dự án
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trm_api.adapters.enum_adapter import normalize_enum_value
from trm_api.adapters.datetime_adapter import normalize_datetime

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Neo4j connection settings
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# Enum definitions (matching with trm_api enums)
class RecognitionType(str, Enum):
    APPRECIATION = "Appreciation"
    GRATITUDE = "Gratitude"
    ACKNOWLEDGMENT = "Acknowledgment"
    PRAISE = "Praise"
    VALIDATION = "Validation"
    CELEBRATION = "Celebration"
    AWARD = "Award"

class RecognitionStatus(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    DRAFT = "Draft"
    ARCHIVED = "Archived"

class WinType(str, Enum):
    ACHIEVEMENT = "Achievement"
    MILESTONE = "Milestone"
    BREAKTHROUGH = "Breakthrough"
    COMPLETION = "Completion"
    IMPROVEMENT = "Improvement"
    INNOVATION = "Innovation"

class WinStatus(str, Enum):
    INITIATED = "Initiated"
    IN_PROGRESS = "InProgress"
    COMPLETED = "Completed"
    VERIFIED = "Verified"
    CELEBRATED = "Celebrated"

class SnippetType(str, Enum):
    LEARNING = "Learning"
    INSIGHT = "Insight"
    PROCESS = "Process"
    TECHNICAL = "Technical"
    KNOWLEDGE = "Knowledge"


class Neo4jDataMigrator:
    """Class for managing Neo4j data migration and standardization."""
    
    def __init__(self, uri, username, password):
        """Initialize with Neo4j connection parameters."""
        self.uri = uri
        self.username = username
        self.password = password
        self.driver = None
    
    def connect(self):
        """Connect to Neo4j database."""
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password))
            logger.info("Connected to Neo4j database.")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {str(e)}")
            raise
    
    def close(self):
        """Close Neo4j connection."""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed.")
    
    def migrate_all(self):
        """Run all migration functions."""
        try:
            self.connect()
            
            self.migrate_recognition_data()
            self.migrate_win_data()
            self.migrate_knowledge_snippet_data()
            self.standardize_relationship_properties()
            
            logger.info("Migration completed successfully!")
        except Exception as e:
            logger.error(f"Migration failed: {str(e)}")
            raise
        finally:
            self.close()
    
    def migrate_recognition_data(self):
        """Standardize Recognition entities."""
        logger.info("Starting Recognition data migration...")
        
        # Standardize RecognitionType and RecognitionStatus enum values
        with self.driver.session() as session:
            # 1. Get all Recognition nodes
            result = session.run("MATCH (r:Recognition) RETURN r.uid, r.recognitionType, r.status, r.createdAt")
            records = list(result)
            
            logger.info(f"Found {len(records)} Recognition nodes to migrate")
            
            # 2. Process each Recognition node
            for record in records:
                uid = record["r.uid"]
                recognition_type = record["r.recognitionType"]
                status = record["r.status"]
                created_at = record["r.createdAt"]
                
                # Normalize enum values
                normalized_type = normalize_enum_value(recognition_type, RecognitionType)
                normalized_status = normalize_enum_value(status, RecognitionStatus)
                
                # Normalize datetime
                normalized_created_at = normalize_datetime(created_at) if created_at else datetime.utcnow().isoformat()
                
                # Update the node
                session.run(
                    """
                    MATCH (r:Recognition {uid: $uid})
                    SET r.recognitionType = $normalized_type,
                        r.status = $normalized_status,
                        r.createdAt = $normalized_created_at
                    RETURN r
                    """,
                    uid=uid,
                    normalized_type=normalized_type,
                    normalized_status=normalized_status,
                    normalized_created_at=normalized_created_at
                )
                
                logger.info(f"Updated Recognition {uid}: {recognition_type} -> {normalized_type}, {status} -> {normalized_status}")
            
            # 3. Set default values for missing required properties
            session.run(
                """
                MATCH (r:Recognition)
                WHERE r.title IS NULL
                SET r.title = 'Untitled Recognition'
                """
            )
            
            session.run(
                """
                MATCH (r:Recognition)
                WHERE r.status IS NULL
                SET r.status = 'Active'
                """
            )
            
            session.run(
                """
                MATCH (r:Recognition)
                WHERE r.recognitionType IS NULL
                SET r.recognitionType = 'Appreciation'
                """
            )
        
        logger.info("Recognition data migration completed successfully.")
    
    def migrate_win_data(self):
        """Standardize WIN entities."""
        logger.info("Starting WIN data migration...")
        
        # Standardize WinType and WinStatus enum values
        with self.driver.session() as session:
            # 1. Get all WIN nodes
            result = session.run("MATCH (w:WIN) RETURN w.uid, w.winType, w.status, w.createdAt")
            records = list(result)
            
            logger.info(f"Found {len(records)} WIN nodes to migrate")
            
            # 2. Process each WIN node
            for record in records:
                uid = record["w.uid"]
                win_type = record["w.winType"]
                status = record["w.status"]
                created_at = record["w.createdAt"]
                
                # Normalize enum values
                normalized_type = normalize_enum_value(win_type, WinType)
                normalized_status = normalize_enum_value(status, WinStatus)
                
                # Normalize datetime
                normalized_created_at = normalize_datetime(created_at) if created_at else datetime.utcnow().isoformat()
                
                # Update the node
                session.run(
                    """
                    MATCH (w:WIN {uid: $uid})
                    SET w.winType = $normalized_type,
                        w.status = $normalized_status,
                        w.createdAt = $normalized_created_at
                    RETURN w
                    """,
                    uid=uid,
                    normalized_type=normalized_type,
                    normalized_status=normalized_status,
                    normalized_created_at=normalized_created_at
                )
                
                logger.info(f"Updated WIN {uid}: {win_type} -> {normalized_type}, {status} -> {normalized_status}")
            
            # 3. Set default values for missing required properties
            session.run(
                """
                MATCH (w:WIN)
                WHERE w.title IS NULL
                SET w.title = 'Untitled WIN'
                """
            )
            
            session.run(
                """
                MATCH (w:WIN)
                WHERE w.status IS NULL
                SET w.status = 'Initiated'
                """
            )
            
            session.run(
                """
                MATCH (w:WIN)
                WHERE w.winType IS NULL
                SET w.winType = 'Achievement'
                """
            )
        
        logger.info("WIN data migration completed successfully.")
    
    def migrate_knowledge_snippet_data(self):
        """Standardize KnowledgeSnippet entities."""
        logger.info("Starting KnowledgeSnippet data migration...")
        
        # Standardize SnippetType and ensure proper tags format
        with self.driver.session() as session:
            # 1. Get all KnowledgeSnippet nodes
            result = session.run("MATCH (ks:KnowledgeSnippet) RETURN ks.uid, ks.snippetType, ks.tags, ks.createdAt")
            records = list(result)
            
            logger.info(f"Found {len(records)} KnowledgeSnippet nodes to migrate")
            
            # 2. Process each KnowledgeSnippet node
            for record in records:
                uid = record["ks.uid"]
                snippet_type = record["ks.snippetType"]
                tags = record["ks.tags"]
                created_at = record["ks.createdAt"]
                
                # Normalize enum values
                normalized_type = normalize_enum_value(snippet_type, SnippetType)
                
                # Normalize tags (ensure it's a list of strings)
                normalized_tags = []
                if tags:
                    if isinstance(tags, str):
                        try:
                            # Try parsing as JSON string
                            parsed_tags = json.loads(tags)
                            if isinstance(parsed_tags, list):
                                normalized_tags = parsed_tags
                            else:
                                normalized_tags = [str(parsed_tags)]
                        except json.JSONDecodeError:
                            # If not JSON, treat as comma-separated values
                            normalized_tags = [tag.strip() for tag in tags.split(',')]
                    elif isinstance(tags, list):
                        normalized_tags = tags
                
                # Normalize datetime
                normalized_created_at = normalize_datetime(created_at) if created_at else datetime.utcnow().isoformat()
                
                # Update the node
                session.run(
                    """
                    MATCH (ks:KnowledgeSnippet {uid: $uid})
                    SET ks.snippetType = $normalized_type,
                        ks.tags = $normalized_tags,
                        ks.createdAt = $normalized_created_at
                    RETURN ks
                    """,
                    uid=uid,
                    normalized_type=normalized_type,
                    normalized_tags=normalized_tags,
                    normalized_created_at=normalized_created_at
                )
                
                logger.info(f"Updated KnowledgeSnippet {uid}: {snippet_type} -> {normalized_type}, tags standardized")
            
            # 3. Set default values for missing required properties
            session.run(
                """
                MATCH (ks:KnowledgeSnippet)
                WHERE ks.content IS NULL
                SET ks.content = 'Empty content'
                """
            )
            
            session.run(
                """
                MATCH (ks:KnowledgeSnippet)
                WHERE ks.snippetType IS NULL
                SET ks.snippetType = 'Knowledge'
                """
            )
            
            session.run(
                """
                MATCH (ks:KnowledgeSnippet)
                WHERE ks.tags IS NULL
                SET ks.tags = []
                """
            )
        
        logger.info("KnowledgeSnippet data migration completed successfully.")
    
    def standardize_relationship_properties(self):
        """Standardize properties on relationships."""
        logger.info("Starting relationship properties standardization...")
        
        with self.driver.session() as session:
            # 1. Standardize datetime properties on all relationships
            result = session.run(
                """
                MATCH ()-[r]-() 
                WHERE exists(r.createdAt) 
                RETURN type(r) as type, id(r) as id, r.createdAt as createdAt
                """
            )
            relationships = list(result)
            
            logger.info(f"Found {len(relationships)} relationships with datetime properties to standardize")
            
            for rel in relationships:
                rel_type = rel["type"]
                rel_id = rel["id"]
                created_at = rel["createdAt"]
                
                # Normalize datetime
                normalized_created_at = normalize_datetime(created_at) if created_at else datetime.utcnow().isoformat()
                
                # Update the relationship
                session.run(
                    """
                    MATCH ()-[r]-() 
                    WHERE id(r) = $rel_id
                    SET r.createdAt = $normalized_created_at
                    """,
                    rel_id=rel_id,
                    normalized_created_at=normalized_created_at
                )
                
                logger.info(f"Updated datetime on relationship {rel_type} (id: {rel_id})")
            
            # 2. Handle specific relationship types
            
            # GENERATES_KNOWLEDGE relationship
            generates_knowledge_rel = session.run(
                """
                MATCH (w:WIN)-[r:GENERATES_KNOWLEDGE]->(ks:KnowledgeSnippet)
                WHERE r.knowledgeCategory IS NULL OR r.relevanceLevel IS NULL
                RETURN r
                """
            )
            
            for rel in generates_knowledge_rel:
                session.run(
                    """
                    MATCH (w:WIN)-[r:GENERATES_KNOWLEDGE]->(ks:KnowledgeSnippet)
                    WHERE id(r) = $rel_id
                    SET r.knowledgeCategory = COALESCE(r.knowledgeCategory, 'LessonsLearned'),
                        r.relevanceLevel = COALESCE(r.relevanceLevel, 'Medium')
                    """,
                    rel_id=rel["r"].id
                )
            
            # RECOGNIZES_WIN relationship
            recognizes_win_rel = session.run(
                """
                MATCH (recog:Recognition)-[r:RECOGNIZES_WIN]->(w:WIN)
                WHERE r.recognitionLevel IS NULL OR r.impactMeasurement IS NULL
                RETURN r
                """
            )
            
            for rel in recognizes_win_rel:
                session.run(
                    """
                    MATCH (recog:Recognition)-[r:RECOGNIZES_WIN]->(w:WIN)
                    WHERE id(r) = $rel_id
                    SET r.recognitionLevel = COALESCE(r.recognitionLevel, 'Standard'),
                        r.impactMeasurement = COALESCE(r.impactMeasurement, 'Medium')
                    """,
                    rel_id=rel["r"].id
                )
            
            # LEADS_TO_WIN relationship
            leads_to_win_rel = session.run(
                """
                MATCH (p)-[r:LEADS_TO_WIN]->(w:WIN)
                WHERE p:Project OR p:Event
                AND (r.contributionLevel IS NULL OR r.directContribution IS NULL)
                RETURN r
                """
            )
            
            for rel in leads_to_win_rel:
                session.run(
                    """
                    MATCH (p)-[r:LEADS_TO_WIN]->(w:WIN)
                    WHERE id(r) = $rel_id
                    SET r.contributionLevel = COALESCE(r.contributionLevel, 'Medium'),
                        r.directContribution = COALESCE(r.directContribution, true),
                        r.impactRatio = COALESCE(r.impactRatio, 0.5)
                    """,
                    rel_id=rel["r"].id
                )
        
        logger.info("Relationship properties standardization completed successfully.")


def main():
    """Main function to run the migration."""
    try:
        logger.info("Starting Neo4j data migration...")
        
        # Create and run the migrator
        migrator = Neo4jDataMigrator(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)
        migrator.migrate_all()
        
        logger.info("Migration completed successfully!")
        return 0
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
