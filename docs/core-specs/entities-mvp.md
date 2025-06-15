# Core Entities for TRM-OS MVP

This document defines the core data entities for the TRM-OS Minimum Viable Product (MVP). These definitions serve as the blueprint for the database schema (Neo4j) and the core models in the application (`src/core/models.py`).

> **Lưu ý về naming convention**: Để đảm bảo sự nhất quán với tài liệu gốc Ontology V3.2, tài liệu này sử dụng quy ước đặt tên `camelCase` cho tất cả các thuộc tính, đúng như định nghĩa trong Ontology V3.2.

---

---

## 1. Tension

Represents a point of friction, a problem, a risk, or an unmet need within the organization. It's the fundamental unit that triggers action.

- **Node Label:** `Tension`
- **Key Properties:**
  - `tensionId` (String, UUID): Unique identifier. **(Primary Key)** [Thay thế cho `id`]
  - `title` (String): A concise summary of the tension.
  - `description` (String): Detailed explanation of the tension, its context, and impact. [Ontology V3.2: định dạng markdown]
  - `status` (String): Current state of the tension (e.g., `Open`, `InProgress`, `Resolved`, `Closed`). [Thay đổi từ UPPER_SNAKE_CASE sang camelCase]
  - `priority` (Integer): The urgency or importance level (e.g., 0-normal, 1-high, 2-critical). [Ontology V3.2: không giới hạn thang đo 1-5]
  - `source` (String): Where the tension was identified (e.g., `FounderInput`, `CustomerFeedback`, `DataSensingAgent`).
  - `sourceRef` (String, Optional): A reference to the original item, like an email ID or URL. [Thay thế cho `source_ref`]
  - `creationDate` (Datetime): Timestamp of creation. [Thay thế cho `created_at`]
  - `lastModifiedDate` (Datetime): Timestamp of the last update. [Thay thế cho `updated_at`]
  - `resolutionDate` (Datetime, Optional): Timestamp when the tension was resolved. [Thay thế cho `resolved_at`]

> **Thuộc tính mở rộng trong tương lai:** `tensionType`, `currentState`, `desiredState`, `impactAssessment`, `reporterAgentId`, `ownerAgentId`, `relatedProjectIds`, `relatedKnowledgeSnippetIds`, `tags` (xem Ontology V3.2 cho chi tiết đầy đủ)

---

---

## 2. Task

Represents a specific, actionable unit of work designed to address a `Tension` or contribute to a `Project`.

- **Node Label:** `Task`
- **Key Properties:**
  - `taskId` (String, UUID): Unique identifier. **(Primary Key)** [Thay thế cho `id`]
  - `name` (String): Clear and specific description of the task. [Thay thế cho `title` theo Ontology V3.2]
  - `status` (String): Current state (e.g., `ToDo`, `InProgress`, `Done`, `Blocked`). [Thay đổi sang camelCase]
  - `priority` (Integer): Task priority (e.g., 0-normal, 1-high, 2-urgent). [Ontology V3.2: không giới hạn thang đo 1-5]
  - `dueDate` (Date, Optional): The target completion date. [Thay thế cho `due_date`]
  - `creationDate` (Datetime): Timestamp of creation. [Thay thế cho `created_at`]
  - `lastModifiedDate` (Datetime): Timestamp of the last update. [Thay thế cho `updated_at`]
  - `actualCompletionDate` (Datetime, Optional): Timestamp of completion. [Thay thế cho `completed_at`]

> **Thuộc tính mở rộng trong tương lai:** `description` (markdown), `taskType`, `assigneeAgentId`, `reporterAgentId`, `projectId`, `startDate`, `effortEstimate`, `effortUnit`, `dependencies`, `subTasks`, `tags` (xem Ontology V3.2 cho chi tiết đầy đủ)

---

---

## 3. Project

A larger initiative or goal that may encompass multiple `Tensions` and `Tasks`. It provides a higher-level context for work being done.

- **Node Label:** `Project`
- **Key Properties:**
  - `projectId` (String, UUID): Unique identifier. **(Primary Key)** [Thay thế cho `id`]
  - `name` (String): The name of the project.
  - `description` (String): A brief overview of the project's goals.
  - `status` (String): Current state (e.g., `Planning`, `Active`, `Completed`, `OnHold`). [Thay đổi sang camelCase]
  - `plannedStartDate` (Date, Optional): Project start date. [Thay thế cho `start_date`]
  - `plannedEndDate` (Date, Optional): Project end date. [Thay thế cho `end_date`]
  - `creationDate` (Datetime): Timestamp of creation. [Thay thế cho `created_at`]
  - `lastModifiedDate` (Datetime): Timestamp of the last update. [Thay thế cho `updated_at`]

