---
# TRM-OS Ontology-First **Master Execution Plan** (v3.2)

> Machine-parsable. AI agents MUST follow exactly. **No mock/demo. All services real.**

---
## 1. metadata

| key | value |
|-----|-------|
| project | TRM-OS |
| version | 3.2 |
| strategy | ontology_first |
| author | Cascade |
| created | 2025-06-12 |
| status | draft-0.2 |

---
## 2. global_rules

1. camelCase identifiers
2. forbidHardcode = true
3. forbidMockDemo = true
4. secureByDesign = true
5. askUserBeforeMajorChange = true
6. allEndpointsVersioned = true (v1)
7. infraAsCode = true (docker-compose, terraform later)

---
## 3. architecture_overview

```
┌────────────┐      HTTP       ┌──────────────┐
│ React SPA  │  ───────────▶  │  FastAPI API │
└────────────┘                │  (Gateway)   │
       ▲  ▲ WS                └──────┬───────┘
       │  │ live-events              │ REST / WS / gRPC
       │  └──────────────┐           │
       │                 ▼           ▼
┌──────────────┐   Kafka topics   ┌──────────────┐         ┌──────────────┐
│ Event Bus    │◀───────────────▶│  ARQ Worker  │─Redis──▶│  AI Agents   │
│ (Kafka)      │                 └──────────────┘         └──────────────┘
└──────┬───────┘                        │                        │
       │ Neo4j Bolt (graph)             │ embeddings            │ Cypher
       ▼                                ▼                        ▼
┌──────────────┐                 ┌──────────────┐         ┌──────────────┐
│ Neo4j Aura   │                 │ Supabase     │         │ Snowflake    │
│ (graph core) │                 │ (pgvector)   │         │ (analytics)  │
└──────────────┘                 └──────────────┘         └──────────────┘
```

### component_list
- `react_spa` (Vite + Tailwind) → port 3000
- `fastapi_gateway` → port 8000 (future envoy ingress)
- `kafka` (bitnami stack) + `schema_registry`
- `redis` (for ARQ)
- `arq_worker` container executing background jobs
- `ai_agents` package (agents orchestrator)
- `neo4j_aura` free tier (or local dev)
- `supabase_pg` with pgvector extension
- `snowflake_dw` for historical analytics
- `grafana_prometheus` + `jaeger` for metrics / traces

---
## 4. data_model

### 4.1 Nodes
| label | props |
|-------|-------|
| Person | id, fullName, role |
| Recognition | id, content, createdAt |
| Tension | id, title, severity, status |
| Project | id, name, status, startAt, endAt |
| WIN | id, score |

### 4.2 Relationships
| relType | start → end | props |
|---------|-------------|-------|
| RECOGNIZED_BY | Recognition → Person |  |
| PARTICIPATES_IN | Person → Project | role |
| RESOLVES | Project → Tension |  |
| RESULTS_IN | Project → WIN |  |

### 4.3 Cypher migration snippet (`migrations/001_init.cypher`)
```cypher
CREATE CONSTRAINT person_id IF NOT EXISTS ON (n:Person) ASSERT n.id IS UNIQUE;
CREATE CONSTRAINT project_id IF NOT EXISTS ON (n:Project) ASSERT n.id IS UNIQUE;
// ... more constraints
```

### 4.4 pgvector schema
```sql
CREATE TABLE IF NOT EXISTS knowledge_snippet_embeddings (
  id uuid primary key default gen_random_uuid(),
  snippet text not null,
  embedding vector(1536) not null
);
```

---
## 5. event_catalog

| eventType | schema | producer | consumer | critical |
|-----------|--------|----------|----------|----------|
| RECOGNITION_CREATED | schemas/recognition_created.json | RecognitionService | RecognitionAgent | yes |
| KNOWLEDGE_SNIPPET_UPSERTED | schemas/knowledge_snippet_upserted.json | DocsService | KnowledgeEmbeddingAgent | yes |
| TENSION_REPORTED | schemas/tension_reported.json | TaskService | TensionAnalyzer | medium |
| PROJECT_COMPLETED | schemas/project_completed.json | ProjectService | WinEvaluatorAgent | high |

---
## 6. api_contracts (excerpt)

### 6.1 REST
| METHOD | PATH | SCHEMA_IN | SCHEMA_OUT | authScope |
|--------|------|-----------|------------|-----------|
| POST | /v1/recognitions | RecognitionCreateDTO | RecognitionDTO | rw_recognition |
| GET | /v1/recognitions/{id} | — | RecognitionDTO | r_recognition |
| POST | /v1/projects | ProjectCreateDTO | ProjectDTO | rw_project |

