# CHỈ DẪN BỐI CẢNH DỰ ÁN TRM-OS

## 1. Tổng quan dự án

TRM-OS là một hệ thống quản lý tri thức và workflow dựa trên ontology, sử dụng Neo4j làm cơ sở dữ liệu đồ thị để lưu trữ các entity, relationship và tổ chức dữ liệu theo mô hình ontology-first.

### File nền tảng quan trọng

- **@ONTOLOGY NỘI BỘ TRM - BẢN THIẾT KẾ THỐNG NHẤT HOÀN CHỈNH V3.2.md** - File "Hiến pháp" chứa đầy đủ định nghĩa ontology
- **@trmos-sumary-documentation.md** - File tóm tắt các thông tin về TRM-OS
- **@GAP_ANALYSIS_ONTOLOGY_V3.2.md** - File phân tích khoảng cách giữa ontology định nghĩa và triển khai thực tế
- **@plan.md** - File kế hoạch triển khai dự án theo phương pháp ontology-first

### Thư mục docs chứa các tài liệu kỹ thuật

- **docs/core-specs/entities-mvp.md** - Định nghĩa chi tiết các entity cho MVP
- **docs/core-specs/relationships-mvp.md** - Định nghĩa chi tiết các relationship cho MVP
- **docs/core-specs/agent-workflows.md** - Mô tả luồng làm việc của các agent
- **docs/core-specs/philosophy-in-code.md** - Triết lý chuyển đổi từ ontology sang code

## 2. Chiến lược triển khai: Ontology-first

- **Nguyên tắc chính**: Xây dựng hệ thống dựa trên ontology đã định nghĩa, không đơn giản hóa hay mock dữ liệu.
- **Cách tiếp cận**: Từ định nghĩa ontology, xây dựng các graph model, API endpoint, và service layer phù hợp.
- **Quy trình**:
  1. Định nghĩa entity trong Neo4j (node class)
  2. Định nghĩa relationship giữa các entity
  3. Xây dựng API endpoint cho entity và relationship
  4. Triển khai service layer để xử lý logic nghiệp vụ
  5. Kiểm thử CRUD và các luồng nghiệp vụ
  6. Seed dữ liệu mẫu để validate hoạt động đúng của ontology

## 3. Hiện trạng dự án

### Kết quả đạt được

- ✅ **Entity Agent**: Đã triển khai đầy đủ, API endpoint hoạt động ổn định
- ✅ **Entity Event**: Đã triển khai thành công, fix hết các lỗi và seed dữ liệu thành công
- ✅ **Relationships**: Đã triển khai thành công các relationship chính:
  - ACTOR_TRIGGERED_EVENT (Agent -> Event)
  - EVENT_CONTEXT (Event -> [Agent, Project, Task, Resource])

### Fix lỗi đã thực hiện

1. **Neo4jDateTimeProperty**: Tạo custom property type để xử lý đúng định dạng DateTime trong Neo4j
2. **Refactor relationship context**: Chuyển từ relationship trừu tượng sang concrete relationship cho từng entity type
3. **Serialize DateTime**: Thêm adapter để chuyển đổi datetime object thành string ISO format khi trả về response
4. **Import Class**: Bổ sung đúng các import cho Resource, Project trong agent.py
5. **Capabilities Array**: Refactor từ JSONProperty sang ArrayProperty(StringProperty()) để tương thích với dữ liệu

### Chi tiết cụ thể việc fix lỗi

1. **Fix lỗi __label__**: Trước đây, code sử dụng BaseNode làm target cho relationship context_node, gây lỗi vì BaseNode là abstract không có __label__. Đã fix bằng cách tạo các relationship cụ thể cho từng loại entity.

