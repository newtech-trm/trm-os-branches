"""
Pydantic models for all Relationship Types in the TRM Ontology.

This file defines the structure and attributes of the edges in our knowledge graph.
Each class represents a specific type of relationship, capturing not just the connection
but also the rich context and properties of that connection, turning simple edges into
first-class citizens of the ontology.

Based on: ONTOLOGY NỘI BỘ TRM - BẢN THIẾT KẾ THỐNG NHẤT HOÀN CHỈNH V3.2.md
"""

from pydantic import BaseModel, Field, constr
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime
import uuid

# --- Base Models for Relationships ---

class Relationship(BaseModel):
    """Base model for all relationship types, providing common audit fields."""
    relationshipId: str = Field(default_factory=lambda: f"rel_{uuid.uuid4()}", description="Mã định danh duy nhất cho bản ghi mối quan hệ này.")
    creationDate: datetime = Field(default_factory=datetime.utcnow, description="Ngày mối quan hệ này được tạo.")
    lastModifiedDate: datetime = Field(default_factory=datetime.utcnow, description="Ngày mối quan hệ này được cập nhật lần cuối.")
    notes: Optional[str] = Field(None, description="Ghi chú bổ sung về mối quan hệ.")

# --- Relationship Type Enums ---

class ActionTypeEnum(str, Enum):
    CREATED = "Created"
    UPDATED = "Updated"
    DELETED = "Deleted"
    COMPLETED = "Completed"
    STARTED = "Started"
    PAUSED = "Paused"
    RESUMED = "Resumed"
    ASSIGNED = "Assigned"
    UNASSIGNED = "Unassigned"
    COMMENTED = "Commented"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    VIEWED = "Viewed"
    ACKNOWLEDGED = "Acknowledged"
    RESOLVED = "Resolved"
    REOPENED = "Reopened"
    ESCALATED = "Escalated"
    DELEGATED = "Delegated"
    SUBMITTED = "Submitted"
    REVIEWED = "Reviewed"
    NOTIFIED = "Notified"
    LOGGED_IN = "LoggedIn"
    LOGGED_OUT = "LoggedOut"
    SYSTEM_GENERATED = "SystemGenerated"
    CUSTOM_ACTION = "CustomAction"
    LINKED = "Linked"
    UNLINKED = "Unlinked"
    ARCHIVED = "Archived"
    RESTORED = "Restored"
    PUBLISHED = "Published"
    UNPUBLISHED = "Unpublished"
    FOLLOWED = "Followed"
    UNFOLLOWED = "Unfollowed"
    RATED = "Rated"
    FLAGGED = "Flagged"

class TargetEntityTypeEnum(str, Enum):
    EVENT = "Event"
    TASK = "Task"
    PROJECT = "Project"
    TENSION = "Tension"
    KNOWLEDGE_SNIPPET = "KnowledgeSnippet"
    WIN = "WIN"
    RECOGNITION = "Recognition"
    RESOURCE = "Resource"
    COMMENT = "Comment"
    DOCUMENT = "Document"
    USER_ACCOUNT = "UserAccount"
    SYSTEM_LOG = "SystemLog"
    TEAM = "Team"
    GOAL = "Goal"
    OBJECTIVE = "Objective"
    KEY_RESULT = "KeyResult"
    AGENT = "Agent"
    TOOL = "Tool"
    SKILL = "Skill"
    OTHER = "Other"

class ProficiencyLevelEnum(str, Enum):
    NOVICE_1 = "Novice_1"
    BEGINNER_2 = "Beginner_2"
    INTERMEDIATE_3 = "Intermediate_3"
    ADVANCED_4 = "Advanced_4"
    EXPERT_5 = "Expert_5"
    MASTER_6 = "Master_6"

class VerificationStatusEnum(str, Enum):
    UNVERIFIED = "Unverified"
    SELF_ASSESSED = "SelfAssessed"
    PEER_VERIFIED = "PeerVerified"
    MANAGER_VERIFIED = "ManagerVerified"
    CERTIFIED = "Certified"
    ASSESSMENT_PENDING = "AssessmentPending"

class TeamRoleEnum(str, Enum):
    LEADER = "Leader"
    MEMBER = "Member"
    CONTRIBUTOR = "Contributor"
    STAKEHOLDER = "Stakeholder"
    OBSERVER = "Observer"
    ADMINISTRATOR = "Administrator"
    GUEST = "Guest"

