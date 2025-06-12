from typing import Optional, List, Tuple
from neomodel import db
from trm_api.graph_models.agent import Agent as GraphAgent
from trm_api.graph_models.skill import GraphSkill
from trm_api.models.agent import AgentCreate, AgentUpdate  # Pydantic model for API data

class AgentRepository:
    def create_agent(self, agent_data: AgentCreate) -> GraphAgent:
        """
        Creates a new agent.
        """
        agent = GraphAgent(
            name=agent_data.name,
            agent_type=agent_data.agent_type,
            description=agent_data.description,
            status=agent_data.status or 'active'
        ).save()
        return agent

    def get_agent_by_uid(self, uid: str) -> Optional[GraphAgent]:
        """
        Retrieves an agent by its unique ID.
        """
        try:
            return GraphAgent.nodes.get(uid=uid)
        except GraphAgent.DoesNotExist:
            return None

    def get_agent_by_name(self, name: str) -> Optional[GraphAgent]:
        """
        Retrieves an agent by name.
        """
        try:
            return GraphAgent.nodes.get(name=name)
        except GraphAgent.DoesNotExist:
            return None

    def list_agents(self, skip: int = 0, limit: int = 100) -> List[GraphAgent]:
        """
        Retrieves a list of all agents with pagination.
        """
        return GraphAgent.nodes.all()[skip:skip + limit]

    def update_agent(self, uid: str, agent_data: AgentUpdate) -> Optional[GraphAgent]:
        """
        Updates an existing agent.
        """
        agent = self.get_agent_by_uid(uid)
        if not agent:
            return None

        update_data = agent_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(agent, key, value)
        
        agent.save()
        return agent

    def delete_agent(self, uid: str) -> bool:
        """
        Deletes an agent by its unique ID.
        Returns True if deletion was successful, False otherwise.
        """
        agent = self.get_agent_by_uid(uid)
        if not agent:
            return False
        
        agent.delete()
        return True
        
    @db.transaction
    def add_skill_to_agent(self, agent_uid: str, skill_uid: str, 
                        proficiency_level: int = 1,
                        confidence_score: float = None,
                        endorsement_count: int = None,
                        years_experience: float = None,
                        last_used = None,
                        preference_rank: int = None,
                        notes: str = None) -> Optional[Tuple[GraphAgent, GraphSkill]]:
        """
        Establishes a HAS_SKILL relationship from an Agent to a Skill
        with all required properties according to the TRM Ontology V3.2.
        
        Args:
            agent_uid: UID of the agent
            skill_uid: UID of the skill
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
            Tuple of (agent, skill) if successful, None otherwise
        """
        import uuid
        from datetime import datetime
        
        # 1. Get both the agent and skill nodes
        agent = self.get_agent_by_uid(agent_uid)
        if not agent:
            return None
            
        try:
            skill = GraphSkill.nodes.get(uid=skill_uid)
        except GraphSkill.DoesNotExist:
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
        
        return (agent, skill)
        
    def get_agent_skills(self, agent_uid: str, skip: int = 0, limit: int = 100) -> List[GraphSkill]:
        """
        Retrieves all Skills that an Agent has.
        """
        agent = self.get_agent_by_uid(agent_uid)
        if not agent:
            return []
            
        # Get all skills connected with HAS_SKILL relationship
        return list(agent.has_skills.all()[skip:skip+limit])
        
    @db.transaction
    def remove_skill_from_agent(self, agent_uid: str, skill_uid: str) -> bool:
        """
        Removes the HAS_SKILL relationship between an Agent and a Skill.
        
        Returns True if disconnection was successful, False otherwise.
        """
        # 1. Get both the agent and skill nodes
        agent = self.get_agent_by_uid(agent_uid)
        if not agent:
            return False
            
        try:
            skill = GraphSkill.nodes.get(uid=skill_uid)
        except GraphSkill.DoesNotExist:
            return False
            
        # 2. Remove the relationship
        agent.has_skills.disconnect(skill)
        
        return True
