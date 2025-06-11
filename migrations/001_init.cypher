// migrations/001_init.cypher

// Constraints for Tension
CREATE CONSTRAINT tension_id_unique IF NOT EXISTS FOR (t:Tension) REQUIRE t.tensionId IS UNIQUE;
CREATE CONSTRAINT tension_id_exists IF NOT EXISTS FOR (t:Tension) REQUIRE t.tensionId IS NOT NULL;
CREATE CONSTRAINT tension_title_exists IF NOT EXISTS FOR (t:Tension) REQUIRE t.title IS NOT NULL;
CREATE CONSTRAINT tension_status_exists IF NOT EXISTS FOR (t:Tension) REQUIRE t.status IS NOT NULL;
CREATE CONSTRAINT tension_priority_exists IF NOT EXISTS FOR (t:Tension) REQUIRE t.priority IS NOT NULL;
CREATE CONSTRAINT tension_creationDate_exists IF NOT EXISTS FOR (t:Tension) REQUIRE t.creationDate IS NOT NULL;
CREATE CONSTRAINT tension_source_exists IF NOT EXISTS FOR (t:Tension) REQUIRE t.source IS NOT NULL;

// Constraints for Task
CREATE CONSTRAINT task_id_unique IF NOT EXISTS FOR (t:Task) REQUIRE t.taskId IS UNIQUE;
CREATE CONSTRAINT task_id_exists IF NOT EXISTS FOR (t:Task) REQUIRE t.taskId IS NOT NULL;
CREATE CONSTRAINT task_title_exists IF NOT EXISTS FOR (t:Task) REQUIRE t.title IS NOT NULL;
CREATE CONSTRAINT task_status_exists IF NOT EXISTS FOR (t:Task) REQUIRE t.status IS NOT NULL;
CREATE CONSTRAINT task_priority_exists IF NOT EXISTS FOR (t:Task) REQUIRE t.priority IS NOT NULL;
CREATE CONSTRAINT task_creationDate_exists IF NOT EXISTS FOR (t:Task) REQUIRE t.creationDate IS NOT NULL;

// Constraints for Project
CREATE CONSTRAINT project_id_unique IF NOT EXISTS FOR (p:Project) REQUIRE p.projectId IS UNIQUE;
CREATE CONSTRAINT project_id_exists IF NOT EXISTS FOR (p:Project) REQUIRE p.projectId IS NOT NULL;
CREATE CONSTRAINT project_title_exists IF NOT EXISTS FOR (p:Project) REQUIRE p.title IS NOT NULL;
CREATE CONSTRAINT project_status_exists IF NOT EXISTS FOR (p:Project) REQUIRE p.status IS NOT NULL;

// Constraints for Agent
CREATE CONSTRAINT agent_id_unique IF NOT EXISTS FOR (a:Agent) REQUIRE a.agentId IS UNIQUE;
CREATE CONSTRAINT agent_id_exists IF NOT EXISTS FOR (a:Agent) REQUIRE a.agentId IS NOT NULL;
CREATE CONSTRAINT agent_name_exists IF NOT EXISTS FOR (a:Agent) REQUIRE a.name IS NOT NULL;
CREATE CONSTRAINT agent_type_exists IF NOT EXISTS FOR (a:Agent) REQUIRE a.type IS NOT NULL;

// Constraints for Event
CREATE CONSTRAINT event_id_unique IF NOT EXISTS FOR (e:Event) REQUIRE e.eventId IS UNIQUE;
CREATE CONSTRAINT event_id_exists IF NOT EXISTS FOR (e:Event) REQUIRE e.eventId IS NOT NULL;
CREATE CONSTRAINT event_type_exists IF NOT EXISTS FOR (e:Event) REQUIRE e.type IS NOT NULL;
CREATE CONSTRAINT event_timestamp_exists IF NOT EXISTS FOR (e:Event) REQUIRE e.timestamp IS NOT NULL;

// Indexes for Tension
CREATE INDEX tension_status_index IF NOT EXISTS FOR (t:Tension) ON (t.status);
CREATE INDEX tension_priority_index IF NOT EXISTS FOR (t:Tension) ON (t.priority);
CREATE INDEX tension_creationDate_index IF NOT EXISTS FOR (t:Tension) ON (t.creationDate);
CREATE INDEX tension_source_index IF NOT EXISTS FOR (t:Tension) ON (t.source);
CREATE INDEX tension_assigneeId_index IF NOT EXISTS FOR (t:Tension) ON (t.assigneeAgentId);

// Indexes for Task
CREATE INDEX task_status_index IF NOT EXISTS FOR (t:Task) ON (t.status);
CREATE INDEX task_priority_index IF NOT EXISTS FOR (t:Task) ON (t.priority);
CREATE INDEX task_creationDate_index IF NOT EXISTS FOR (t:Task) ON (t.creationDate);
CREATE INDEX task_dueDate_index IF NOT EXISTS FOR (t:Task) ON (t.dueDate);
CREATE INDEX task_assigneeId_index IF NOT EXISTS FOR (t:Task) ON (t.assigneeAgentId);
CREATE INDEX task_projectId_index IF NOT EXISTS FOR (t:Task) ON (t.projectId);

// Indexes for Project
CREATE INDEX project_status_index IF NOT EXISTS FOR (p:Project) ON (p.status);

// Indexes for Agent
CREATE INDEX agent_type_index IF NOT EXISTS FOR (a:Agent) ON (a.type);

// Indexes for Event
CREATE INDEX event_type_index IF NOT EXISTS FOR (e:Event) ON (e.type);
CREATE INDEX event_timestamp_index IF NOT EXISTS FOR (e:Event) ON (e.timestamp);
CREATE INDEX event_actorAgentId_index IF NOT EXISTS FOR (e:Event) ON (e.actorAgentId);
