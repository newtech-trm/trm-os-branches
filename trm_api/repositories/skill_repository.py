from typing import Optional, List, Tuple
from neomodel import db
from trm_api.graph_models.skill import GraphSkill
from trm_api.graph_models.agent import Agent as GraphAgent
from trm_api.models.skill import SkillCreate, SkillUpdate  # Pydantic model for API data

class SkillRepository:
    def create_skill(self, skill_data: SkillCreate) -> GraphSkill:
        """
        Creates a new skill.
        """
        skill = GraphSkill(
            name=skill_data.name,
            description=skill_data.description,
            category=skill_data.category
        ).save()
        return skill

    def get_skill_by_uid(self, uid: str) -> Optional[GraphSkill]:
        """
        Retrieves a skill by its unique ID.
        """
        try:
            return GraphSkill.nodes.get(uid=uid)
        except GraphSkill.DoesNotExist:
            return None

    def get_skill_by_name(self, name: str) -> Optional[GraphSkill]:
        """
        Retrieves a skill by name.
        """
        try:
            return GraphSkill.nodes.get(name=name)
        except GraphSkill.DoesNotExist:
            return None

    def list_skills(self, skip: int = 0, limit: int = 100) -> List[GraphSkill]:
        """
        Retrieves a list of all skills with pagination.
        """
        return GraphSkill.nodes.all()[skip:skip + limit]

    def update_skill(self, uid: str, skill_data: SkillUpdate) -> Optional[GraphSkill]:
        """
        Updates an existing skill.
        """
        skill = self.get_skill_by_uid(uid)
        if not skill:
            return None

        update_data = skill_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(skill, key, value)
        
        skill.save()
        return skill

    def delete_skill(self, uid: str) -> bool:
        """
        Deletes a skill by its unique ID.
        Returns True if deletion was successful, False otherwise.
        """
        skill = self.get_skill_by_uid(uid)
        if not skill:
            return False
        
        skill.delete()
        return True
        
    @db.transaction
    def connect_skill_to_agent(self, skill_uid: str, agent_uid: str,
                            proficiency_level: int = 1,
                            confidence_score: float = None,
                            endorsement_count: int = None,
                            years_experience: float = None,
                            last_used = None,
                            preference_rank: int = None,
                            notes: str = None) -> Optional[Tuple[GraphSkill, GraphAgent]]:
        """
        Establishes a HAS_SKILL relationship from an Agent to a Skill
        with all required properties according to the TRM Ontology V3.2.
        
        Args:
            skill_uid: UID of the skill
            agent_uid: UID of the agent
            proficiency_level: Proficiency level (1-5) 
                1: Novice
                2: Advanced Beginner
                3: Competent
                4: Proficient
                5: Expert
            confidence_score: Confidence score (0.0-1.0) for this skill assessment
            endorsement_count: Number of endorsements for this skill
            years_experience: Years of experience with this skill
            last_used: DateTime when this skill was last used
            preference_rank: Preference rank for this skill (lower = higher preference)
            notes: Additional notes about this relationship
            
        Returns:
            Tuple of (skill, agent) if successful, None otherwise
        """
        import uuid
        from datetime import datetime
        
        # 1. Get both the skill and agent nodes
        skill = self.get_skill_by_uid(skill_uid)
        if not skill:
            return None
            
        try:
            agent = GraphAgent.nodes.get(uid=agent_uid)
        except GraphAgent.DoesNotExist:
            return None
        
        # 2. Create the HAS_SKILL relationship with all properties
        relationship_props = {
            'relationshipId': str(uuid.uuid4()),
            'proficiencyLevel': proficiency_level,
            'creationDate': datetime.now(),
            'lastModifiedDate': datetime.now()
        }
        
        # Add optional properties if provided
        if confidence_score is not None:
            relationship_props['confidenceScore'] = confidence_score
        if endorsement_count is not None:
            relationship_props['endorsementCount'] = endorsement_count
        if years_experience is not None:
            relationship_props['yearsExperience'] = years_experience
        if last_used:
            relationship_props['lastUsed'] = last_used
        if preference_rank is not None:
            relationship_props['preferenceRank'] = preference_rank
        if notes:
            relationship_props['notes'] = notes
            
        # Connect with relationship properties
        agent.has_skills.connect(skill, relationship_props)
        
        return (skill, agent)
        
    def get_agents_with_skill(self, skill_uid: str, skip: int = 0, limit: int = 100) -> List[GraphAgent]:
        """
        Retrieves all Agents that have a specific Skill.
        """
        skill = self.get_skill_by_uid(skill_uid)
        if not skill:
            return []
            
        # Get all agents connected with HAS_SKILL relationship
        return list(skill.skilled_agents.all()[skip:skip+limit])
