from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
import uuid
from enum import Enum

# Define enumerations for constrained fields
class TaskType(str, Enum):
    FEATURE = "Feature"
    BUG = "Bug"
    CHORE = "Chore"
    RESEARCH = "Research"
    DOCUMENTATION = "Documentation"
    MEETING = "Meeting"

class TaskStatus(str, Enum):
    TODO = "ToDo"
    IN_PROGRESS = "InProgress"
    BLOCKED = "Blocked"
    IN_REVIEW = "InReview"
    DONE = "Done"
    CANCELLED = "Cancelled"
    BACKLOG = "Backlog"

class EffortUnit(str, Enum):
    HOURS = "hours"
    DAYS = "days"
    STORY_POINTS = "story_points"

# The base model for a Task, containing shared fields.
class TaskBase(BaseModel):
    name: str = Field(..., min_length=5, max_length=150, description="Tên hoặc tiêu đề ngắn gọn của công việc.")
    description: Optional[str] = Field(None, description="Mô tả chi tiết về công việc, bao gồm yêu cầu, mục tiêu, tiêu chí hoàn thành.")
    
    # Task type & status
    task_type: Optional[TaskType] = Field(None, description="Phân loại công việc, giúp lọc và báo cáo.")
    status: TaskStatus = Field(TaskStatus.TODO, description="Trạng thái hiện tại của công việc trong quy trình.")
    
    # Priority & effort
    priority: int = Field(0, ge=0, le=2, description="Mức độ ưu tiên của công việc (0-Normal, 1-High, 2-Urgent).")
    effort_estimate: Optional[int] = Field(None, ge=0, description="Ước tính công sức hoặc thời gian cần thiết để hoàn thành công việc.")
    effort_unit: EffortUnit = Field(EffortUnit.HOURS, description="Đơn vị của effort_estimate.")
    
    # Assignment & reporting
    assignee_agent_id: Optional[str] = Field(None, description="ID của Agent được giao thực hiện công việc này.")
    reporter_agent_id: Optional[str] = Field(None, description="ID của Agent đã tạo hoặc báo cáo công việc này.")
    
    # Dates
    start_date: Optional[datetime] = Field(None, description="Ngày bắt đầu dự kiến hoặc thực tế của công việc.")
    due_date: Optional[datetime] = Field(None, description="Hạn chót (deadline) cần hoàn thành công việc.")
    actual_completion_date: Optional[datetime] = Field(None, description="Ngày công việc thực sự được hoàn thành.")
    
    # Categorization
    tags: Optional[List[str]] = Field(None, description="Các từ khóa hoặc nhãn để phân loại, tìm kiếm công việc.")
    
    # Dependencies (these can be stored as direct properties or handled through relationships)
    dependencies: Optional[List[str]] = Field(None, description="Danh sách các taskId khác mà công việc này phụ thuộc vào.")
    sub_tasks: Optional[List[str]] = Field(None, description="Danh sách các taskId con của công việc này.")

    # Configuration for Pydantic model.
    # from_attributes=True allows the model to be created from ORM objects.
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "Thiết kế API cho Task entity theo Ontology V3.2",
                "description": "Cập nhật API endpoints để hỗ trợ đầy đủ các thuộc tính Task theo Ontology V3.2, bao gồm taskType, priority, effortEstimate, etc.",
                "task_type": "Feature",
                "status": "ToDo",
                "priority": 1,
                "effort_estimate": 8,
                "effort_unit": "hours",
                "tags": ["api", "task", "ontology-v3.2"],
                "due_date": "2025-06-20T18:00:00Z"
            }
        }
    )

# Pydantic model for creating a new Task.
# It requires a project_id to link the task to a project.
class TaskCreate(TaskBase):
    project_id: str = Field(..., description="The ID of the project this task belongs to.")

# Pydantic model for updating an existing Task.
# All fields are optional.
class TaskUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=5, max_length=150)
    description: Optional[str] = Field(None)
    task_type: Optional[TaskType] = Field(None)
    status: Optional[TaskStatus] = Field(None)
    priority: Optional[int] = Field(None, ge=0, le=2)
    effort_estimate: Optional[int] = Field(None, ge=0)
    effort_unit: Optional[EffortUnit] = Field(None)
    assignee_agent_id: Optional[str] = Field(None)
    reporter_agent_id: Optional[str] = Field(None)
    start_date: Optional[datetime] = Field(None)
    due_date: Optional[datetime] = Field(None)
    actual_completion_date: Optional[datetime] = Field(None)
    tags: Optional[List[str]] = Field(None)
    dependencies: Optional[List[str]] = Field(None)
    sub_tasks: Optional[List[str]] = Field(None)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Cập nhật API endpoints Task",
                "status": "InProgress",
                "priority": 2,
                "assignee_agent_id": "agent_123",
                "tags": ["urgent", "api"]
            }
        }
    )

# This class represents the data structure of a Task as stored in the database.
# It inherits from TaskBase and adds system-generated fields like uid, created_at, updated_at.
class TaskInDB(TaskBase):
    # Align these fields with the BaseNode graph_model
    uid: str
    created_at: datetime
    updated_at: datetime

# This is the model that will be returned to the client in API responses.
# It inherits all fields from TaskInDB.
class Task(TaskInDB):
    # We can add any additional derived or computed fields here
    pass
    pass
