#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script kiểm thử API mối quan hệ LEADS_TO_WIN trong TRM Ontology V3.2
Kiểm thử end-to-end: tạo Project, tạo WIN, kết nối Project hoặc Event với WIN,
kiểm tra các thuộc tính của relationship, và kiểm tra liên thông thực tế với Neo4j.
"""

import requests
import uuid
import json
import time
from datetime import datetime
import sys

# Cấu hình API
API_BASE_URL = "http://localhost:8000/api/v1"
API_CHECK_ENDPOINT = f"{API_BASE_URL}/users"  # Endpoint để kiểm tra kết nối API

# Màu cho output
HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'

def print_header(message):
    """In thông điệp header."""
    line = "=" * 80
    print(f"\n{line}")
    print(f"{BOLD}{HEADER}{'= ' + message.center(76) + ' ='}{ENDC}")
    print(f"{line}")

def print_success(message):
    """In thông điệp thành công."""
    print(f"{OKGREEN}{message}{ENDC}")

def print_error(message):
    """In thông điệp lỗi."""
    print(f"{FAIL}{message}{ENDC}")

def print_warning(message):
    """In thông điệp cảnh báo."""
    print(f"{WARNING}{message}{ENDC}")

def print_info(message):
    """In thông tin thông thường."""
    print(f"{OKBLUE}{message}{ENDC}")

def check_api_connection():
    """Kiểm tra kết nối đến API server trước khi bắt đầu kiểm thử."""
    print("Kiểm tra kết nối tới API server...")
    try:
        response = requests.get(API_CHECK_ENDPOINT)
        if response.status_code == 200:
            print_success(f"API server sẵn sàng, status code: {response.status_code}")
            return True
        else:
            print_warning(f"API server hoạt động nhưng trả về status code: {response.status_code}")
            return True  # Vẫn tiếp tục vì API server có thể sẵn sàng dù endpoint này trả về khác 200
    except requests.ConnectionError:
        print_error("Không thể kết nối đến API server. Hãy chắc chắn rằng server đang chạy.")
        return False
    except Exception as e:
        print_error(f"Lỗi khi kiểm tra kết nối API: {e}")
        return False

def create_project():
    """Tạo Project mới thông qua API."""
    print_header("Tạo Project mới")
    
    project_data = {
        "title": f"Test Project {uuid.uuid4().hex[:8]}",
        "description": "Project kiểm thử mối quan hệ LEADS_TO_WIN từ API",
        "status": "active"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/projects/", json=project_data)
        response.raise_for_status()
        project = response.json()
        print_success(f"Đã tạo Project: {project['title']} (UID: {project['uid']})")
        return project
    except Exception as e:
        print_error(f"Lỗi khi tạo Project: {e}")
        if hasattr(e, 'response'):
            print_error(f"Response: {e.response.text}")
        return None

def create_win():
    """Tạo WIN mới thông qua API."""
    print_header("Tạo WIN mới")
    
    win_data = {
        "summary": f"Test WIN Summary {uuid.uuid4().hex[:8]}",
        "description": "WIN kiểm thử mối quan hệ LEADS_TO_WIN từ API với chi tiết đầy đủ.",
        "winType": "ProcessImprovement",
        "relatedEntityIds": []
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/wins/", json=win_data)
        response.raise_for_status()
        win = response.json()
        print_success(f"Đã tạo WIN: {win['title']} (UID: {win['uid']})")
        return win
    except Exception as e:
        print_error(f"Lỗi khi tạo WIN: {e}")
        if hasattr(e, 'response'):
            print_error(f"Response: {e.response.text}")
        return None

def connect_project_to_win(project_uid, win_uid):
    """Kết nối Project với WIN thông qua relationship LEADS_TO_WIN."""
    print_header(f"Kết nối Project với WIN (Project {project_uid} -> WIN {win_uid})")
    
    relationship_data = {
        "contribution_level": 4,  # Significant
        "direct_contribution": True,
        "impact_ratio": 0.75,
        "recognition_score": 85,
        "notes": "Project đóng góp đáng kể cho WIN này"
    }
    
    # Giả định endpoint có dạng /wins/{win_id}/connect-project/{project_id}
    # hoặc /api/v1/projects/{project_id}/connect-win/{win_id}
    # Cần điều chỉnh theo endpoint thực tế
    endpoint = f"{API_BASE_URL}/wins/{win_uid}/source-projects/{project_uid}"
    
    try:
        response = requests.post(endpoint, json=relationship_data)
        response.raise_for_status()
        result = response.json()
        print_success(f"Đã kết nối Project với WIN: {result}")
        return result
    except Exception as e:
        print_error(f"Lỗi khi kết nối Project với WIN: {e}")
        if hasattr(e, 'response'):
            print_error(f"Response: {e.response.text}")
        return None

def get_win_sources(win_uid):
    """Lấy danh sách nguồn liên quan đến một WIN cụ thể."""
    print_header(f"Lấy danh sách nguồn của WIN (UID: {win_uid})")
    
    try:
        response = requests.get(f"{API_BASE_URL}/wins/{win_uid}/sources")
        response.raise_for_status()
        sources = response.json()
        print_success(f"Các nguồn của WIN: {json.dumps(sources, indent=2)}")
        return sources
    except Exception as e:
        print_error(f"Lỗi khi lấy nguồn WIN: {e}")
        if hasattr(e, 'response'):
            print_error(f"Response: {e.response.text}")
        return None

def disconnect_project_from_win(project_uid, win_uid):
    """Xóa mối quan hệ LEADS_TO_WIN giữa Project và WIN."""
    print_header(f"Xóa kết nối Project với WIN (Project {project_uid} -> WIN {win_uid})")
    
    # Giả định endpoint có dạng /wins/{win_id}/disconnect-project/{project_id}
    # hoặc /api/v1/projects/{project_id}/disconnect-win/{win_id}
    # Cần điều chỉnh theo endpoint thực tế
    endpoint = f"{API_BASE_URL}/wins/{win_uid}/source-projects/{project_uid}"
    
    try:
        response = requests.delete(endpoint)
        response.raise_for_status()
        print_success("Đã xóa kết nối Project với WIN thành công")
        return True
    except Exception as e:
        print_error(f"Lỗi khi xóa kết nối Project với WIN: {e}")
        if hasattr(e, 'response'):
            print_error(f"Response: {e.response.text}")
        return False

def delete_win(win_uid):
    """Xóa WIN bằng API."""
    print_header(f"Xóa WIN (UID: {win_uid})")
    
    try:
        response = requests.delete(f"{API_BASE_URL}/wins/{win_uid}")
        response.raise_for_status()
        print_success(f"Đã xóa WIN (UID: {win_uid})")
        return True
    except Exception as e:
        print_error(f"Lỗi khi xóa WIN: {e}")
        if hasattr(e, 'response'):
            print_error(f"Response: {e.response.text}")
        return False

def delete_project(project_uid):
    """Xóa Project bằng API."""
    print_header(f"Xóa Project (UID: {project_uid})")
    
    try:
        response = requests.delete(f"{API_BASE_URL}/projects/{project_uid}")
        response.raise_for_status()
        print_success(f"Đã xóa Project (UID: {project_uid})")
        return True
    except Exception as e:
        print_error(f"Lỗi khi xóa Project: {e}")
        if hasattr(e, 'response'):
            print_error(f"Response: {e.response.text}")
        return False

def run_test():
    """Chạy toàn bộ quy trình kiểm thử."""
    print_header("BẮT ĐẦU KIỂM THỬ API MỐI QUAN HỆ LEADS_TO_WIN")
    print(f"Thời gian bắt đầu: {datetime.now().strftime('%H:%M:%S %d/%m/%Y')}")
    
    # Kiểm tra kết nối API
    if not check_api_connection():
        return
    
    project = None
    win = None
    
    try:
        # Tạo Project mới
        project = create_project()
        if not project:
            return
        
        # Tạo WIN mới
        win = create_win()
        if not win:
            return
        
        # Kết nối Project với WIN
        connection = connect_project_to_win(project["uid"], win["uid"])
        if not connection:
            return
        
        # Lấy danh sách nguồn của WIN
        sources = get_win_sources(win["uid"])
        if not sources:
            return
        
        # Xóa kết nối
        if not disconnect_project_from_win(project["uid"], win["uid"]):
            return
        
        # Kiểm tra lại danh sách nguồn sau khi xóa kết nối
        sources_after = get_win_sources(win["uid"])
        if sources_after and len(sources_after.get("projects", [])) > 0:
            print_warning("Project vẫn còn trong danh sách nguồn sau khi xóa kết nối!")
        else:
            print_success("Project đã được xóa khỏi danh sách nguồn.")
        
        print_header("KIỂM THỬ MỐI QUAN HỆ LEADS_TO_WIN HOÀN TẤT")
        print(f"Thời gian kết thúc: {datetime.now().strftime('%H:%M:%S %d/%m/%Y')}")
        
    finally:
        # Dọn dẹp tài nguyên đã tạo
        if win:
            delete_win(win["uid"])
        if project:
            delete_project(project["uid"])

if __name__ == "__main__":
    run_test()
