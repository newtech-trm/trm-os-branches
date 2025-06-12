from neomodel import (
    StructuredRel,
    StringProperty,
    IntegerProperty,
    FloatProperty,
    DateTimeProperty,
    RelationshipTo,
    RelationshipFrom
)
from datetime import datetime

class HasSkillRel(StructuredRel):
    """
    Relationship class for HAS_SKILL, connecting Agent or User -> Skill.
    Following the TRM Ontology V3.2 specification.
    """
    # Required properties
    relationshipId = StringProperty(unique_index=True, required=True)
    proficiencyLevel = IntegerProperty(
        default=1,  # Không thể dùng cả required=True và default cùng lúc
        choices={
            1: 'Novice',
            2: 'Advanced Beginner',
            3: 'Competent',
            4: 'Proficient',
            5: 'Expert'
        }
    )
    creationDate = DateTimeProperty(default=datetime.now)
    lastModifiedDate = DateTimeProperty(default=datetime.now)
    
    # Optional properties
    confidenceScore = FloatProperty(default=0.5)  # 0.0 to 1.0
    endorsementCount = IntegerProperty(default=0)
    yearsExperience = FloatProperty()
    lastUsed = DateTimeProperty()
    preferenceRank = IntegerProperty()  # lower = higher preference
    notes = StringProperty()
