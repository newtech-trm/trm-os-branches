from typing import Optional, List
from neomodel import db

from trm_api.models.task import TaskCreate, TaskUpdate
from trm_api.graph_models.task import Task as GraphTask
from trm_api.graph_models.project import Project as GraphProject

class TaskRepository:
    """
    Repository for handling all database operations related to Tasks.
    This repository follows the new project-centric architecture.
    """

    @db.transaction
    def create_task(self, task_data: TaskCreate) -> Optional[GraphTask]:
        """
        Creates a new Task and connects it to a parent Project.

        This operation is transactional. If any step fails, the entire
        operation is rolled back.
        """
        # 1. Find the parent project for this task.
        try:
            project = GraphProject.nodes.get(uid=task_data.project_id)
        except GraphProject.DoesNotExist:
            # Can't create a task for a non-existent project.
            return None

        # 2. Create the new task node.
        # The 'name' field in Pydantic's TaskBase maps to 'name' in GraphTask.
        task_properties = task_data.model_dump(exclude={'project_id'})
        new_task = GraphTask(**task_properties).save()

        # 3. Create the relationship from Project to the new Task.
        project.tasks.connect(new_task)

        return new_task

    def get_task_by_uid(self, uid: str) -> Optional[GraphTask]:
        """
        Retrieves a Task node by its unique ID.
        """
        try:
            return GraphTask.nodes.get(uid=uid)
        except GraphTask.DoesNotExist:
            return None

    def list_tasks_for_project(self, project_id: str, skip: int = 0, limit: int = 100) -> List[GraphTask]:
        """
        Lists all tasks that belong to a specific project.
        """
        try:
            project = GraphProject.nodes.get(uid=project_id)
            # The relationship from Project to Task is 'tasks'
            tasks = project.tasks.all()
            return tasks[skip:skip+limit]
        except GraphProject.DoesNotExist:
            return []

    def update_task(self, uid: str, task_data: TaskUpdate) -> Optional[GraphTask]:
        """
        Updates an existing task.
        """
        task = self.get_task_by_uid(uid)
        if not task:
            return None

        # Use exclude_unset=True to only update fields that were provided.
        update_data = task_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(task, key, value)
        
        task.save()
        return task

    def delete_task(self, uid: str) -> bool:
        """
        Deletes a task by its unique ID.
        """
        task = self.get_task_by_uid(uid)
        if not task:
            return False
        
        task.delete()
        return True