# --- Specific Relationship Models ---

class PerformedAction(Relationship):
    """Model for the PERFORMED_ACTION relationship (7.1)"""
    agentId: str = Field(..., description="ID của Agent thực hiện hành động.")
    targetEntityId: str = Field(..., description="ID của thực thể là đối tượng của hành động.")
    targetEntityType: TargetEntityTypeEnum = Field(..., description="Loại thực thể của targetEntityId.")
    actionType: ActionTypeEnum = Field(..., description="Loại hành động cụ thể được thực hiện.")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Thời điểm chính xác hành động được thực hiện.")
    roleInAction: Optional[str] = Field(None, description="Vai trò của agent trong hành động, ví dụ: 'Creator', 'Assignee', 'Reviewer'.")
    details: Optional[str] = Field(None, description="Mô tả chi tiết hoặc ghi chú bổ sung về hành động.")
    sourceApplication: str = Field("TRM-OS Core", description="Ứng dụng hoặc module nguồn đã ghi nhận hành động này.")
    durationMs: Optional[int] = Field(None, ge=0, description="Thời gian thực hiện hành động, tính bằng mili giây.")
    contextSessionId: Optional[str] = Field(None, description="ID của phiên làm việc hoặc ngữ cảnh rộng hơn.")

class HasSkill(Relationship):
    """Model for the HAS_SKILL relationship (7.2)"""
    agentId: str = Field(..., description="ID của Agent sở hữu kỹ năng.")
    skillId: str = Field(..., description="ID của Skill được sở hữu.")
    proficiencyLevel: ProficiencyLevelEnum = Field(..., description="Mức độ thành thạo của Agent đối với Skill này.")
    verificationStatus: VerificationStatusEnum = Field(VerificationStatusEnum.UNVERIFIED, description="Trạng thái xác minh kỹ năng của Agent.")
    verificationDate: Optional[datetime] = Field(None, description="Ngày kỹ năng được xác minh.")
    verifiedByAgentId: Optional[str] = Field(None, description="ID của Agent đã xác minh kỹ năng.")
    experienceInYears: Optional[float] = Field(None, ge=0, description="Số năm kinh nghiệm của Agent với kỹ năng này.")
    lastUsedDate: Optional[datetime] = Field(None, description="Ngày Agent sử dụng kỹ năng này lần cuối.")

class RequiresSkill(Relationship):
    """Model for the REQUIRES_SKILL relationship (7.3)"""
    requesterEntityId: str = Field(..., description="ID của Project hoặc Task yêu cầu kỹ năng.")
    requesterEntityType: constr(regex='^(Project|Task)$') = Field(..., description="Loại của thực thể yêu cầu (Project hoặc Task).")
    skillId: str = Field(..., description="ID của Skill được yêu cầu.")
    minimumProficiencyLevel: ProficiencyLevelEnum = Field(..., description="Mức độ thành thạo tối thiểu được yêu cầu.")
    importance: str = Field("Medium", description="Mức độ quan trọng của kỹ năng đối với sự thành công của Project/Task.", pattern='^(Critical|High|Medium|Low)$')
    isMandatory: bool = Field(True, description="Kỹ năng này có bắt buộc hay không.")

class IsMemberOf(Relationship):
    """Model for the IS_MEMBER_OF relationship (7.4)"""
    agentId: str = Field(..., description="ID của Agent là thành viên.")
    teamId: str = Field(..., description="ID của Team mà Agent thuộc về.")
    role: TeamRoleEnum = Field(TeamRoleEnum.MEMBER, description="Vai trò của Agent trong Team.")
    isActive: bool = Field(True, description="Mối quan hệ thành viên này có đang hoạt động hay không.")
    startDate: datetime = Field(default_factory=datetime.utcnow, description="Ngày Agent bắt đầu tham gia Team.")
    endDate: Optional[datetime] = Field(None, description="Ngày Agent kết thúc vai trò trong Team.")

