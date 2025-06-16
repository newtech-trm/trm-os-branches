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

## Cấu trúc dự án và Tầng hiện tại
1. **Database Layer**: Neo4j + Ontology models (GraphProject, GraphTask, GraphWIN, v.v.)
2. **Service Layer**: ProjectService, TaskService, RelationshipService, v.v.
3. **API Layer**: FastAPI /api/v1/projects/, /api/v1/tasks/, /api/v1/relationships/, v.v.
4. **UI Layer**: Chưa phát triển

## GAP Analysis
Dữ liệu trên Neo4j hiện tại còn "sơ sài" vì:
1. Mới chỉ seed và kiểm thử các entity chính, chưa có data thực tế phong phú từ người dùng
2. Chưa có entity Resource và các subtype (Asset, Document, File, ...)
3. Chưa bổ sung đầy đủ thuộc tính mở rộng cho Project/Task/Win/KnowledgeAsset
4. Chưa có nhiều relationship phức tạp giữa các entity
5. Chưa phát triển UI/UX nên chưa có nguồn nhập liệu từ người dùng cuối
6. Chưa seed data mẫu đa dạng cho các workflow thực tế

## Yêu cầu phát triển (ưu tiên theo thứ tự)
1. **Tối ưu hóa API và codebase**:
   - Tối ưu hiệu suất các endpoint
   - Tăng cường bảo mật và xử lý lỗi
   - Cải thiện logging và monitoring
   - Xem xét thêm pagination cho các endpoint trả về nhiều dữ liệu

2. **Bổ sung entity còn thiếu**:
   - Phát triển model Resource và các subtype theo Ontology
   - Tạo service và API endpoint cho Resource
   - Bổ sung thuộc tính mở rộng cho Project/Task/Win theo Ontology
   - Mở rộng các relationship phức tạp giữa entity

3. **Nâng cao chất lượng kiểm thử**:
   - Seed thêm data mẫu thực tế đa dạng
   - Mở rộng kiểm thử tự động
   - Bổ sung validation phức tạp hơn

4. **Phát triển UI/UX frontend (tùy chọn, hãy hỏi user)**:
   - Thiết kế UI hiện đại, đơn giản, dễ sử dụng
   - Tích hợp với backend API
   - Hiển thị quan hệ ontology trực quan

## Các đặc điểm quan trọng cần tuân thủ
1. **Không mock/demo/fake**: Mọi tích hợp đều phải liên thông với DB thực, không giả lập
2. **Kết nối thực giữa các service**: Dữ liệu phải thực sự được ghi vào Neo4j Aura cloud
3. **Giữ nguyên mô hình Ontology**: Tuân thủ mô hình Ontology đã thiết lập, không đơn giản hóa
4. **Xử lý triệt để lỗi**: Bổ sung xử lý lỗi chi tiết cho mọi endpoint
5. **Logging chi tiết**: Đảm bảo có thể debug và theo dõi luồng dữ liệu

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

## Lưu ý quan trọng
1. Mục tiêu lớn nhất là xây dựng hệ thống AI Agent tự chủ thực sự, không phải demo/prototype
2. Mọi dữ liệu phải thực sự được lưu vào Neo4j, kiểm tra bằng truy vấn trực tiếp
3. Không đơn giản hóa khi gặp lỗi, phải giải quyết triệt để vấn đề gốc rễ
4. Luôn tuân thủ schema Ontology, không thay đổi tùy tiện
5. Đảm bảo pipeline hoạt động trơn tru từ API đến DB
6. Tăng cường bảo mật và validation cho mọi endpoint

