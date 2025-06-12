#!/usr/bin/env python3
"""
Script kiểm thử API endpoints cho mối quan hệ RESOLVES_TENSION giữa Project và Tension.
Sử dụng HTTP requests trực tiếp để tương tác với API endpoints.
"""
import sys
import os
import uuid
import json
import requests
from datetime import datetime

# API Base URL - Điều chỉnh nếu API đang chạy trên cổng khác
API_BASE_URL = "http://localhost:8000/api/v1"

def print_header(message):
    """In tiêu đề cho các bước kiểm thử."""
    print("\n" + "=" * 80)
    print(f" {message.upper()} ".center(80, "="))
    print("=" * 80)

def create_project():
    """Tạo Project mới thông qua API."""
    print_header("Tạo project mới")
    
    project_data = {
        "title": f"Test Project {uuid.uuid4().hex[:8]}",
        "description": "Dự án kiểm thử mối quan hệ RESOLVES_TENSION từ API",
        "status": "active"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/projects/", json=project_data)
        response.raise_for_status()  # Raise exception cho HTTP error
        project = response.json()
        print(f"Đã tạo Project: {project['title']} (UID: {project['uid']})")
        return project
    except Exception as e:
        print(f"Lỗi khi tạo Project: {e}")
        if hasattr(e, 'response'):
            print(f"Response: {e.response.text}")
        return None

def create_tension(project_id):
    """Tạo Tension mới thông qua API."""
    print_header("Tạo tension mới")
    
    tension_data = {
        "title": f"Test Tension {uuid.uuid4().hex[:8]}",
        "description": "Tension kiểm thử mối quan hệ RESOLVES_TENSION từ API",
        "status": "detected",
        "project_id": project_id,
        "severity": 3
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/tensions/", json=tension_data)
        response.raise_for_status()
        tension = response.json()
        print(f"Đã tạo Tension: {tension['title']} (UID: {tension['uid']})")
        return tension
    except Exception as e:
        print(f"Lỗi khi tạo Tension: {e}")
        if hasattr(e, 'response'):
            print(f"Response: {e.response.text}")
        return None

def connect_project_to_tension(project_id, tension_id):
    """Tạo mối quan hệ RESOLVES_TENSION từ Project đến Tension."""
    print_header("Kết nối Project và Tension (RESOLVES_TENSION)")
    
    try:
        # Thiết lập mối quan hệ từ phía Project
        response = requests.post(
            f"{API_BASE_URL}/projects/{project_id}/resolves-tension/{tension_id}"
        )
        response.raise_for_status()
        relationship = response.json()
        print(f"Kết quả kết nối từ API:")
        print(json.dumps(relationship, indent=2))
        return True
    except Exception as e:
        print(f"Lỗi khi kết nối Project và Tension: {e}")
        if hasattr(e, 'response'):
            print(f"Response: {e.response.text}")
        return False

def get_tensions_resolved_by_project(project_id):
    """Lấy danh sách Tensions được giải quyết bởi Project."""
    print_header("Lấy danh sách Tensions được giải quyết bởi Project")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/projects/{project_id}/resolves-tensions"
        )
        response.raise_for_status()
        tensions = response.json()
        print(f"Project đang giải quyết {len(tensions)} tension(s):")
        for idx, tension in enumerate(tensions, 1):
            print(f"  {idx}. {tension['title']} (UID: {tension['tension_id']})")
        return tensions
    except Exception as e:
        print(f"Lỗi khi lấy danh sách Tensions được giải quyết: {e}")
        if hasattr(e, 'response'):
            print(f"Response: {e.response.text}")
        return []

def get_projects_resolving_tension(tension_id):
    """Lấy danh sách Projects đang giải quyết Tension."""
    print_header("Lấy danh sách Projects đang giải quyết Tension")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/tensions/{tension_id}/resolved-by"
        )
        response.raise_for_status()
        projects = response.json()
        print(f"Tension được giải quyết bởi {len(projects)} project(s):")
        for idx, project in enumerate(projects, 1):
            print(f"  {idx}. {project['title']} (UID: {project['project_id']})")
        return projects
    except Exception as e:
        print(f"Lỗi khi lấy danh sách Projects đang giải quyết: {e}")
        if hasattr(e, 'response'):
            print(f"Response: {e.response.text}")
        return []

def remove_relationship(project_id, tension_id):
    """Xóa mối quan hệ RESOLVES_TENSION giữa Project và Tension."""
    print_header("Xóa mối quan hệ RESOLVES_TENSION")
    
    try:
        response = requests.delete(
            f"{API_BASE_URL}/projects/{project_id}/resolves-tension/{tension_id}"
        )
        response.raise_for_status()
        print(f"Đã xóa thành công mối quan hệ RESOLVES_TENSION")
        return True
    except Exception as e:
        print(f"Lỗi khi xóa mối quan hệ: {e}")
        if hasattr(e, 'response'):
            print(f"Response: {e.response.text}")
        return False