class HasSubtask(Relationship):
    """Model for the HAS_SUBTASK relationship (7.5)"""
    parentTaskId: str = Field(..., description="ID của Task cha.")
    childTaskId: str = Field(..., description="ID của Task con.")
    dependencyType: str = Field("Finish-to-Start", description="Loại phụ thuộc giữa Task cha và con.", pattern='^(Finish-to-Start|Start-to-Start|Finish-to-Finish|Start-to-Finish)$')
    lagDays: int = Field(0, description="Độ trễ (tính bằng ngày) giữa hai Task.")

class IsRelatedTo(Relationship):
    """Model for the IS_RELATED_TO relationship (7.6)"""
    sourceEntityId: str = Field(..., description="ID của thực thể nguồn.")
    sourceEntityType: TargetEntityTypeEnum = Field(..., description="Loại của thực thể nguồn.")
    targetEntityId: str = Field(..., description="ID của thực thể đích.")
    targetEntityType: TargetEntityTypeEnum = Field(..., description="Loại của thực thể đích.")
    relationshipType: str = Field(..., description="Mô tả bản chất của mối quan hệ, ví dụ: 'Duplicates', 'Blocks', 'Depends on', 'Is part of'.")
    description: Optional[str] = Field(None, description="Mô tả chi tiết hơn về mối quan hệ.")

class Generated(Relationship):
    """Model for the GENERATED relationship (7.7)"""
    sourceEntityId: str = Field(..., description="ID của thực thể nguồn (ví dụ: Task, Project).")
    sourceEntityType: constr(regex='^(Task|Project|Event)$') = Field(..., description="Loại của thực thể nguồn.")
    generatedEntityId: str = Field(..., description="ID của thực thể được tạo ra (ví dụ: Tension, WIN, Recognition).")
    generatedEntityType: constr(regex='^(Tension|WIN|Recognition|Event)$') = Field(..., description="Loại của thực thể được tạo ra.")
    generationContext: Optional[str] = Field(None, description="Ngữ cảnh hoặc lý do của việc tạo ra.")

class Consumed(Relationship):
    """Model for the CONSUMED relationship (7.8)"""
    consumerEntityId: str = Field(..., description="ID của thực thể tiêu thụ (ví dụ: Agent, Task).")
    consumerEntityType: constr(regex='^(Agent|Task)$') = Field(..., description="Loại của thực thể tiêu thụ.")
    consumedEntityId: str = Field(..., description="ID của thực thể bị tiêu thụ (ví dụ: Event).")
    consumedEntityType: constr(regex='^(Event)$') = Field(..., description="Loại của thực thể bị tiêu thụ.")
    consumptionTimestamp: datetime = Field(default_factory=datetime.utcnow, description="Thời điểm tiêu thụ.")

class Triggered(Relationship):
    """Model for the TRIGGERED relationship (7.9)"""
    sourceEventId: str = Field(..., description="ID của Event gây ra trigger.")
    triggeredEntityId: str = Field(..., description="ID của thực thể bị trigger (ví dụ: Agent, Task).")
    triggeredEntityType: constr(regex='^(Agent|Task|Project)$') = Field(..., description="Loại của thực thể bị trigger.")
    triggerMechanism: str = Field("Automatic", description="Cơ chế trigger (ví dụ: 'Automatic', 'Manual').")
    triggerCondition: Optional[str] = Field(None, description="Điều kiện cụ thể đã gây ra trigger.")

class HasTension(Relationship):
    """Model for the HAS_TENSION relationship (7.10)"""
    sourceEntityId: str = Field(..., description="ID của Project hoặc Task chứa Tension.")
    sourceEntityType: constr(regex='^(Project|Task)$') = Field(..., description="Loại của thực thể nguồn.")
    tensionId: str = Field(..., description="ID của Tension được chứa.")
    status: str = Field("Open", description="Trạng thái của Tension trong ngữ cảnh này.", pattern='^(Open|Resolved|Closed|Archived)$')

class LedToWin(Relationship):
    """Model for the LED_TO_WIN relationship (7.11)"""
    sourceEntityId: str = Field(..., description="ID của Task hoặc Project dẫn đến WIN.")
    sourceEntityType: constr(regex='^(Task|Project)$') = Field(..., description="Loại của thực thể nguồn.")
    winId: str = Field(..., description="ID của WIN được tạo ra.")
    contributionDescription: str = Field(..., description="Mô tả sự đóng góp cụ thể của Task/Project vào WIN.")
    contributionPercentage: Optional[float] = Field(None, ge=0, le=100, description="Tỷ lệ phần trăm đóng góp (nếu có thể đo lường).")

