# Finalized Technology Stack for TRM-OS MVP

This document outlines the definitive technology stack for building the TRM-OS MVP. These choices are based on the system's requirements for graph-based data, event-driven architecture, AI/ML capabilities, and rapid development.

---

| Component | Technology Choice | Justification |
| :--- | :--- | :--- |
| **Backend Framework** | **Python 3.11+ with FastAPI** | Python is the de facto language for AI/ML. FastAPI provides high performance, automatic API documentation (crucial for agent interaction), and an easy learning curve, enabling rapid development. |
| **Primary Database (Graph)** | **Neo4j (AuraDB)** | The entire TRM-OS model is based on entities and relationships, making a native graph database the perfect fit. Neo4j is mature, and AuraDB (cloud version) simplifies management and scaling. |
| **Vector Database** | **Supabase (PGVector)** | Chosen for its simplicity and cost-effectiveness. It provides a robust PostgreSQL instance with the PGVector extension, which is sufficient for the MVP's embedding storage and similarity search needs. It also offers other useful backend-as-a-service features. |
| **Event Messaging** | **RabbitMQ / Redis Pub/Sub** | An event bus is critical for the decoupled, event-driven architecture. RabbitMQ is a robust choice. For the MVP, Redis Pub/Sub could be a simpler, faster alternative to implement initially. The decision will be finalized at the start of the sprint based on deployment complexity. |
| **Agent & AI Logic** | **LangChain, OpenAI API** | LangChain provides a powerful framework for building applications with LLMs, simplifying prompt management, and chaining calls. The OpenAI API will be used for the core intelligence of the agents (e.g., analyzing text, suggesting tasks). |
| **Integrations** | **Google Cloud Platform (GCP)** | Specifically for the **Gmail API** and **Pub/Sub** service. This is required for the highest-priority integration of reading emails to create tensions. |
| **Deployment** | **Docker, Docker Compose** | Containerizing the application (FastAPI backend, agents, etc.) ensures consistency across development and production environments. Docker Compose will be used to orchestrate the services locally. |
| **Frontend (Internal Tools)** | **Streamlit (for Admin/Ops)** | While a full user-facing UI is out of scope for the MVP, Streamlit will be used to quickly build simple internal dashboards for monitoring agent activity, viewing the graph state, and manual data entry. |
