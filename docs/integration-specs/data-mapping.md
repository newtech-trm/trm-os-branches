# Data Mapping for MVP Integrations

This document provides detailed specifications for mapping data from external sources into TRM-OS entities. For the MVP, the focus is solely on the high-priority integration: **Gmail to Tension**.

> **Lưu ý về naming convention**: Để đảm bảo sự nhất quán với tài liệu gốc Ontology V3.2, tài liệu này sử dụng quy ước đặt tên `camelCase` cho tất cả các thuộc tính, trạng thái và hành động.

---

## 1. Source: Gmail

- **Trigger:** An email is added to the label `TRM-OS/Tensions`.
- **Target Entity:** `Tension`
- **Responsible Agent:** `DataSensingAgent`

## 2. Field Mapping: Gmail Email → Tension Entity

| Source Field (Gmail) | Transformation Logic | Target Field (Tension) | Notes |
| :--- | :--- | :--- | :--- |
| **Email Subject** | Use directly as the title. | `title` | This provides a concise, recognizable summary. |
| **Email Body (Plain Text)** | Use the full plain-text body. | `description` | Contains the detailed context of the tension. HTML content should be stripped. |
| **Message-ID Header** | Extract the unique message ID. | `sourceRef` | This is a crucial, unique identifier to prevent duplicate processing and allow tracing back to the original email. |
| **(Constant Value)** | Set a constant string `'gmail'`. | `source` | Clearly indicates where this tension originated. |
| **(System Generated)** | Generate a new UUID. | `tensionId` | The internal primary key for the `Tension` node. |
| **(System Generated)** | Set to `open` upon creation. | `status` | All new tensions from email start as open. |
| **(System Generated)** | Set to `3` (Medium) as a default. | `priority` | Priority can be adjusted manually later. We might introduce logic to parse priority from the subject (e.g., `[P1]`) in the future. |
| **Date Header** | Parse the timestamp of the email. | `creationDate` | Represents when the tension was originally communicated, not when it was processed. |

## 3. Example Workflow

1. A user forwards an email to a specific address or applies the label `TRM-OS/Tensions` to an email in their inbox.
2. Google Cloud Pub/Sub (or a similar mechanism) sends a notification to a webhook endpoint monitored by the `DataSensingAgent`.
3. The `DataSensingAgent` uses the Gmail API to fetch the full content of the email identified in the notification.
4. It applies the mapping logic defined above to construct the properties for a new `Tension` object.
5. The agent creates the `Tension` node in Neo4j.
