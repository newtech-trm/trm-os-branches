# Current Tools Audit & MVP Integration Plan

This document audits the current software and tools in use at TRM and defines the integration strategy for the MVP. The goal is to meet users where they are and integrate TRM-OS into existing workflows seamlessly.

> **Lưu ý về naming convention**: Để đảm bảo sự nhất quán với tài liệu gốc Ontology V3.2, tài liệu này sử dụng quy ước đặt tên `camelCase` cho tất cả các thuộc tính, trạng thái và sự kiện.

---

## Integration Priority Levels

- **High:** Essential for the core functionality of the MVP. The system's value is significantly diminished without this.
- **Medium:** Important, provides significant value, but can be added in a fast-follow release after the initial MVP.
- **Low:** Nice to have, but not critical for the initial launch. Scheduled for future development.

---

## Tool Integration Breakdown

| Tool | Primary Use Case | MVP Integration Goal | Priority |
| :--- | :--- | :--- | :--- |
| **Gmail** | Primary channel for external & internal communication. Source of many `Tensions`. | **Read emails from a specific label (e.g., "TRM-OS/Tensions").** The `DataSensingAgent` will parse these emails to automatically create `Tension` nodes in the graph. | **High** |
| **Slack / MS Teams** | Real-time internal communication and notifications. | **Send notifications to a specific channel.** The system will push alerts for critical events, such as `tensionCreated` or `taskAssigned` (human review step). | **Medium** |
| **Google Sheets** | Ad-hoc data tracking, simple project plans, reports. | **Read data from a designated Google Sheet.** This could be used for bulk-importing `Projects` or `Tasks` that have already been planned. | **Medium** |
| **CRM (e.g., HubSpot)** | Managing customer relationships, sales pipeline, and support tickets. | **(Out of Scope for MVP)** In the future, the system will read data from the CRM to enrich `Tensions` with customer context. For the MVP, we will focus on the core internal loop first. | **Low** |
| **Calendar (Google/Outlook)** | Scheduling meetings and deadlines. | **(Out of Scope for MVP)** Future integration could involve creating calendar events for `Task` due dates or scheduling meetings to resolve `Tensions`. | **Low** |
