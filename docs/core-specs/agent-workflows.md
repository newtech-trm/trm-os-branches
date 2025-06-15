# Core Agent Workflows (MVP)

This document details the core workflows that agents follow in the MVP version of TRM-OS. These workflows represent the most common interaction patterns and business processes within the system.

> **Lưu ý về naming convention**: Để đảm bảo sự nhất quán với tài liệu gốc Ontology V3.2, tài liệu này sử dụng quy ước đặt tên `camelCase` cho tất cả các thuộc tính, trạng thái và mối quan hệ.

---

## 1. Tension Ingestion and Creation Workflow

**Goal:** To identify and create a `tension` from an external data source.

- **Trigger:** New data arrives from an external source (e.g., a specific Gmail label, a webhook call).
- **Responsible Agent:** `dataSensingAgent` (or a similarly named agent).
- **Steps:**
    1.  **Receive Data:** The agent ingests the raw data (e.g., email content).
    2.  **Analyze Content:** It performs a basic analysis (e.g., using keywords, sentiment analysis, or a simple LLM prompt) to determine if the data represents a potential tension.
    3.  **Create Tension:** If a tension is identified, the agent creates a new `tension` node with `status: 'open'`.
    4.  **Create Event:** The agent creates a `tensionCreated` `event` node.
    5.  **Link Entities:** It establishes the necessary relationships: `(agent)-[:triggers]->(event)` and `(event)-[:affects]->(tension)`.

---

## 2. Task Suggestion Workflow

**Goal:** To propose actionable `tasks` to resolve an open `tension`.

- **Trigger:** A new `tension` is created with `status: 'open'`.
- **Responsible Agent:** `tensionResolutionAgent`.
- **Steps:**
    1.  **Detect New Tension:** The agent is notified of or polls for new, open tensions.
    2.  **Analyze Tension:** It analyzes the `tension`'s title and description to understand the core problem.
    3.  **Propose Tasks:** The agent generates one or more `task` descriptions that would help resolve the tension.
    4.  **Create Tasks:** For each proposal, it creates a new `task` node with `status: 'todo'`.
    5.  **Link Entities:** It establishes the `(task)-[:resolves]->(tension)` relationship for each new task.
    6.  **(Future Step):** Notify a human user for review and assignment of the newly created tasks.

---

## 3. Task Completion and Event Generation Workflow

**Goal:** To ghi nhận hoàn thành task và tạo event phù hợp trong hệ thống.

- **Trigger:** Trạng thái của `task` được cập nhật thành `'done'`.
- **Responsible Agent:** Agent thực hiện task, hoặc một `systemAgent` chuyên giám sát thay đổi trạng thái.
- **Steps:**
    1. **Detect Task Completion:** Agent phát hiện thay đổi trạng thái task.
    2. **Create Event:** Agent tạo node `event` với name là `TASK_COMPLETED`.
    3. **Link Entities:** Thiết lập các relationship:
       - `(agent)-[:ACTOR_TRIGGERED_EVENT]->(event)` 
       - `(event)-[:EVENT_CONTEXT]->(task)`
    4. **Update Related Entities:** Cập nhật trạng thái của các entity liên quan.

**Hiện trạng (2025-06-15):**
- Event API đã hoàn thiện và có thể xử lý việc tạo event cho task completed
- Relationship ACTOR_TRIGGERED_EVENT và EVENT_CONTEXT đã được triển khai
- Seed script đã test thành công việc tạo event và liên kết với các entity
- Cần phát triển service layer để tự động hóa quy trình này khi task được cập nhật
