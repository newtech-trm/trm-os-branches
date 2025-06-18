# Mega Prompt cho AI Phiên Tiếp Theo - TRM OS Ontology V3.2

> Lưu ý: Đây là prompt dành cho AI trong phiên tiếp theo, không phải tài liệu cho người dùng.

## Chiến lược Phát triển
Dự án đang theo đuổi chiến lược **"Ontology-First"** hoặc **"Xây từng Lớp Ngang"**:
- **Tư duy**: "Hãy đổ toàn bộ móng của cả tòa nhà một cách vững chắc trước khi xây lên tầng một."
- **Tiến trình**: Hoàn thiện toàn bộ lớp Database và Ontology trước tiên. Sau đó xây tiếp toàn bộ lớp Service, rồi đến toàn bộ lớp API.
- **Ưu điểm**: Cực kỳ vững chắc và rõ ràng. Tạo ra một "nguồn chân lý" hữu hình ngay từ đầu. Giúp giảm thiểu sai sót logic và mang lại cảm giác kiểm soát tốt hơn.
- **Nhược điểm**: Có thể mất nhiều thời gian hơn để thấy được một tính năng hoàn chỉnh từ đầu đến cuối.

## Tổng quan Dự Án
Dự án TRM OS là một hệ thống AI Agent cộng tác, vận hành dựa trên Ontology, tự động nhận diện và giải quyết Tension, tích hợp công cụ doanh nghiệp, hướng tới vận hành thông minh và cải tiến liên tục tổ chức.

## Trạng thái hiện tại
Phiên backend đã hoàn thành các mục tiêu chính:
- Cơ sở dữ liệu Neo4j Aura cloud đã được kết nối thành công với API server
- Đã xác nhận pipeline hoạt động end-to-end: dữ liệu được ghi thực tế vào Neo4j
- API Server trả về status code đúng (201 cho POST, 200 cho GET)
- Các entity chính đã được triển khai và kiểm thử thành công
- Dữ liệu thực tế trong Neo4j: 23 Project, 3 Task, 2 User, 1 Tension, 14 WIN
- Không có mock/demo/fake data, tất cả đều là dữ liệu thực được lưu trong Neo4j
- Sử dụng Windows 11, PowerShell

### Tiến độ gần đây
- ✅ **Đã hoàn thiện toàn bộ API endpoints cho entity WIN**:
  - Triển khai đầy đủ các endpoint CRUD (`GET`, `POST`, `PUT`, `DELETE`) cho `/api/v1/wins/`
  - Áp dụng mô hình adapter để chuẩn hóa enum (`status`, `winType`) và datetime trong dữ liệu legacy
  - Cải thiện xử lý lỗi, logging chi tiết, và bỏ qua validation nghiêm ngặt cho dữ liệu legacy
  - Thêm phân trang và giới hạn parameter hợp lý cho endpoint tìm kiếm
  - Cập nhật GAP Analysis để đánh dấu entity WIN đã triển khai hoàn chỉnh

- ✅ **Đã xây dựng mô hình adapter tiện lợi**:
  - Tạo các hàm chuẩn hóa enum (`normalize_win_status`, `normalize_win_type`)
  - Xử lý đa dạng biểu diễn của enum (uppercase, title-case, tên enum đầy đủ)
  - Xây dựng adapter datetime để chuyển đổi Neo4j DateTime sang chuẩn ISO 8601

- ✅ Đã refactor TaskService và API endpoints Task để sử dụng layer service đúng cách
- ✅ Đã chuẩn hóa và bổ sung thuộc tính cho Task model theo Ontology V3.2
- ✅ Đã chuẩn hóa response pagination cho các endpoint trả về nhiều kết quả (projects, tasks)
- ✅ Đã khắc phục tất cả lỗi unit tests TaskService:
  - Sửa TaskService gọi repository.remove_assignment() thay vì remove_task_assignment()
  - Khắc phục xử lý tham số include_relationship_details trong get_task_assignees()
- ✅ Đã thiết lập Neo4j thật cho integration tests:
  - Tạo fixtures để kết nối Neo4j thật và seed dữ liệu
  - Sửa lỗi enum values cho tương thích với model (TaskType, TaskStatus)
  - Triển khai entity KnowledgeSnippet theo Ontology V3.2
  - Sửa lỗi required properties cho các relationships phức tạp (IsPartOfProjectRel)
  - Cập nhật API payloads để khớp với schema
