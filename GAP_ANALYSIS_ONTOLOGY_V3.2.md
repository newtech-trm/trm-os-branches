# Phân tích GAP Ontology V3.2 (Cập nhật dựa trên OpenAPI)

## Tiến độ mới nhất (18/06/2025)

- ✅ **Khắc phục lỗi integration tests với Neo4j thật**: Đã phát hiện và sửa các vấn đề trong integration tests để đảm bảo tất cả tests có thể chạy với cơ sở dữ liệu Neo4j thật (không mock). Cụ thể đã sửa lỗi relationships bắt buộc trong fixtures, enum không khớp (`TaskType`, `TaskStatus`), thiếu các trường bắt buộc trong payloads API, và tên method không đồng nhất giữa API endpoint và service layer (`create_knowledge_snippet` vs `create_snippet`).

- ✅ **Sửa lỗi API Recognition**: Đã khắc phục các vấn đề validation trong API Recognition. Đã tạo module `enum_adapter.py` để chuẩn hóa các giá trị enum không đồng nhất từ Neo4j (có nhiều dạng biểu diễn: uppercase, title-case, tên enum đầy đủ). Đã cải thiện xử lý lỗi và logging chi tiết. Tạm thời đã bỏ `response_model` của FastAPI để chuẩn hóa dữ liệu thủ công.

- ✅ **Tạo KnowledgeSnippet theo Ontology V3.2**: Đã triển khai đầy đủ entity `KnowledgeSnippet` với các thuộc tính (`snippetType`, `content`, `tags`) và API endpoints thích hợp. Đã sửa lỗi tương thích giữa API route `/api/v1/knowledge-snippets/` và service method `create_snippet()` để đảm bảo hoạt động đúng.

- ⚠️ **Phát hiện các vấn đề vớidữ liệu legacy trong Neo4j**: Phát hiện dữ liệu legacy trong Neo4j có nhiều vấn đề như: các giá trị enum không đồng nhất (`RecognitionType`, `RecognitionStatus`), trường DateTime không chuẩn, thiếu trường bắt buộc trong nhiều bản ghi. Cần cân nhắc giữa việc migrate dữ liệu hoàn toàn hoặc xử lý qua adapter.

- 🔍 **GAP từ data adapter**: Cần (1) Chuẩn hóa cách serialize/deserialize dữ liệu đặc biệt (DateTime, Enum, Array) giữa Neo4j-Neomodel-Pydantic, (2) Thống nhất cách xử lý trường bắt buộc thiếu trong dữ liệu legacy, (3) Tạo các adapter module tập trung (`enum_adapter.py`, `datetime_adapter.py`) để đảm bảo nhất quán.

- ⚠️ **Tiếp tục chiến lược Ontology-First**: Các vấn đề phát hiện cho thấy cần tiếp tục chuẩn hóa dữ liệu theo Ontology V3.2 xuyên suốt từ Neo4j models đến API responses. Đã rút ra nhiều bài học cho Entity WIN sắp triển khai.

## Entity GAP Analysis

