# Philosophy in Code: Implementing the TRM-OS Vision

This document provides a concise guide for developers on how the core philosophy of TRM-OS, particularly "Recognition → Event → WIN", is translated into the actual data structures and code architecture.

> **Lưu ý về naming convention**: Để đảm bảo sự nhất quán với tài liệu gốc Ontology V3.2, tài liệu này sử dụng quy ước đặt tên `camelCase` cho tất cả các thuộc tính, trạng thái và hành động trong code.

---

## The Core Loop: Recognition → Event → WIN

This is the fundamental operational loop of the system. It's not just a concept; it's the blueprint for our data flow and agent behavior.

1. **Recognition (Sự công nhận / Ghi nhận):**
   - **What it is:** The system's ability to identify a significant occurrence. This isn't just about finding problems (`Tensions`), but also about acknowledging progress (`Tasks` being completed).
   - **How it's coded:** This is the primary function of our **Agents**. For example, the `DataSensingAgent` *recognizes* a potential `Tension` in an email. The `TensionResolutionAgent` *recognizes* that a `Tension` needs a `Task`.

2. **Event (Sự kiện):**
   - **What it is:** The immutable, factual record of a recognition. It's the "single source of truth" for what has happened in the system.
   - **How it's coded:** This maps directly to the **`Event` entity**. Every significant action an agent takes results in the creation of an `Event` node. The relationship `(Event)-[:RELATES_TO]->(Entity)` is crucial, as it provides a clear, auditable trail connecting the event to the specific `Tension`, `Task`, or `Project` it affects.

3. **WIN (Chiến thắng / Kết quả):**
   - **What it is:** The tangible, positive outcome resulting from the chain of events. It's the realization of value.
   - **How it's coded (for the MVP):** A "WIN" is not a separate entity *yet*. For the MVP, a WIN is represented by a **state change** in our core entities. The most important WIN is a `Tension` node's status changing from `open` to `resolved`. Đây là kết quả có thể đo lường được chứng minh hệ thống đã xử lý thành công một điểm bế tắc.

## Guiding Principles for Development

- **Everything is an Event:** If it's an important action or state change, it must be recorded as an `Event`. This creates transparency and an audit trail.
- **Agents Drive Action:** Agents are the actors. They *recognize* situations and *trigger* `Events`.
- **The Graph Tells the Story:** The structure of our Neo4j graph, with its nodes and relationships, should visually represent the "Recognition → Event → WIN" flow. One should be able to query the graph and trace the entire lifecycle of a tension from its creation to its resolution.