def delete_tension(tension_id):
    """Xóa Tension đã tạo."""
    print_header("Xóa Tension")
    
    try:
        response = requests.delete(f"{API_BASE_URL}/tensions/{tension_id}")
        response.raise_for_status()
        print(f"Đã xóa Tension (UID: {tension_id})")
        return True
    except Exception as e:
        print(f"Lỗi khi xóa Tension: {e}")
        if hasattr(e, 'response'):
            print(f"Response: {e.response.text}")
        return False

def delete_project(project_id):
    """Xóa Project đã tạo."""
    print_header("Xóa Project")
    
    try:
        response = requests.delete(f"{API_BASE_URL}/projects/{project_id}")
        response.raise_for_status()
        print(f"Đã xóa Project (UID: {project_id})")
        return True
    except Exception as e:
        print(f"Lỗi khi xóa Project: {e}")
        if hasattr(e, 'response'):
            print(f"Response: {e.response.text}")
        return False

def cleanup(project_id, tension_id):
    """Dọn dẹp dữ liệu kiểm thử."""
    print_header("Dọn dẹp dữ liệu kiểm thử")
    
    # Xóa mối quan hệ trước
    remove_relationship(project_id, tension_id)
    
    # Xóa Tension và Project
    tension_deleted = delete_tension(tension_id)
    project_deleted = delete_project(project_id)
    
    if tension_deleted and project_deleted:
        print("Đã dọn dẹp xong dữ liệu kiểm thử")
        return True
    else:
        print(f"Có vấn đề khi dọn dẹp dữ liệu. Tension deleted: {tension_deleted}, Project deleted: {project_deleted}")
        return False

def main():
    """Hàm main thực hiện các bước kiểm thử."""
    print_header("BẮT ĐẦU KIỂM THỬ API MỐI QUAN HỆ RESOLVES_TENSION")
    print(f"Thời gian bắt đầu: {datetime.now().strftime('%H:%M:%S %d/%m/%Y')}")
    
    try:
        # Kiểm tra trạng thái API server
        print("Kiểm tra kết nối tới API server...")
        try:
            response = requests.get(f"{API_BASE_URL}/")
            print(f"API server sẵn sàng, status code: {response.status_code}")
        except Exception as e:
            print(f"Không thể kết nối tới API server: {e}")
            print("Đảm bảo TRM API server đang chạy trước khi thực hiện kiểm thử.")
            return
        
        # Bước 1: Tạo Project và Tension mới
        project = create_project()
        if not project:
            return
        
        tension = create_tension(project["uid"])
        if not tension:
            delete_project(project["uid"])
            return
        
        # Bước 2: Tạo mối quan hệ RESOLVES_TENSION
        if connect_project_to_tension(project["uid"], tension["uid"]):
            # Bước 3: Kiểm tra mối quan hệ
            tensions = get_tensions_resolved_by_project(project["uid"])
            projects = get_projects_resolving_tension(tension["uid"])
            
            # Xác minh mối quan hệ đã được tạo đúng
            tension_found = any(t["tension_id"] == tension["uid"] for t in tensions)
            project_found = any(p["project_id"] == project["uid"] for p in projects)
            
            if tension_found and project_found:
                print("\n✓ Mối quan hệ RESOLVES_TENSION đã được tạo thành công và có thể truy vấn từ cả hai phía")
            else:
                print("\n✗ Mối quan hệ không nhất quán giữa hai phía")
            
            # Bước 4: Xóa mối quan hệ
            remove_relationship(project["uid"], tension["uid"])
            
            # Kiểm tra lại sau khi xóa
            tensions_after = get_tensions_resolved_by_project(project["uid"])
            projects_after = get_projects_resolving_tension(tension["uid"])
            
            if not tensions_after and not projects_after:
                print("✓ Mối quan hệ đã được xóa thành công")
            else:
                print("✗ Mối quan hệ vẫn còn tồn tại sau khi xóa")
        
        # Bước 5: Dọn dẹp
        cleanup(project["uid"], tension["uid"])
        
        print_header("KIỂM THỬ HOÀN THÀNH")
        print(f"Thời gian kết thúc: {datetime.now().strftime('%H:%M:%S %d/%m/%Y')}")
        
    except Exception as e:
        print(f"\nLỖI TRONG QUÁ TRÌNH KIỂM THỬ: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