### 6.2 WebSocket
- `/ws/live` stream events after auth (JWT)

---
## 7. ci_cd_pipeline

1. **Lint & Test** (GitHub Actions)
   - `ruff`, `pytest`, `pytest-e2e`, `markdownlint`.
2. **Build Images**
   - `docker build` backend, worker, nginx – push to GHCR.
3. **Deploy Staging**
   - Fly.io (backend+worker), Netlify (frontend), Neo4j Aura dev, Supabase dev.
4. **E2E Cypress** against staging.
5. **Blue-Green Prod** when staging .

---
## 8. risk_register

| id | risk | impact | likelihood | mitigation |
|----|------|--------|------------|-----------|
| R1 | LLM rate-limit | medium | high | batching, caching embeddings |
| R2 | Neo4j Aura downtime | high | medium | daily export + standby docker neo4j |
| R3 | Cost overrun Snowflake | medium | low | use auto-suspend & warehouse sizing |

---
## 9. sla_observability

| metric | target | alert |
|--------|--------|-------|
| API p95 latency | < 150 ms | pager if > 300 ms 5 m |
| Event end-to-end (Recognition→Neo4j) | < 2 s | warn if > 5 s |
| Uptime | ≥ 99.5 % monthly | pager if < 99 % |

Tracing: OpenTelemetry → Jaeger; Metrics: Prometheus → Grafana, Alertmanager.

---
## 10. sprint_schedule & task_matrix

> Estimates in ideal hours, owner `TBD`.

### Sprint 0 – **infra_bootstrap** (5 days)
| id | task | est | owner |
|----|------|-----|-------|
| S0-01 | Write `docker-compose.yml` base stack | 4 |  |
| S0-02 | Author `001_init.cypher` & migrate | 6 |  |
| S0-03 | Provision Supabase dev project & pgvector table | 3 |  |
| S0-04 | Draft `asyncapi.yaml` for base events | 4 |  |
| S0-05 | Seed sample data script (`seed_recognition_win.py`) | 4 |  |

### Sprint 1 – **core_services** (7 days)
| id | task | est | owner |
|----|------|-----|-------|
| S1-01 | FastAPI modules recognition/project/task | 10 |  |
| S1-02 | Event publishers w/ schema registry | 6 |  |
| S1-03 | ARQ worker container + Redis config | 4 |  |
| S1-04 | RecognitionAgent implementation | 6 |  |
| S1-05 | KnowledgeEmbeddingAgent | 8 |  |
| S1-06 | Unit + integration tests | 6 |  |

### Sprint 2 – **analytics_loop** (7 days)
| id | task | est | owner |
|----|------|-----|-------|
| S2-01 | NLP model fine-tune for TensionAnalyzer | 12 |  |
| S2-02 | WinEvaluatorAgent scoring logic | 6 |  |
| S2-03 | WebSocket gateway & React dashboard | 8 |  |
| S2-04 | E2E tests dashboard latency | 4 |  |

### Sprint 3 – **prod_hardening** (5 days)
| id | task | est | owner |
|----|------|-----|-------|
| S3-01 | Auth0/Supabase auth integration | 6 |  |
| S3-02 | OpenTelemetry tracing everywhere | 6 |  |
| S3-03 | GitHub Actions CI workflows | 4 |  |
| S3-04 | Fly.io deploy staging + prod blue-green | 7 |  |
| S3-05 | Final acceptance & handover docs | 4 |  |

---
## 11. ai_agent_workflows

### 11.1 RecognitionAgent
```
on RECOGNITION_CREATED:
  1. fetch person node (or create)
  2. create Recognition node & RECOGNIZED_BY rel
  3. emit KNOWLEDGE_SNIPPET_UPSERTED
```

### 11.2 KnowledgeEmbeddingAgent
```
on KNOWLEDGE_SNIPPET_UPSERTED:
  1. call OpenAI embeddings (retry=3, backoff)
  2. store pgvector row
  3. ack Kafka offset
```

### 11.3 TensionAnalyzer
```
on TENSION_REPORTED → run spaCy + classifier → update severity
```

---
## 12. next_action (immediate)

1. **Branch** `ontology-first-architecture`
2. Create `migrations/001_init.cypher` with constraints & indexes (see §4.3)
3. Expand `docker-compose.yml` with Kafka, Redis, Neo4j, Supabase (dev)
4. Commit & push ⇒ open PR `feat/infra_bootstrap`
5. Run `make up` locally; ensure all containers healthy

---
# END OF PLAN