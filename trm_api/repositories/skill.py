from typing import List, Optional
from ..graph_models.skill import GraphSkill
from ..api.v1.models.skill import SkillCreate, SkillUpdate

class SkillRepository:
    """
    Repository for handling CRUD operations for Skills.
    """

    def create_skill(self, skill_data: SkillCreate) -> GraphSkill:
        """
        Creates a new skill node in the database.
        
        Args:
            skill_data: Pydantic model with skill creation data.
            
        Returns:
            The newly created GraphSkill object.
        """
        skill = GraphSkill(**skill_data.model_dump()).save()
        return skill

    def get_skill_by_uid(self, uid: str) -> Optional[GraphSkill]:
        """
        Retrieves a single skill by its UID.
        
        Args:
            uid: The unique identifier of the skill.
            
        Returns:
            A GraphSkill object or None if not found.
        """
        return GraphSkill.nodes.get_or_none(uid=uid)

    def list_all_skills(self) -> List[GraphSkill]:
        """
        Lists all skill nodes in the database.
        
        Returns:
            A list of all GraphSkill objects.
        """
        return GraphSkill.nodes.all()

    def update_skill(self, uid: str, skill_data: SkillUpdate) -> Optional[GraphSkill]:
        """
        Updates an existing skill node.
        
        Args:
            uid: The UID of the skill to update.
            skill_data: Pydantic model with the fields to update.
            
        Returns:
            The updated GraphSkill object or None if not found.
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
        Deletes a skill node from the database.
        
        Args:
            uid: The UID of the skill to delete.
            
        Returns:
            True if deletion was successful, False otherwise.
        """
        skill = self.get_skill_by_uid(uid)
        if not skill:
            return False
        
        skill.delete()
        return True