| Entity trong Ontology V3.2 | Trạng thái hiện tại | Chi tiết GAP (Dựa trên OpenAPI và Ontology V3.2) |
|---------------------------|---------------------|---------------------------------------------------|
| **User/Agent**            | ✅ Đã triển khai     | User và Agent được quản lý qua API `/api/v1/users/`. Task có thể gán cho `user_id` và `agent_id`. Cần review thuộc tính chi tiết theo Ontology V3.2. |
| **Project**               | ✅ Đã triển khai     | Đã triển khai CRUD đầy đủ qua API `/api/v1/projects/`. Đã bổ sung đầy đủ thuộc tính mở rộng (`goal`, `scope`, `priority`, `project_type`, `tags`, `start_date`, `target_end_date`, `health`, `metrics`, `is_strategic`, etc.) theo Ontology V3.2. Đã triển khai các relationship `MANAGES_PROJECT` (Agent → Project), `ASSIGNED_TO_PROJECT` (Resource → Project), và parent-child relationship giữa các Project. |
| **Task**                  | ✅ Đã triển khai     | Đã triển khai CRUD cơ bản qua API `/api/v1/tasks/` và các endpoint gán task. Cần review thuộc tính chi tiết (`taskType`, `priority`, etc.) theo Ontology V3.2. |
| **Resource**              | ✅ Đã triển khai     | Entity Resource và các subtype (`FinancialResource`, `KnowledgeResource`, `HumanResource`, `ToolResource`, `EquipmentResource`, `SpaceResource`) đã có API tạo (POST) và quản lý (GET, PUT, DELETE) qua `/api/v1/resources/` và các sub-path. Cần review thuộc tính chi tiết. |
| **Tension**               | ✅ Đã triển khai     | Đã triển khai CRUD cơ bản qua API `/api/v1/tensions/`. Cần review thuộc tính chi tiết (`currentState`, `desiredState`, etc.) theo Ontology V3.2. |
| **Recognition**           | ⚠️ Triển khai một phần | Graph model `recognition.py` đã được cập nhật theo Ontology V3.2. Đã sửa lỗi endpoint `GET /api/v1/recognitions/` với chuẩn hóa enum, datetime và trường bắt buộc. Cần tiếp tục triển khai đầy đủ CRUD endpoints. |
| **WIN**                   | ⚠️ Triển khai một phần | Graph model `win.py` đã được cập nhật theo Ontology V3.2 (bao gồm các thuộc tính `name`, `status`, `winType`, `tags` và các mối quan hệ `led_to_by_events`, `led_to_by_projects`, `recognized_by_recognitions`, `generates_knowledge_snippets`, `generates_events`). API endpoints (CRUD) chưa triển khai. |
| **KnowledgeAsset**        | ⚠️ Triển khai một phần | Có `KnowledgeResource` được triển khai qua API `/api/v1/resources/knowledge`. Cần làm rõ mối quan hệ với `ConceptualFramework`, `Methodology` và các thuộc tính chuyên biệt của `KnowledgeAsset`. |
| **KnowledgeSnippet**      | ⚠️ Triển khai một phần | Có `KnowledgeResource` qua API. Chưa rõ `KnowledgeSnippet` có được quản lý riêng, là một phần của `KnowledgeResource`, hay cần API riêng. |
| **Event**                 | ✅ Đã triển khai     | Graph model `event.py` đã được cập nhật đầy đủ theo Ontology V3.2 (bao gồm `name`, `description`, `tags`, `payload` và các mối quan hệ `triggered_by_actor`, `primary_context_agent/project/task/resource`, `generated_by_projects/tasks/agents/recognitions/wins`). API endpoints CRUD đã triển khai thành công qua `/api/v1/events/`. Đã thêm adapter serialization để xử lý datetime. |
| **Team**                  | ✅ Đã triển khai     | Đã triển khai CRUD cơ bản qua API `/api/v1/teams/` và quản lý members. Cần review thuộc tính chi tiết theo Ontology V3.2. |
| **Skill**                 | ✅ Đã triển khai     | Đã triển khai CRUD cơ bản qua API `/api/v1/skills/`. Cần review thuộc tính chi tiết theo Ontology V3.2. |