```python
# Code cũ - Gây lỗi
context_node = RelationshipTo('trm_api.graph_models.base', 'BaseNode', 'EVENT_CONTEXT')

# Code mới - Đã fix
primary_context_agent = RelationshipTo('trm_api.graph_models.agent', 'Agent', 'EVENT_CONTEXT')
primary_context_project = RelationshipTo('trm_api.graph_models.project', 'Project', 'EVENT_CONTEXT')
primary_context_task = RelationshipTo('trm_api.graph_models.task', 'Task', 'EVENT_CONTEXT')
primary_context_resource = RelationshipTo('trm_api.graph_models.resource', 'Resource', 'EVENT_CONTEXT')
```

2. **Fix lỗi datetime serialization**: Trước đây, API trả về datetime object gây lỗi 500 khi Pydantic cố gắng serialize. Đã fix bằng cách tạo adapter chuyển đổi dữ liệu:

```python
# Tạo adapter function trong endpoint
def convert_event_to_schema(event: EventGraphModel) -> EventSchema:
    return EventSchema(
        uid=event.uid,
        name=event.name,
        description=event.description,
        payload=event.payload,
        tags=event.tags,
        created_at=event.created_at.isoformat() if event.created_at else None,
        updated_at=event.updated_at.isoformat() if event.updated_at else None
    )
```

## 4. Cấu trúc thư mục và đường dẫn code

### Thư mục gốc (root)

```plaintext
e:\tech\trm-os-branches\
```

### Cấu trúc thư mục chính

