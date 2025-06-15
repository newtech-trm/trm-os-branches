# Core Relationships for TRM-OS MVP

This document defines the core relationships (edges) between the entities for the TRM-OS MVP. These relationships are fundamental to how the knowledge graph is structured in Neo4j and represent the verbs connecting the nouns (entities).

> **Lưu ý về naming convention**: Để đảm bảo sự nhất quán với tài liệu gốc Ontology V3.2, tài liệu này sử dụng quy ước đặt tên `camelCase` cho tất cả các thuộc tính và mối quan hệ.
> 
> **Về sự đơn giản hóa**: Các mối quan hệ trong tài liệu MVP này là phiên bản đơn giản hóa từ tài liệu gốc Ontology V3.2 (ONTOLOGY NỘI BỘ TRM - BẢN THIẾT KẾ THỐNG NHẤT HOÀN CHỈNH V3.2). Các thuộc tính phức tạp sẽ được bổ sung trong các phiên bản sau.

---

## 1. `(Task)-[:RESOLVES]->(Tension)`

- **Description:** This is a primary action-oriented relationship. It signifies that a specific `Task` is created with the intention of resolving a `Tension`.
- **Direction:** `Task` -> `Tension`
- **Source Node:** `Task`
- **Target Node:** `Tension`
- **Properties (Optional for MVP):**
  - `effectivenessScore` (Float): A score indicating how effectively the task resolved the tension, can be added later. [Thay thế cho `effectiveness_score`]

---

## 2. `(Agent)-[:PERFORMS]->(Task)`

- **Description:** Indicates that an `Agent` (AI or human) is assigned to or has executed a `Task`.
- **Direction:** `Agent` -> `Task`
- **Source Node:** `Agent`
- **Target Node:** `Task`
- **Properties:**
  - `assignedAt` (Datetime): When the task was assigned. [Thay thế cho `assigned_at`]
  - `status` (String): The agent's status regarding the task (e.g., `assigned`, `working`, `completed`). [Đã chuyển về camelCase]

---

## 3. `(Task)-[:PART_OF]->(Project)`

- **Description:** Connects a `Task` to a larger `Project`, providing hierarchical context.
- **Direction:** `Task` -> `Project`
- **Source Node:** `Task`
- **Target Node:** `Project`

---

## 4. `(Tension)-[:AFFECTS]->(Project)`

- **Description:** Shows that a `Tension` has an impact on a specific `Project`.
- **Direction:** `Tension` -> `Project`
- **Source Node:** `Tension`
- **Target Node:** `Project`

---

## 5. `(Agent)-[:ACTOR_TRIGGERED_EVENT]->(Event)`

- **Description:** Signifies that an `Agent` has performed an action that resulted in a noteworthy `Event` being created.
- **Direction:** `Agent` -> `Event`
- **Source Node:** `Agent`
- **Target Node:** `Event`
- **Hiện trạng:** Đã triển khai thành công trong Event API, quan hệ được xây dựng qua trường triggered_by_actor của EventGraphModel. Seed event tạo relationship này thành công.

---

## 6. `(Event)-[:EVENT_CONTEXT]->(Entity)`

- **Description:** Quan hệ liên kết từ một `Event` đến entity chính mà sự kiện liên quan đến. Cho phép tạo event log linh hoạt và có thể kiểm tra.
- **Direction:** `Event` -> `Entity` 
- **Source Node:** `Event`
- **Target Node:** Có thể là `Agent`, `Project`, `Task`, `Resource` hoặc entity khác.
- **Hiện trạng:**
  - Đã refactor thành các relationship riêng biệt cho từng loại entity: `primary_context_agent`, `primary_context_project`, `primary_context_task`, `primary_context_resource`.
  - Đã fix lỗi __label__ bằng cách không sử dụng BaseNode trừu tượng mà kết nối trực tiếp đến các entity cụ thể.
  - Sử dụng trường context_node_label trong API payload để xác định loại entity khi tạo relationship.
  - Seed event tạo relationship này thành công.
- **Example Usage:**
  - Event "TASK_COMPLETED" có relationship `primary_context_task` trỏ đến Task node cụ thể đã hoàn thành.
