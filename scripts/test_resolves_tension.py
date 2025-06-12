#!/usr/bin/env python3
"""
Script kiểm thử mối quan hệ RESOLVES_TENSION giữa Project và Tension.
Sử dụng API và repository trực tiếp để xác nhận tính đúng đắn của việc triển khai.
"""
import sys
import os
import uuid
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from neomodel import config as neomodel_config

# Tải biến môi trường từ file .env
env_path = Path(os.path.dirname(os.path.abspath(__file__))) / '..' / '.env'
load_dotenv(env_path)

# Cấu hình kết nối Neo4j từ biến môi trường
NEO4J_URI = os.getenv('NEO4J_URI', 'neo4j+s://66abf65c.databases.neo4j.io')
NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')

# Cấu hình neomodel để sử dụng kết nối Neo4j từ biến môi trường
# Neo4j Aura sử dụng bolt+s:// thay vì neo4j+s://
# Format: bolt+s://user:password@instance-id.databases.neo4j.io:7687
host = NEO4J_URI.split('://')[-1]  # Lấy phần host/instance-id
bolt_url = f"bolt+s://{NEO4J_USER}:{NEO4J_PASSWORD}@{host}:7687"
neomodel_config.DATABASE_URL = bolt_url

print(f"Đang kết nối đến Neo4j tại: {NEO4J_URI}")
print(f"URL kết nối neomodel: {bolt_url.replace(NEO4J_PASSWORD, '****')}")

# Thiết lập timeout dài hơn cho kết nối cloud
neomodel_config.MAX_CONNECTION_POOL_SIZE = 50
neomodel_config.CONNECTION_RETRY_COUNT = 3
neomodel_config.CONNECTION_TIMEOUT = 10  # seconds

# Thêm thư mục trm_api vào Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import các module cần thiết
from trm_api.repositories.project_repository import ProjectRepository
from trm_api.repositories.tension_repository import TensionRepository
from trm_api.models.project import ProjectCreate
from trm_api.models.tension import TensionCreate

# Khởi tạo repositories
project_repo = ProjectRepository()
tension_repo = TensionRepository()

def print_header(message):
    """In tiêu đề cho các bước kiểm thử."""
    print("\n" + "=" * 80)
    print(f" {message.upper()} ".center(80, "="))
    print("=" * 80)

def test_create_project_and_tension():
    """Tạo Project và Tension mới để kiểm thử."""
    print_header("Tạo project và tension mới")
    
    # Tạo project mới
    new_project_data = ProjectCreate(
        title=f"Test Project {uuid.uuid4().hex[:8]}",
        description="Dự án kiểm thử mối quan hệ RESOLVES_TENSION",
        status="active"
    )
    project = project_repo.create_project(new_project_data)
    print(f"Đã tạo Project: {project.title} (UID: {project.uid})", flush=True)
    
    # Tạo tension mới
    new_tension_data = TensionCreate(
        summary=f"Test Tension {uuid.uuid4().hex[:8]}",
        description="Tension kiểm thử mối quan hệ RESOLVES_TENSION",
        status="detected",
        project_id=project.uid,  # Liên kết với project vừa tạo
        priority="high"  # Thay thế severity bằng priority theo schema
    )
    tension = tension_repo.create_tension(new_tension_data)
    print(f"Đã tạo Tension: {tension.title} (UID: {tension.uid})", flush=True)
    
    return project, tension

def test_connect_project_to_tension(project, tension):
    """Kiểm thử việc tạo mối quan hệ RESOLVES_TENSION từ Project đến Tension."""
    print_header("Tạo mối quan hệ RESOLVES_TENSION")
    
    # Sử dụng repository của Tension
    result = tension_repo.connect_tension_to_project(
        tension_uid=tension.uid,
        project_uid=project.uid
    )
    
    if result:
        connected_tension, connected_project = result
        print(f"Đã kết nối thành công: Project '{connected_project.title}' đang giải quyết Tension '{connected_tension.title}'")
        return True
    else:
        print("Lỗi: Không thể tạo mối quan hệ RESOLVES_TENSION")
        return False