> **Thuộc tính mở rộng trong tương lai:** `goal`, `scope` (markdown), `priority`, `actualStartDate`, `actualEndDate`, `budget`, `budgetCurrency`, `actualCost`, `progressPercentage`, `ownerAgentId`, `stakeholderAgentIds`, `relatedTensionIds`, `tags` (xem Ontology V3.2 cho chi tiết đầy đủ)

---

---

## 4. Agent

Represents an autonomous entity (AI or human-in-the-loop) that performs actions within the system. For the MVP, this will primarily be AI agents.

- **Node Label:** `Agent`
- **Key Properties:**
  - `agentId` (String, UUID): Unique identifier. **(Primary Key)** [Thay thế cho `id`]
  - `name` (String): A unique name for the agent (e.g., `TensionResolutionAgent`, `DataSensingAgent`).
  - `agentType` (String): The category of the agent (e.g., `AIAgent`, `InternalAgent`, `ExternalAgent`, `AGE`). [Thay thế cho `type`, mở rộng các loại]
  - `description` (String): What the agent is responsible for.
  - `status` (String): Operational status (e.g., `Active`, `Inactive`, `PendingApproval`, `Disabled`). [Thay đổi sang camelCase và mở rộng]
  - `creationDate` (Datetime): Timestamp of creation. [Thay thế cho `created_at`]

> **Thuộc tính mở rộng trong tương lai:** `lastModifiedDate`, `contactInfo` (object), `capabilities` (list), và các thuộc tính theo từng subtype (`InternalAgent`, `ExternalAgent`, `AIAgent`, `AGE`) - xem Ontology V3.2 cho chi tiết đầy đủ

---

---

## 5. Event

A record of a significant occurrence within the system. Events are immutable and form the basis of the "Recognition → Event → WIN" philosophy. Event API đã được triển khai thành công và dữ liệu Event có thể được seed và lưu vào Neo4j.

- **Node Label:** `Event`
- **Key Properties:** *(đã triển khai đúng theo mô hình Neo4j)*
  - `uid` (String, UUID): Unique identifier. **(Primary Key)**
  - `name` (String): The type of event (e.g., `USER_LOGIN`, `PROJECT_STATUS_UPDATED`, `TASK_ASSIGNED`).
  - `description` (String): A human-readable description of the event.
  - `payload` (JSONProperty): A flexible JSON object containing event-specific data.
  - `tags` (ArrayProperty): Tags for categorizing or filtering events.
  - `created_at` (DateTimeProperty): Timestamp của thời điểm tạo event (ISO format string).
  - `updated_at` (DateTimeProperty): Timestamp của lần cập nhật cuối (ISO format string).

- **Key Relationships:** *(đã triển khai đầy đủ)*
  - `triggered_by_actor` (RelationshipFrom): Từ Agent đến Event (ACTOR_TRIGGERED_EVENT)
  - `primary_context_agent` (RelationshipTo): Từ Event đến Agent (EVENT_CONTEXT)
  - `primary_context_project` (RelationshipTo): Từ Event đến Project (EVENT_CONTEXT)
  - `primary_context_task` (RelationshipTo): Từ Event đến Task (EVENT_CONTEXT)
  - `primary_context_resource` (RelationshipTo): Từ Event đến Resource (EVENT_CONTEXT)
  - `generated_by_projects` (RelationshipFrom): Từ Project đến Event (GENERATES_EVENT)
  - `generated_by_tasks` (RelationshipFrom): Từ Task đến Event (GENERATES_EVENT)
  - `generated_by_agents` (RelationshipFrom): Từ Agent đến Event (GENERATES_EVENT)
  - `generated_by_recognitions` (RelationshipFrom): Từ Recognition đến Event (GENERATES_EVENT)
  - `generated_by_wins` (RelationshipFrom): Từ WIN đến Event (GENERATES_EVENT)

> **Cập nhật hiện trạng:** Event API đã triển khai thành công endpoint CRUD (/api/v1/events/) và serialize đúng datetime thành ISO format string. Relationships được tổ chức riêng biệt cho từng entity type (không còn lỗi __label__). API sử dụng context_node_label để phân biệt loại entity khi tạo relationship.