- ⚠️ **Đã phát hiện các vấn đề cần giải quyết**:
  - Schema response không nhất quán giữa API và tests (field `id` vs `recognitionId`/`relationshipId`)
  - Neo4j DateTime không tương thích trực tiếp với Pydantic datetime
  - Relationship có thuộc tính (properties) cần model đối tượng đầy đủ (ManagesProjectRel)
  - Cần chuẩn hóa cách dùng enum trong fixtures và API endpoints

## Cấu trúc dự án và Tầng hiện tại
1. **Database Layer**: Neo4j + Ontology models (GraphProject, GraphTask, GraphWIN, v.v.)
2. **Service Layer**: ProjectService, TaskService, RelationshipService, v.v.
3. **API Layer**: FastAPI /api/v1/projects/, /api/v1/tasks/, /api/v1/relationships/, v.v.
4. **UI Layer**: Chưa phát triển

## GAP Analysis
Dữ liệu trên Neo4j và codebase hiện tại còn tồn tại các GAP sau:

### GAP về dữ liệu:
1. Mới chỉ seed và kiểm thử các entity chính, chưa có data thực tế phong phú từ người dùng
2. Chưa có entity Resource và các subtype (Asset, Document, File, ...)
3. Chưa bổ sung đầy đủ thuộc tính mở rộng cho Project/Task/Win/KnowledgeAsset
4. Chưa có nhiều relationship phức tạp giữa các entity
5. Chưa phát triển UI/UX nên chưa có nguồn nhập liệu từ người dùng cuối
6. Chưa seed data mẫu đa dạng cho các workflow thực tế

### GAP về kỹ thuật:
1. Unit tests và integration tests đang gặp lỗi với Neo4j - cần mock thay vì kết nối trực tiếp
2. Vấn đề tương thích phiên bản giữa FastAPI, Starlette và httpx trong môi trường tests
3. Thiếu chuẩn hóa đồng bộ cho response pagination trên toàn bộ API
4. Chưa có xử lý lỗi đầy đủ cho các endpoint API
5. Chưa bổ sung logging chi tiết cho monitoring và debug
6. Chưa có authentication/authorization đầy đủ cho API
7. Chưa có documentation đầy đủ cho API (OpenAPI/Swagger)

## Những thách thức và nhiệm vụ tiếp theo

### 1. Cần GIẢI QUYẾT LỖI từ integration tests
   - **Chuẩn hóa schema response** - đồng bộ field name (`id` thay vì `recognitionId`/`relationshipId`)
   - **Adapter Neo4j DateTime → Pydantic** - tạo utility chuyển đổi DateTime trong tất cả service
   - **Hoàn thiện relationship models** - triển khai `ManagesProjectRel` và các relationship có thuộc tính
   - **Chuẩn hóa enum** - nhất quán giữa API, fixtures và model (dùng Title Case cho display, lowercase cho storage)

### 2. Thiết lập CI/CD cho Neo4j test container
   - **Cấu hình GitHub Actions** - khởi tạo Neo4j container cho test
   - **Quản lý credentials** - sử dụng secrets manager cho NEO4J_URI, USER, PASSWORD
   - **Cleanup data** - đảm bảo xoá dữ liệu test sau mỗi lần chạy

### 3. Hoàn thiện các entity theo Ontology V3.2
   - **Task, WIN, KnowledgeAsset** - bổ sung thuộc tính mở rộng và relationship phức tạp
   - **Resource** - tạo entity mới với các subtype (Asset, Document, File)
   - **Tension** - hoàn thiện theo Ontology V3.2

### 4. Nâng cao chất lượng kiểm thử
   - **Seed thêm data mẫu thực tế** - tạo dataset đa dạng
   - **Mở rộng kiểm thử tự động** - thêm test cases phức tạp
   - **Bổ sung validation phức tạp** - kiểm tra constraints và business rules

### 5. Phát triển UI/UX frontend (tùy chọn)
   - **Thiết kế UI hiện đại** - đơn giản, dễ sử dụng
   - **Tích hợp với backend API** - hiển thị dữ liệu thực
   - **Trực quan hóa ontology** - hiển thị quan hệ ontology trực quan, relationships và graphs