- **docs/** - Tài liệu kỹ thuật và đặc tả
  - **core-specs/** - Đặc tả cốt lõi
  - **integration-specs/** - Đặc tả tích hợp
  - **technical-decisions/** - Các quyết định kỹ thuật
- **trm_api/** - Mã nguồn chính của API
  - **api/** - API endpoints và routers
    - **v1/** - API version 1
      - **endpoints/** - Các endpoint cụ thể
      - **schemas/** - Các schema Pydantic
  - **graph_models/** - Models Neo4j dựa trên ontology
  - **services/** - Lớp service xử lý logic nghiệp vụ
- **scripts/** - Các script hỗ trợ, seed dữ liệu

### Đường dẫn chính cần chú ý

1. **Graph Models** (entity và relationship) được định nghĩa tại:

   ```plaintext
   e:\tech\trm-os-branches\trm_api\graph_models\*.py
   ```

   Ví dụ: `agent.py`, `event.py`, `resource.py`, `project.py`, v.v.

2. **API Endpoints** được triển khai tại:

   ```plaintext
   e:\tech\trm-os-branches\trm_api\api\v1\endpoints\*.py
   ```

   Ví dụ: `event.py`, `agent.py`, `project.py`, v.v.

3. **API Schemas** (Pydantic models) được định nghĩa tại:

   ```plaintext
   e:\tech\trm-os-branches\trm_api\api\v1\schemas\*.py
   ```

   Ví dụ: `event.py`, `agent.py`, `project.py`, v.v.

4. **Services** (xử lý logic nghiệp vụ) được triển khai tại:

   ```plaintext
   e:\tech\trm-os-branches\trm_api\services\*.py
   ```

   Ví dụ: `event_service.py`, `agent_service.py`, v.v.

5. **Scripts** (seed dữ liệu, test) được lưu tại:

   ```plaintext
   e:\tech\trm-os-branches\scripts\*.py
   ```

   Ví dụ: `seed_agent_data.py`, `seed_event_data.py`, v.v.

## 5. Bài học kinh nghiệm (Lessons Learned)

### Từ các fix lỗi Event API

1. **Xử lý DateTime trong Neo4j**
   - Luôn sử dụng custom `Neo4jDateTimeProperty` thay cho `DateTimeProperty` của neomodel
   - Đảm bảo signature `inflate()` của Neo4jDateTimeProperty nhận đủ các tham số mà framework truyền vào
   - Code tham khảo trong `trm_api/graph_models/base.py`

2. **Serialize/Deserialize datetime**
   - Thêm adapter function trong endpoint để chuyển đổi các trường datetime sang string ISO format
   - Đảm bảo schema Pydantic định nghĩa các trường datetime dạng string
   - Code tham khảo trong `trm_api/api/v1/endpoints/event.py`

3. **Định nghĩa Relationship**
   - Không sử dụng relationship trừ u tượng cho các node khác loại
   - Sử dụng relationship cụ thể cho từng loại node (ví dụ `AGENT_CONTEXT`, `PROJECT_CONTEXT`)
   - Cân nhắc kiểm tra kỹ RelationshipTo/From, đảm bảo truyền đúng kiểu (class hoặc string tên class)

4. **Xử lý Array/JSON**
   - Sử dụng `ArrayProperty(StringProperty())` thay vì `JSONProperty` cho các trường mang tính array đơn giản
   - Đảm bảo dữ liệu trong Neo4j đúng kiểu với property định nghĩa trong model

### Lưu ý cho các phần tiếp theo

1. **Triển khai Recognition API**
   - Tuân thủ các checklist trong GAP Analysis
   - Áp dụng các lesson learned về datetime và relationship
   - Đảm bảo tương thích với các entity đã triển khai

2. **Triển khai WIN API**
   - Tuân thủ các checklist trong GAP Analysis
   - Đặc biệt chú ý các relationship quan trọng: LEADS_TO_WIN, GENERATES_KNOWLEDGE

3. **Triển khai KnowledgeSnippet**
   - Cần làm rõ mối quan hệ với KnowledgeResource trước khi triển khai
   - Tích hợp chặt chẽ với WIN thông qua GENERATES_KNOWLEDGE

### Kiểm soát chất lượng (QA)

1. **Kiểm thử unit test cho từng entity**
   - Mỗi entity cần test CRUD đầy đủ
   - Các validation logic cần được test kỹ

2. **Kiểm thử relationship**
   - Test việc tạo và query các relationship
   - Đảm bảo các relationship hoạt động đúng theo ontology

3. **Seed dữ liệu mẫu**
   - Luôn seed dữ liệu mẫu sau khi triển khai entity mới
   - Kiểm tra tính chất graph traversal của Neo4j qua relationship

## 6. Mục tiêu tiếp theo

Theo kế hoạch được cập nhật, mục tiêu tiếp theo là:

1. **Refactor schema/service/Cypher query cho các entity còn lại**:
   - Project
   - Resource
   - Task
   - Recognition
   - WIN

2. **Đảm bảo tất cả entity và relationship đồng bộ với ontology V3.2**:
   - Xem xét lại các relationship trong GAP Analysis
   - Triển khai các entity còn thiếu
   - Bổ sung property và relationship theo ontology

3. **Liên tục cập nhật GAP Analysis**:
   - Sau mỗi đợt triển khai entity mới
   - Đánh dấu rõ trạng thái hoàn thành
   - Mô tả cách triển khai chi tiết

## 5. Lưu ý quan trọng

- **Nghiêm cấm mock/demo/fake**: Tất cả triển khai phải thực sự hoạt động
- **Nghiêm cấm hardcode**: Phải thực sự liên thông giữa các service
- **Giữ nguyên mục đích**: Không đơn giản hóa mà phải đảm bảo sản phẩm hoàn chỉnh, chính xác
- **Luôn cập nhật GAP Analysis**: Mỗi khi hoàn thành một đoạn dài các việc
- **Chiến lược ontology-first**: Tuân thủ chặt chẽ định nghĩa trong Hiến pháp ontology V3.2

## 6. Tài liệu tham khảo

- [Graph Models](e:\tech\trm-os-branches\trm_api\graph_models\) - Các định nghĩa model cho Neo4j
- [API Endpoints](e:\tech\trm-os-branches\trm_api\api\v1\endpoints\) - Các API endpoint đã triển khai
- [Services](e:\tech\trm-os-branches\trm_api\services\) - Các service xử lý logic nghiệp vụ
- [Schemas](e:\tech\trm-os-branches\trm_api\schemas\) - Các schema Pydantic cho API