def test_query_related_items(project, tension):
    """Kiểm thử truy vấn các items đã liên kết qua mối quan hệ RESOLVES_TENSION."""
    print_header("Kiểm tra mối quan hệ đã được tạo")
    
    # 1. Truy vấn từ phía Tension - kiểm tra các Project đang giải quyết tension
    projects_resolving = tension_repo.get_projects_resolving_tension(tension.uid)
    print(f"Có {len(projects_resolving)} project đang giải quyết Tension '{tension.title}':", flush=True)
    for idx, proj in enumerate(projects_resolving, 1):
        print(f"  {idx}. {proj.title} (UID: {proj.uid})", flush=True)
    
    # 2. Truy vấn từ phía Project - kiểm tra các Tension đang được giải quyết bởi project
    tensions_resolved = project_repo.get_tensions_resolved_by_project(project.uid)
    print(f"\nDự án '{project.title}' đang giải quyết {len(tensions_resolved)} tension:", flush=True)
    for idx, tens in enumerate(tensions_resolved, 1):
        print(f"  {idx}. {tens.title} (UID: {tens.uid})", flush=True)
    
    # Kiểm tra xác thực mối quan hệ
    if project.uid in [p.uid for p in projects_resolving] and tension.uid in [t.uid for t in tensions_resolved]:
        print(f"✓ Mối quan hệ đã được thiết lập thành công và có thể truy vấn từ cả hai phía", flush=True)
        return True
    else:
        print("\n✗ Mối quan hệ không nhất quán giữa hai phía")
        return False

def test_remove_relationship(project, tension):
    """Kiểm thử việc xóa mối quan hệ RESOLVES_TENSION."""
    print_header("Xóa mối quan hệ RESOLVES_TENSION")
    
    success = project_repo.remove_tension_from_project(
        project_uid=project.uid,
        tension_uid=tension.uid
    )
    
    if success:
        print(f"Đã thiết lập mối quan hệ RESOLVES_TENSION từ Project '{project.title}' sang Tension '{tension.title}'", flush=True)
        
        # Xác nhận rằng mối quan hệ đã được xóa
        projects_resolving = tension_repo.get_projects_resolving_tension(tension.uid)
        tensions_resolved = project_repo.get_tensions_resolved_by_project(project.uid)
        
        if not projects_resolving and not tensions_resolved:
            print(f"✓ Mối quan hệ đã được xóa thành công", flush=True)
            return True
        else:
            print("✗ Mối quan hệ vẫn còn tồn tại sau khi xóa")
            return False
    else:
        print("Lỗi: Không thể xóa mối quan hệ RESOLVES_TENSION")
        return False

def cleanup(project, tension):
    """Dọn dẹp dữ liệu kiểm thử."""
    print_header("Dọn dẹp dữ liệu kiểm thử")
    
    # Xóa tension và project đã tạo để không làm rác database
    tension_deleted = tension_repo.delete_tension(tension.uid)
    project_deleted = project_repo.delete_project(project.uid)
    
    if tension_deleted and project_deleted:
        print(f"Đã xóa thành công Tension '{tension.title}' và Project '{project.title}'", flush=True)
        return True
    else:
        print(f"Lỗi khi xóa dữ liệu kiểm thử. Tension deleted: {tension_deleted}, Project deleted: {project_deleted}")
        return False

def main():
    """Hàm main thực hiện các bước kiểm thử."""
    print_header("BẮT ĐẦU KIỂM THỬ MỐI QUAN HỆ RESOLVES_TENSION")
    print(f"Thời gian bắt đầu: {datetime.now().strftime('%H:%M:%S %d/%m/%Y')}")
    
    try:
        # Bước 1: Tạo Project và Tension mới
        project, tension = test_create_project_and_tension()
        
        # Bước 2: Tạo mối quan hệ RESOLVES_TENSION
        if test_connect_project_to_tension(project, tension):
            # Bước 3: Truy vấn để kiểm tra mối quan hệ đã được tạo
            test_query_related_items(project, tension)
            
            # Bước 4: Xóa mối quan hệ
            test_remove_relationship(project, tension)
        
        # Bước 5: Dọn dẹp
        cleanup(project, tension)
        
        print_header("KIỂM THỬ HOÀN THÀNH")
        print(f"Thời gian kết thúc: {datetime.now().strftime('%H:%M:%S %d/%m/%Y')}")
        
    except Exception as e:
        print(f"\nLỖI TRONG QUÁ TRÌNH KIỂM THỬ: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
