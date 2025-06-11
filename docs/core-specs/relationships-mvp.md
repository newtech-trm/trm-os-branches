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

## 5. `(Agent)-[:TRIGGERS]->(Event)`

- **Description:** Signifies that an `Agent` has performed an action that resulted in a noteworthy `Event` being created.
- **Direction:** `Agent` -> `Event`
- **Source Node:** `Agent`
- **Target Node:** `Event`

---

## 6. `(Event)-[:RELATES_TO]->(Entity)`

- **Description:** A generic but powerful relationship linking an `Event` to the primary entity it concerns. This allows for a flexible and auditable event log.
- **Direction:** `Event` -> `Entity`
- **Source Node:** `Event`
- **Target Node:** Can be a `Tension`, `Task`, or `Project` node.
- **Example Usage:**
  - An `Event` of type `taskCompleted` would have a `RELATES_TO` relationship pointing to the specific `Task` node that was completed. [Đã chuyển về camelCase]