| Relationship trong Ontology V3.2 | Trạng thái hiện tại | Chi tiết GAP (Dựa trên OpenAPI và Ontology V3.2) |
|----------------------------------|---------------------|---------------------------------------------------|
| **ASSIGNS_TASK** (Agent/User ASSIGNS_TASK Task) | ✅ Đã triển khai | Triển khai qua API `/api/v1/tasks/{task_id}/assign/user/{user_id}` và `/api/v1/tasks/{task_id}/assign/agent/{agent_id}`. Có các thuộc tính quan hệ như `assignment_type`, `priority_level`, `estimated_effort`, `assigned_by`, `notes`. API cho phép chấp nhận và hoàn thành task. |
| **LEADS_TO_WIN** (Project/Event LEADS_TO_WIN WIN) | ⚠️ Triển khai một phần | Graph model `win.py` định nghĩa mối quan hệ này từ `Project` và `Event` thông qua `LeadsToWinRel`. API (và WIN API) chưa triển khai. |
| **GENERATES_EVENT** (Event <- Recognition): Recognition nào đã tạo ra Event này. | ⚠️ Triển khai một phần | Graph models `project.py`, `task.py`, `agent.py`, `recognition.py`, `win.py` và `event.py` (thông qua `GeneratesEventRel`) định nghĩa mối quan hệ này. API endpoints cho việc tạo/quản lý mối quan hệ này và cho `Event` entity vẫn chưa triển khai. |
| **GIVEN_BY** (Agent GIVEN_BY Recognition) | ⚠️ Triển khai một phần | Graph model `recognition.py` định nghĩa mối quan hệ này (là `RelationshipFrom`). API chưa triển khai. |
| **RECEIVED_BY** (Recognition RECEIVED_BY Agent) | ⚠️ Triển khai một phần | Graph model `recognition.py` định nghĩa mối quan hệ này. API chưa triển khai. |
| **RECOGNIZES_WIN** (Recognition RECOGNIZES_WIN WIN) | ⚠️ Triển khai một phần | Graph models `recognition.py` và `win.py` định nghĩa mối quan hệ này thông qua `RecognizesWinRel`. API (và WIN/Recognition entity API) chưa triển khai. |
| **RECOGNIZES_CONTRIBUTION_TO** (Recognition RECOGNIZES_CONTRIBUTION_TO [Project,Task,Resource]) | ⚠️ Triển khai một phần | Graph model `recognition.py` định nghĩa mối quan hệ này. API chưa triển khai. |
| **RESOLVES_TENSION** (Project RESOLVES_TENSION Tension) | ✅ Đã triển khai | Triển khai qua API `/api/v1/projects/{project_id}/resolves-tension/{tension_id}` và `/api/v1/tensions/{tension_id}/resolved-by/{project_id}`. |
| **IS_PART_OF_PROJECT** (Task IS_PART_OF_PROJECT Project) | ✅ Đã triển khai (ngầm) | Ngầm định qua API tạo (`POST /api/v1/tasks/` yêu cầu `project_id`) và liệt kê Task (`GET /api/v1/tasks/` theo `project_id`). |
| **ACTOR_TRIGGERED_EVENT** (Event <- Agent): Ai/Cái gì đã kích hoạt Event này. | ✅ Đã triển khai | Graph model `event.py` định nghĩa mối quan hệ này (là `RelationshipFrom`). API đã triển khai và hoạt động đúng trong API `/api/v1/events/` thông qua tham số `actor_uid` trong request. |
| **EVENT_CONTEXT** (Event EVENT_CONTEXT [Project,Task,etc.]) | ✅ Đã triển khai | Graph model `event.py` định nghĩa relationship riêng cho từng loại entity (`primary_context_agent`, `primary_context_project`, `primary_context_task`, `primary_context_resource`). API đã triển khai và hoạt động đúng trong `/api/v1/events/` thông qua `context_uid` và `context_node_label`. |
| **HAS_SKILL** (User/Agent HAS_SKILL Skill) | ⚠️ Chưa rõ qua API | Không có API endpoint trực tiếp quản lý mối quan hệ này trong OpenAPI spec. Cần kiểm tra logic service hoặc nếu quản lý qua thuộc tính của User/Agent. |
| **PARTICIPATES_IN** (User PARTICIPATES_IN Team) | ✅ Đã triển khai | Triển khai qua API `/api/v1/teams/{team_uid}/members/{user_uid}` (thêm user vào team) và `GET /api/v1/teams/{team_uid}/members`. |
| **MANAGES_PROJECT** (Agent MANAGES_PROJECT Project) | ⚠️ Chưa rõ qua API | Không có API endpoint trực tiếp quản lý mối quan hệ này. Có thể được quản lý qua thuộc tính `ownerAgentId` của Project (nếu có). Cần kiểm tra schema Project và logic service. |
| **ASSIGNED_TO_PROJECT** (Resource ASSIGNED_TO_PROJECT Project) | ✅ Đã triển khai | Triển khai qua API `/api/v1/resources/{resource_uid}/assign-to-project/{project_uid}`. |
| **ASSIGNED_TO_TASK** (Resource ASSIGNED_TO_TASK Task) | ✅ Đã triển khai | Triển khai qua API `/api/v1/resources/{resource_uid}/assign-to-task/{task_uid}`. |
| **GENERATES_KNOWLEDGE**          | ❌ Chưa triển khai   | Không có API endpoint tương ứng trong OpenAPI spec. |
3.  **Triển khai các API endpoint còn lại**
    * Chi tiết API endpoints cho `Recognition`:
        * `POST /api/v1/recognitions/` ✗ Chưa triển khai
        * `GET /api/v1/recognitions/{recognition_uid}` ✗ Chưa triển khai
        * `PUT /api/v1/recognitions/{recognition_uid}` ✗ Chưa triển khai
        * `DELETE /api/v1/recognitions/{recognition_uid}` ✗ Chưa triển khai
        * `GET /api/v1/recognitions/` ✅ Đã triển khai, đã sửa lỗi validation với chuẩn hóa enum và datetime

    * Chi tiết API endpoints cho `WIN`:
        * `POST /api/v1/wins/` ✗ Chưa triển khai
        * `GET /api/v1/wins/{win_uid}` ✗ Chưa triển khai
        * `PUT /api/v1/wins/{win_uid}` ✗ Chưa triển khai
        * `DELETE /api/v1/wins/{win_uid}` ✗ Chưa triển khai
        * `GET /api/v1/wins/` ✗ Chưa triển khai

    * Chi tiết API endpoints cho `KnowledgeSnippet`:
        * `POST /api/v1/knowledge-snippets/` ✗ Chưa triển khai
        * `GET /api/v1/knowledge-snippets/{snippet_uid}` ✗ Chưa triển khai
        * `PUT /api/v1/knowledge-snippets/{snippet_uid}` ✗ Chưa triển khai
        * `DELETE /api/v1/knowledge-snippets/{snippet_uid}` ✗ Chưa triển khai
        * `GET /api/v1/knowledge-snippets/` ✗ Chưa triển khai

    * API endpoints quản lý relationship chung:
        * `POST /api/v1/{entity_type}/{entity_uid}/relationships/{relationship_type}` ✗ Chưa triển khai
        * `DELETE /api/v1/{entity_type}/{entity_uid}/relationships/{relationship_type}/{target_uid}` ✗ Chưa triển khai
        * `GET /api/v1/{entity_type}/{entity_uid}/relationships/{relationship_type}` ✗ Chưa triển khai

    * Triển khai API endpoints cho các mối quan hệ đã được định nghĩa trong model và các mối quan hệ còn thiếu, bao gồm:
        * `LEADS_TO_WIN` (Project → WIN)
        * `GENERATES_EVENT` (từ `Project`, `Task`, `Agent`, `Recognition`, `WIN` tới `Event`): Model đã cập nhật. API đã được triển khai thành công.
        * Các mối quan hệ của `Recognition`: `GIVEN_BY`, `RECEIVED_BY`, `RECOGNIZES_WIN`, `RECOGNIZES_CONTRIBUTION_TO`: Model đã cập nhật. API cần triển khai.
        * Các mối quan hệ của `WIN`: `LEADS_TO_WIN` (từ `Project`, `Event`), `RECOGNIZED_BY` (từ `Recognition`), `GENERATES_KNOWLEDGE` (tới `KnowledgeSnippet`), `GENERATES_EVENT` (tới `Event`): Model đã cập nhật. API cần triển khai.
        * `ACTOR_TRIGGERED_EVENT` (Event <- Agent): Ai/Cái gì đã kích hoạt Event này. API đã được triển khai thành công.
        * `EVENT_CONTEXT` (Event → [Project,Task,etc.]): Model đã cập nhật. API đã được triển khai thành công thông qua các relationship riêng biệt cho từng loại entity.
        * `HAS_SKILL` (User/Agent → Skill): Cân nhắc API trực tiếp nếu cần, hoặc làm rõ cách quản lý.
        * `MANAGES_PROJECT` (Agent → Project): ✅ Đã triển khai API trực tiếp qua các endpoints `/api/v1/projects/{project_id}/managers/{agent_id}` (POST, PUT, DELETE) và `/api/v1/projects/{project_id}/managers` hoặc `/api/v1/projects/{project_id}/managers-with-relationships` (GET) với đầy đủ thuộc tính relationship (`role`, `responsibility_level`, `appointed_at`, `notes`).
        * `GENERATES_KNOWLEDGE` (ví dụ từ `WIN` tới `KnowledgeSnippet`), `USES_KNOWLEDGE`, `CREATES_KNOWLEDGE`.
        * `TRIGGERED_BY`, `TRIGGERS` (rà soát lại các mối quan hệ này, có thể một số đã được thay thế bởi `ACTOR_TRIGGERED_EVENT` hoặc cần làm rõ thêm).
{{ ... }}

