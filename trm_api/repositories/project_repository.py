from typing import Optional, List
from trm_api.graph_models.project import Project as GraphProject
from trm_api.models.project import ProjectCreate, ProjectUpdate # This is the Pydantic model for API data

class ProjectRepository:
    def create_project(self, project_data: ProjectCreate) -> GraphProject:
        """
        Creates a new project.
        """
        project = GraphProject(
            title=project_data.title,
            description=project_data.description,
            status=project_data.status
        ).save()
        return project

    def get_project_by_uid(self, uid: str) -> Optional[GraphProject]:
        """
        Retrieves a project by its unique ID.
        """
        try:
            return GraphProject.nodes.get(uid=uid)
        except GraphProject.DoesNotExist:
            return None

    def list_projects(self, skip: int = 0, limit: int = 100) -> List[GraphProject]:
        """
        Retrieves a list of all projects with pagination.
        """
        return GraphProject.nodes.all()[skip:skip + limit]

    def update_project(self, uid: str, project_data: ProjectUpdate) -> Optional[GraphProject]:
        """
        Updates an existing project.
        """
        project = self.get_project_by_uid(uid)
        if not project:
            return None

        update_data = project_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(project, key, value)
        
        project.save()
        return project

    def delete_project(self, uid: str) -> bool:
        """
        Deletes a project by its unique ID.
        Returns True if deletion was successful, False otherwise.
        """
        project = self.get_project_by_uid(uid)
        if not project:
            return False
        
        project.delete()
        return True
