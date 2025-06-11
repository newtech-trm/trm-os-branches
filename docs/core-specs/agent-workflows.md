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

## 3. Task Completion and Recognition Workflow

**Goal:** To recognize the completion of a task and trigger subsequent actions.

- **Trigger:** A `task`'s status is updated to `'done'`.
- **Responsible Agent:** The agent that performed the task, or a generic `systemAgent` monitoring status changes.
- **Steps:**
    1.  **Detect Task Completion:** The agent detects the status change.
    2.  **Create Event:** It creates a `taskCompleted` `event` node.
    3.  **Link Entities:** It establishes the `(agent)-[:triggers]->(event)` and `(event)-[:affects]->(task)` relationships.
    4.  **Update Tension Status (Chain Reaction):** This `taskCompleted` event can trigger another workflow (potentially by the `tensionResolutionAgent`) to check if all tasks for a given `tension` are complete. If so, the agent can update the `tension`'s status to `resolved`.
