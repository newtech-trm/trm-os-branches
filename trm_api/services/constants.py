"""
Các hằng số được sử dụng trong các services.
Tuân thủ triệt để theo triết lý ontology-first.
"""

# Mapping giữa các loại entity trong API và các label Neo4j
EntityTypeKindMapping = {
    "USER": "User",
    "AGENT": "Agent",
    "TASK": "Task",
    "PROJECT": "Project",
    "TEAM": "Team",
    "RESOURCE": "Resource",
    "EVENT": "Event",
    "TENSION": "Tension",
    "KNOWLEDGE_SNIPPET": "KnowledgeSnippet",
    "WIN": "WIN",
    "RECOGNITION": "Recognition",
    "SKILL": "Skill",
}