## Các đặc điểm quan trọng cần tuân thủ
1. **Không mock/demo/fake**: Mọi tích hợp đều phải liên thông với DB thực, không giả lập
2. **Kết nối thực giữa các service**: Dữ liệu phải thực sự được ghi vào Neo4j Aura cloud
3. **Giữ nguyên mô hình Ontology**: Tuân thủ mô hình Ontology đã thiết lập, không đơn giản hóa
4. **Xử lý triệt để lỗi**: Bổ sung xử lý lỗi chi tiết cho mọi endpoint
5. **Logging chi tiết**: Đảm bảo có thể debug và theo dõi luồng dữ liệu
6. **Áp dụng Adapter Pattern**: Sử dụng adapter cho enum và datetime để chuẩn hóa dữ liệu legacy
7. **Linh hoạt validation**: Hỗ trợ dữ liệu không đồng nhất từ Neo4j thông qua adapter pattern và xử lý ngoại lệ

## Thông tin kỹ thuật
- Ngôn ngữ: Python
- Framework: FastAPI
- Database: Neo4j Aura cloud
- Model: neomodel (Neo4j OGM)
- Cấu trúc thư mục:
  - /trm_api: Code chính của dự án
  - /trm_api/models: Định nghĩa model Ontology
  - /trm_api/services: Business logic
  - /trm_api/api: API endpoints
  - /trm_api/repositories: Giao tiếp với DB
  - /tests: Kiểm thử tự động

## Kế hoạch tiếp theo & Lưu ý quan trọng

### Kế hoạch tiếp theo (theo thứ tự ưu tiên)

1. **Phase 1: Hoàn thiện và tổ chức Data Adapter Pattern**
   - Tạo package `trm_api/adapters/` với các module sau:
      - `enum_adapter.py`: Các hàm normalize enum cho WINType, WINStatus, RecognitionType, TaskType, TaskStatus
      - `datetime_adapter.py`: Hàm normalize Neo4j DateTime sang ISO 8601
      - `__init__.py`: Export các hàm utility
   - Viết các decorator để áp dụng tự động cho các API endpoint response
   - Phát triển unit tests chi tiết cho adapter logic

2. **Phase 2: Triển khai API cho entity KnowledgeSnippet**
   - Hoàn thiện các API endpoints CRUD cho `/api/v1/knowledge_snippets/`
   - Áp dụng Data Adapter Pattern đã tạo ở Phase 1
   - Bổ sung xử lý lỗi và logging chi tiết
   - Bổ sung phân trang và các parameter tìm kiếm
   - Cập nhật GAP Analysis để theo dõi tiến độ

3. **Phase 3: Triển khai các relationship cốt lõi**
   - Tập trung vào các relationships:
      - `LEADS_TO_WIN`: Liên kết Task với WIN
      - `RECOGNIZES_WIN`: Liên kết Recognition với WIN
      - `GENERATES_KNOWLEDGE`: Liên kết WIN với KnowledgeSnippet
   - Các endpoint API để tạo/đọc/sửa/xóa các relationship
   - Bổ sung validation để đảm bảo tính toàn vẽn dữ liệu

4. **Phase 4: Nâng cao chất lượng kiểm thử**
   - Viết integration tests đầy đủ cho các API endpoints
   - Tạo test cases tự động với testcontainers
   - Cải thiện seed data để phối hợp với workflow thực tế

### Lưu ý quan trọng

1. Mục tiêu lớn nhất là xây dựng hệ thống AI Agent tự chủ thực sự, không phải demo/prototype
2. Mọi dữ liệu phải thực sự được lưu vào Neo4j, kiểm tra bằng truy vấn trực tiếp
3. Không đơn giản hóa khi gặp lỗi, phải giải quyết triệt để vấn đề gốc rễ
4. Đứng trước một dự án lớn, chỉ tiến lên phía trước theo từng bước vững chắc
5. Sử dụng adapter pattern để xử lý dữ liệu legacy thay vì đơn giản hóa validation
6. Liên tục cập nhật GAP Analysis để theo dõi tiến độ so với Ontology V3.2