class AcknowledgedBy(Relationship):
    """Model for the ACKNOWLEDGED_BY relationship (7.12)"""
    winId: str = Field(..., description="ID của WIN được ghi nhận.")
    recognitionId: str = Field(..., description="ID của Recognition ghi nhận WIN đó.")
    acknowledgerId: str = Field(..., description="ID của UserAccount hoặc Agent thực hiện ghi nhận.")
    acknowledgerType: constr(regex='^(UserAccount|Agent)$') = Field(..., description="Loại của thực thể ghi nhận.")
    acknowledgementTimestamp: datetime = Field(default_factory=datetime.utcnow, description="Thời điểm ghi nhận.")

class HasKnowledge(Relationship):
    """Model for the HAS_KNOWLEDGE relationship (7.13)"""
    knowledgeHolderId: str = Field(..., description="ID của thực thể chứa tri thức (UserAccount, Team, Agent).")
    knowledgeHolderType: constr(regex='^(UserAccount|Team|Agent)$') = Field(..., description="Loại của thực thể chứa tri thức.")
    knowledgeSnippetId: str = Field(..., description="ID của KnowledgeSnippet được chứa.")
    sourceOfKnowledge: Optional[str] = Field(None, description="Nguồn gốc của tri thức này (ví dụ: 'Kinh nghiệm dự án X', 'Tài liệu Y').")

class UsesKnowledge(Relationship):
    """Model for the USES_KNOWLEDGE relationship (7.14)"""
    knowledgeUserId: str = Field(..., description="ID của thực thể sử dụng tri thức (Agent, Task, Project).")
    knowledgeUserType: constr(regex='^(Agent|Task|Project)$') = Field(..., description="Loại của thực thể sử dụng tri thức.")
    knowledgeSnippetId: str = Field(..., description="ID của KnowledgeSnippet được sử dụng.")
    usageContext: str = Field(..., description="Ngữ cảnh sử dụng tri thức (ví dụ: 'Để giải quyết task A', 'Để lên kế hoạch dự án B').")
    usageTimestamp: datetime = Field(default_factory=datetime.utcnow, description="Thời điểm tri thức được sử dụng.")
    feedback: Optional[str] = Field(None, description="Phản hồi về tính hữu ích của tri thức trong ngữ cảnh này.")

class RequiresResource(Relationship):
    """Model for the REQUIRES_RESOURCE relationship (7.15)"""
    requesterEntityId: str = Field(..., description="ID của thực thể yêu cầu tài nguyên (Task, Project).")
    requesterEntityType: constr(regex='^(Task|Project)$') = Field(..., description="Loại của thực thể yêu cầu.")
    resourceId: str = Field(..., description="ID của Resource được yêu cầu.")
    quantity: float = Field(..., description="Số lượng tài nguyên được yêu cầu.")
    unit: str = Field(..., description="Đơn vị tính của số lượng (ví dụ: 'hours', 'items', 'USD').")
    status: str = Field("Pending", description="Trạng thái của yêu cầu.", pattern='^(Pending|Approved|Rejected|Allocated|Consumed)$')

class HasComment(Relationship):
    """Model for the HAS_COMMENT relationship (7.16)"""
    targetEntityId: str = Field(..., description="ID của thực thể được bình luận.")
    targetEntityType: TargetEntityTypeEnum = Field(..., description="Loại của thực thể được bình luận.")
    commentId: str = Field(..., description="ID của Comment.")

class Mentions(Relationship):
    """Model for the MENTIONS relationship (7.17)"""
    sourceEntityId: str = Field(..., description="ID của thực thể chứa sự đề cập (Comment, Tension, Task).")
    sourceEntityType: constr(regex='^(Comment|Tension|Task|Project|WIN)$') = Field(..., description="Loại của thực thể nguồn.")
    mentionedEntityId: str = Field(..., description="ID của thực thể được đề cập (UserAccount, Team, Agent).")
    mentionedEntityType: constr(regex='^(UserAccount|Team|Agent)$') = Field(..., description="Loại của thực thể được đề cập.")
    context: Optional[str] = Field(None, description="Đoạn văn bản chứa sự đề cập.")