4.  **Kiểm thử toàn diện:**
    * Kiểm thử tất cả các API endpoint đã triển khai dựa trên OpenAPI spec và logic nghiệp vụ.
    * ✅ Đã kiểm thử thành công API endpoints của Project và các relationship mới (`MANAGES_PROJECT`, `ASSIGNED_TO_PROJECT`, parent-child) thông qua script `seed_extended_project.py`.
    * ✅ Đã sửa lỗi và kiểm thử thành công API endpoint `GET /api/v1/recognitions/` với dữ liệu thực tế từ Neo4j.
    * Xác nhận đầy đủ thuộc tính của các entity và relationship models/schemas.
    * Kiểm tra tính đúng đắn của các mối quan hệ được tạo/quản lý qua API.
    * Kiểm thử việc serialize/deserialize datetime cho tất cả entity, sử dụng chuẩn `Neo4jDateTimeProperty` và adapter ISO format. ✗ Chưa triển khai toàn diện cho mọi entity.

5.  **Data Adapter Pattern:**
    * ✅ **Đã triển khai Enum Adapter**: Tạo module `enum_adapter.py` để chuẩn hóa các giá trị enum không đồng nhất trong Neo4j. Xử lý nhiều dạng biểu diễn khác nhau (uppercase, title-case, tên enum đầy đủ) và trả về giá trị chuẩn theo ontology.
    * ✅ **Đã triển khai DateTime Adapter**: Chuẩn hóa datetime object từ Neo4j sang chuẩn ISO 8601 trước khi trả về qua API. 
    * **Bài học từ Recognition API**: 
      * Dữ liệu trong Neo4j chịa các kỹ thuật lưu trữ không đồng nhất (enum, datetime, trường bắt buộc). Cần cân bằng giữa cách migrate dữ liệu hoặc sử dụng adapter.
      * FastAPI `response_model` rất nghiêm ngặt về validation, nên trong trường hợp legacy data có thể tạm thời bỏ qua và xử lý thủ công.
      * Phương pháp "robust by default": Trả về dữ liệu hoạt động được dù có vài item gặp lỗi, kèm cảnh báo chi tiết.
    * **Kế hoạch nâng cao**:
      * Tổ chức các adapter vào một module riêng (`trm_api/adapters/`) để tăng khả năng tái sử dụng.
      * Tạo các decorator để áp dụng adapter một cách tự động cho các endpoint.
      * Phát triển các test case riêng cho logic của adapter.
      * Tạo migration script để dần chuẩn hóa dữ liệu legacy trong Neo4j.

6.  **Cập nhật tài liệu:**
    *   Liên tục cập nhật `GAP_ANALYSIS_ONTOLOGY_V3.2.md` này.
    *   Đảm bảo `ONTOLOGY NỘI BỘ TRM - BẢN THIẾT KẾ THỐNG NHẤT HOÀN CHỈNH V3.2.md` là nguồn tham chiếu chính xác.
